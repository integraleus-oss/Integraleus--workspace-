I reviewed the diff plus the surrounding code in each scoped file. I could not execute either test suite — Bash is denied in this session — so every finding below is static analysis. Both suites should be run before merge.

## High

**H1 — `scripts/execution-supervisor.py:131`: unguarded `process.wait(timeout=5)` on the terminal-evidence kill path.**
The timeout path (`:133-137`) and the `KeyboardInterrupt` path (`:139-144`) both catch `subprocess.TimeoutExpired` and escalate to `SIGKILL`. This one does not. If the runner does not exit within 5s of `SIGTERM` — plausible, since it has an in-flight `openclaw agent` child — `TimeoutExpired` propagates out of `run()` (the enclosing `try` catches only `KeyboardInterrupt`), so `finalize` never runs, `notify_once` never runs, the state file stays `RUNNING` with no `finishedAt`, and the runner plus its child are left alive burning slices. This diff newly activates that branch by adding `BLOCKED` to `TERMINAL`/`EVIDENCE_MAP` (`:18-22`), and it is also the normal `SUCCEEDED` path whenever the supervisor polls in the window between the runner's `RESULT.json` rename and its exit.

**H2 — `projects/execution-supervisor-taskflow/index.js:172` and `:313`: `spawn()` with no `error` listener.**
Both detached spawns omit an `error` handler; contrast `:219-220` and `:231-233`, which have one. If `python3` is not on the Gateway's PATH, the `ChildProcess` emits `error` with no listener → uncaught exception in the Gateway. Short of that, `child.pid` is `undefined`, so `dispatchAdmission` still marks the admission `DISPATCHED` (`:173`), persists `supervisorPid: undefined` (`:176`), replies "PID undefined" (`:192`), and creates a TaskFlow with no supervisor and no state file — so the recovery service (`:256`) never finds it. Silent, permanent loss of an admitted task.

