Bash is denied in this session, so this is a static review only (I could not execute the test suites).

## Scope confirmed

I read all six files. `scripts/managed-outcome-contract.mjs` (new, untracked) is a hard dependency of the runner's `terminalStatus()`/`validateManagedOutcome()` decision but was excluded from scope — the "exit 0 is never SUCCEEDED" chain is only verified up to that boundary.

---

## What holds up

- **Exit code 0 alone is never SUCCEEDED** (`execution-supervisor.py:207-210`): with no validated terminal evidence, exit 0 → `FAILED`; `SUCCEEDED` + nonzero exit → `CRASHED`. `run` also forces `requireValidatedTerminal = bool(terminal_evidence)` (`:184`), so the flag can't be dropped to weaken validation at launch. Recovery is symmetric and conservative (`:273` — a missing `exitCode` demotes `SUCCEEDED` to `CRASHED`).
- **Capability handoff** (`execution-supervisor.py:191-197`, `managed-agent-runner.mjs:120-129`): nonce goes over an anonymous pipe, write end closed pre-spawn, only the SHA-256 is persisted; the runner reads once, `closeSync`s the fd, deletes the var from `process.env` *and* from the derived `childEnv` before any agent spawn. No nonce appears in any prompt, `agent-output.json`, plan, or review file. `RESULT.json` (which does hold the plaintext nonce) is unlinked at start and only written after the last child agent has exited.
- **Terminal evidence read after exit** (`:205-209`): only inside the `poll() is not None` branch; the 5 s heartbeat never reads `RESULT.json`.
- **Arbitrary-command start removed**: no `execution_supervisor_start`; `execution_supervisor_dispatch` takes `Type.Object({})` with `additionalProperties: false` and derives the entire argv internally (`index.js:208-215`). Confirmed.
- **High thinking**: default `"high"` in both schemas; planner, plan-reviewer and both terminal reviewers are hardcoded `"high"`.

---

## CRITICAL

**1. The integrity anchor is stored in a file the supervised model can rewrite — validated `SUCCEEDED` is forgeable.**
`scripts/execution-supervisor.py:186` persists `terminalNonceHash` into `execution-supervisor-state.json`, and `recover` validates `RESULT.json` against that hash read back from the same file (`:249-252`). That state file lives at `state/tasks/managed-admission/<id>/execution-supervisor-state.json` (`index.js:141`) — inside the workspace, in the directory the managed agent is explicitly told to write ("Update task evidence as work progresses", `managed-agent-runner.mjs:188`), and its path is printed into `EVIDENCE.md` (`:129`). The managed slices are plain `openclaw agent --agent main` processes with full bash/file tools and no sandbox.

Failure scenario: a slice writes `RESULT.json` = `{"terminalStatus":"SUCCEEDED","contractValidated":true,"terminalNonce":"X","exitCode":0}` **and** patches the state file with `status:"SUCCEEDED"`, `terminalNonceHash: sha256("X")`. `terminal_from_evidence` and `terminal_exit_code` both validate, `recover` takes the `else` at `:256-257`, and the owner is notified `SUCCEEDED`. The nonce defends only against an attacker who can write `RESULT.json` but not the state file — nothing enforces that split. `validate_recovery_state` (`:65-76`) checks filenames only, and the plugin's trust check (`index.js:276-277`) cross-checks against `admission.json`, which sits in the same writable directory.

**2. `finalize()` lets a disk-authored terminal status override the supervisor's own observation.**
`scripts/execution-supervisor.py:162-163`: after the child exits, `finalize` re-reads the state file and returns immediately if `persisted["status"] in TERMINAL` — `return 0 if persisted["status"] == "SUCCEEDED" else 4` — without consulting the freshly computed `observed`/`code` it was just handed at `:209-210`. This directly contradicts the invariant asserted in the comment at `:221-222` ("No other disk-authored terminal status is authoritative while this supervisor still owns and observes the child"). Failure scenario: the child writes `status:"SUCCEEDED"` into the state file inside the ≤5 s window between heartbeats and exits; the supervisor exits 0 and leaves the forged record as the durable truth, never calling `update_evidence`/`notify_once` with the real outcome. The heartbeat's own guard (`:217`) only special-cases `TIMED_OUT`, so it does not close this.

---