**H3 — `index.js:104-107` + `:141-142`: session-keyed admissions are never cleared.**
`admissionsBySession` is written on every admission and never deleted, not even when the supervisor reaches a terminal status. `admissionForContext` falls back to the session key whenever `ctx.runId` is absent — which is exactly the `before_dispatch` ingress path (the integration test's `ingressCtx`, `index.test.mjs:96-97`, has no `runId`). For any later turn in that session whose ctx lacks `runId`, `before_tool_call` (`:207-213`) blocks *every* tool with "already detached; foreground work is blocked" and `before_prompt_build` (`:201-205`) prepends a dispatch instruction for a task that already finished. Pre-existing, but this diff extends managed lifetime from one agent call to up to 12 slices, widening the window considerably.

## Medium

**M1 — `execution-supervisor.py:92-96`: the exactly-once outbox is not crash-safe.**
`notify_once` appends and fsyncs the outbox line (`:92-93`), *then* sets `notificationId` and persists state (`:94-96`). A crash in that window leaves `notificationId: None`, so `recover` (`:151`) calls `notify_once` again and appends a second line with the same deterministic id. `test_notification_exactly_once_after_recovery` (`test_execution_supervisor.py:38-41`) only covers the happy path, so it cannot catch this. Contradicts `README.md:8` ("exactly-once local delivery ledger") and Execution Truth Protocol rule 6 ("emit at most one notification"). Fix: record intent in state first, or scan the outbox for the event id before appending.

**M2 — `managed-agent-runner.mjs:43-49,64-65` vs `index.js:167,171`: runner and supervisor share one timeout, so the runner's terminal path is unreachable.**
`dispatchAdmission` passes `admission.timeoutSeconds` to both. The supervisor's clock starts first, so it always hits `TIMED_OUT` before the runner's `deadline`. Compounding it, the runner hands the *entire* remaining budget to each slice (`:48`, `:65`), so the last `openclaw agent` call is scheduled to run right up to the kill instant with zero margin to write `RESULT.json`. Net effect: the fallback at `:85-90` never fires in production, the final slice's work is discarded, and with no per-slice cap `MANAGED_MAX_SLICES=12` is decorative — slice 1 can consume the whole hour. Give the runner a strictly smaller budget and cap each slice at a fraction of the remainder.

**M3 — `managed-agent-runner.mjs:82`: validation errors are computed but never fed back.**
`checked.errors` reaches `previous` only when `outcome` is falsy. When the agent writes a *present but invalid* outcome — e.g. `SUCCEEDED` with `objectiveComplete: false` — it is silently reclassified as CONTINUE and slice N+1 is told "Your previous contract was: {…}" with no indication of what was rejected. The agent has no signal to correct and repeats itself until the budget is exhausted. `managed-agent-runner.test.mjs:57` encodes precisely this dead end (3 slices → FAILED) rather than a repair loop.

**M4 — `managed-agent-runner.mjs:62-63`: continuation slices drop the authoritative objective.**
Slice 1 sends `${task}${contractInstruction}`; slices 2+ send only the previous contract JSON. The objective survives only via the `openclaw` session store, which is subject to compaction over an hour-long run — while the contract text itself warns "do not silently narrow it." `task` is already in memory at `:39`; re-including it is free.

**M5 — `managed-agent-runner.mjs:50,85`: the outcome file is cleared per slice, `RESULT.json` never is.**
`RESULT.json` is also what the supervisor polls as `--terminal-evidence` (`index.js:166`) from its first loop iteration (`execution-supervisor.py:126`). Since `taskRoot` is deterministic in `ctx.runId` (`index.js:36-38`, `:114`), a leftover `RESULT.json` under a reused root makes the supervisor kill the fresh runner immediately and report the *previous* run's status. The end-of-loop guard at `:85` has the same defect — it can see a stale file and skip the fallback write. Unlink `args.result` at startup alongside the outcome.

**M6 — `managed-agent-runner.mjs:70-74`: a valid terminal outcome is discarded on any non-zero exit.**
The exit-code branch precedes the `terminalStatus` check. Per the CLI docs (`docs/tools/agent-send.md:97-100`), a Gateway timeout or closed connection fails the command *while the Gateway may still finish the accepted turn* — a non-zero exit that does not mean failure. `managed-agent-runner.test.mjs:62` pins the current behavior, so it is deliberate, but the same doc note implies the reverse hazard: after the runner reports CRASHED and the supervisor kills the process group, the Gateway-side turn is not in that group and keeps running unsupervised in `agent:main:managed:<id>`.

**M7 — `execution-supervisor.py:65-82,120,125`: the supervisor clobbers agent edits to `EVIDENCE.md`.**
`--evidence` and the managed task's evidence file are the same path (`index.js:161,165`). The supervisor read-modify-writes it on every poll tick (`:125`, default 0.25s) and `:75` truncates everything from the `## Execution Supervisor` marker onward — while the runner's contract instructs the agent to "Update task evidence as work progresses" (`managed-agent-runner.mjs:61`). Any agent write landing between the read (`:66`) and the `os.replace` (`:37`) is lost. Over a 12-slice run this is systematic evidence loss.

**M8 — `execution-supervisor.py:154` + `index.js:256-261`: PID-only liveness plus unbounded rescan retries stale `RUNNING` forever.**
`pid_alive` checks only `os.kill(pid, 0)` — no start-time or cmdline comparison. After a reboot or PID recycling, `recover` reports `RUNNING` indefinitely. The service filter at `:258` skips only states that are *both* terminal and delivered, so each stale state spawns a fresh `recover` process every `pollMs` forever, on top of a full recursive walk of `state/tasks` (`:66-80`) each tick. Violates Execution Truth Protocol rules 3 and 6.

**M9 — `index.js:224`: an empty delivery context is a permanent, un-backed-off failure loop.**
`dispatchAdmission` passes `JSON.stringify(deliveryContext ?? {})` (`:168`), and `deliveryFromDispatch` (`:146-156`) returns `{channel: undefined, to: ctx.conversationId}` for any non-Telegram-shaped session key. Line 224 then throws before the flow mutation at `:242-246`, so the TaskFlow is never finished or failed *and* the error re-logs every 5s indefinitely. The terminal result is never delivered by any path.

## Low

- **L1 — `managed-agent-runner.mjs:31`:** resolve on `close`, not `exit`; `exit` can fire with stdout/stderr still buffered, so `agent-output.json` (`:69`) may record truncated output.
- **L2 — `scripts/managed-outcome-contract.mjs` is untracked** (`??` in `git status`). The runner hard-imports it at `:6`; committing only the modified files ships a runner that dies at module load.
- **L3 — `managed-agent-runner.mjs:68-69`:** `agent-output.json` grows quadratically — every slice pushes full stdout/stderr into `attempts` and rewrites the whole array.
- **L4 — `managed-agent-runner.mjs:41,43`:** unvalidated `Number()`. A non-numeric `MANAGED_MAX_SLICES` makes the loop body never execute → instant `FAILED` with `slices: 0`; a non-numeric `--timeout` passes `"NaN"` to `openclaw --timeout`.
- **L5 — `index.js:55-60`:** `safePath` realpaths only the root. `resolve()` handles `..`, but an in-workspace symlink pointing outside passes the prefix check, and there's a TOCTOU gap before `spawn`. Owner-gated, so impact is limited.
- **L6 — `execution-supervisor.py:18`:** `STALE` is listed as a terminal/paused state in the Execution Truth Protocol but is absent from `TERMINAL` and `EVIDENCE_MAP`, so heartbeat expiry has no encoding. This diff closed the `BLOCKED` half of that gap.
- **L7 —** atomicity asymmetry: `execution-supervisor.py:30-39` fsyncs before `os.replace`; `managed-agent-runner.mjs:14-18` does not, and leaks the temp file if `rename` throws. Neither fsyncs the parent directory.
- **L8 —** `spawn("python3", …)` (`index.js:172,219,231,313`) resolves via PATH, unlike `process.execPath` for the runner (`:169`).

## Test quality

- **`index.test.mjs` was not updated at all.** The dispatch argv gained `--outcome` (`index.js:170`) and `--thinking` (`:171`), and config gained `managedAgentThinkingLevel` — but the fake runner (`index.test.mjs:19-22`) ignores argv and nothing asserts either flag. The single new config contract in this diff has zero coverage.
- **Time budgeting is untested.** The `remainingSeconds <= 1` break (`managed-agent-runner.mjs:48-49`) and the resulting `slices: 0` fallback are unexercised; the fake `openclaw` ignores `--timeout` entirely.
- **No stale-file scenario.** Nothing pre-creates `RESULT.json`/`MANAGED_OUTCOME.json` to prove the runner clears them (M5) — notable given the unlink at `:50` is deliberate new behavior.
- **No crash-window test for the outbox** (M1).
- **No end-to-end BLOCKED test through the plugin** — covered in Python (`test_execution_supervisor.py:35-37`) and in the runner (`managed-agent-runner.test.mjs:61`), but not that `reconcileState` routes it to `runtime.fail` with the right `blockedSummary` (`index.js:245`).
- **Hardcoded absolute paths** at `managed-agent-runner.test.mjs:42` and `index.test.mjs:46` tie the suite to one machine.
- `runProcess` switched to `stdio: "inherit"` (`managed-agent-runner.test.mjs:9`), so 8 scenarios now dump full child output into logs.

## What's solid

`managed-outcome-contract.mjs` is pure and independently unit-tested (`managed-agent-runner.test.mjs:22-25`). The CONTINUE→SUCCEEDED multi-slice path and the invalid-blocker→CONTINUE path are covered with attempt-count assertions. `BLOCKED` was added to `TERMINAL` and `EVIDENCE_MAP` on both the Python and JS sides in the same change, aligning with Execution Truth Protocol rule 6. The version bump is consistent across `package.json`, `package-lock.json`, and `openclaw.plugin.json`, and the JSON config schema mirrors the TypeBox schema exactly for the new field. `--thinking` is a real `openclaw agent` flag. The README documents the new completion contract.

**FAIL** — blocking on H1, H2, H3, and M1/M2/M5.