## HIGH

**3. Reconciliation discards the recorded originating delivery context.**
`projects/execution-supervisor-taskflow/index.js:281-282` unconditionally overwrites `state.deliveryContext` — the value the supervisor durably persisted at dispatch via `--delivery-json` (`execution-supervisor.py:187`) — with one re-derived from `sessionKey` alone. Two concrete failures:
- `accountId` is always lost: `deliveryFromDispatch({}, {sessionKey})` has no `ctx.accountId`, so `sendText` is called with `accountId: undefined` (`:299-302`) even though the dispatch-time context carried it. Multi-account sends go out on the wrong account.
- Any session key that doesn't match `:group:N:topic:M$` or `:direct:N$` — e.g. the `agent:main:main` private case the test itself exercises at `index.test.mjs:139` — yields `{channel: undefined, to: undefined}`, falls back to `config.delivery`, and if that is unset throws `missing originating delivery context` (`:296`) on **every** poll tick. The run is terminal, `notificationDelivered` stays false forever, `ack` never runs, and the owner is never notified. The correct value was on disk and was thrown away one line earlier.

**4. Stale dispatch-lock reclaim can start a second supervisor for a live run.**
`index.js:186-200`: the lock is taken *before* spawn (`:186`), but `status: "DISPATCHED"` is only written to `admission.json` *after* spawn succeeds (`:218-221`). If the plugin process dies in that window, the supervisor and its runner are alive while `admission.json` still reads `ADMITTED` and the lock file is orphaned. After 30 s, `:189-192` unlinks the lock and recurses, dispatching a **second** supervisor with the same `--state`, `--outbox`, `--evidence` and `--terminal-evidence` paths. The two instances have different `runId`s and different nonces, so the outbox `id` dedup at `:137/:142-148` cannot collapse them: two `exec-*` events, two owner notifications, two runners racing on one `RESULT.json`. The mtime heuristic cannot distinguish "crashed before spawn" from "spawned and still running"; nothing checks for a live supervisor PID before reclaiming.

**5. `admission.json` — the file that gates reconciliation trust — is written non-atomically.**
`index.js:221` and `index.js:310` use a bare `writeFile` overwrite, unlike every other durable write in this system (`execution-supervisor.py:33-46` temp+fsync+rename; `managed-agent-runner.mjs:16-20` temp+rename). A crash or full disk mid-write leaves truncated JSON; `reconcileState`'s `.catch(() => null)` at `:275` then makes `admission` null and `:277` throws `untrusted supervisor state` on every tick, permanently. There is no repair path — the terminal state can never be reconciled into the flow and the notification is never delivered.

---

## MEDIUM (noting, not blocking)

- `index.js:239` — the ingress path passes `messages: []`, so `CONTEXT.json` is always empty for owner-originated dispatches, while the task packet (`:47`) tells the agent that "recent source-session context is stored in" that file. The primary path for large objectives silently loses all conversation context.
- `index.js:364` vs `:141` — `safePath` returns a `realpath`, but `admission.statePath` is a non-canonicalized `resolve()`. If any component of `workspaceRoot` is a symlink, the `execution_supervisor_recover` tool fails the `:276` equality check every time.
- `requiresManagedExecution` (`index.js:32-37`) keys on a closed set of imperative verb forms. Large Russian objectives phrased with infinitives ("нужно реализовать…", "требуется выполнить…") or nominalizations bypass admission entirely, regardless of length.
- `execution-supervisor.py:293` — `--require-validated-terminal` is accepted but never read (`:184` derives it from `--terminal-evidence`). Dead flag that reads as a safety control.
- `execution-supervisor.py:165` — `return int(state.get("exitCode") or 0)` can return a negative signal code (e.g. `-15`), which `SystemExit` maps to a nonsense shell status.

---

## Verdict

**FAIL** — two CRITICAL execution-truth defects (forgeable validated `SUCCEEDED` via the model-writable state file; `finalize` deferring to disk-authored terminal status) and three HIGH activation/delivery defects (delivery context discarded on reconcile, double-dispatch on stale lock reclaim, non-atomic trust-gate write). The exit-code, capability-handoff, read-after-exit and no-arbitrary-command properties do hold; the failures are in what the state file is trusted to say and in owner-delivery reconciliation.
