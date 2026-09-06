I could not execute the test suites — Bash denied `python3` and `node` invocations in this session. All findings below are from static analysis of the code and the on-disk state artifacts; I've flagged where that limits confidence.

---

# Standards Review R6 — Managed Program Orchestration

## What the change closed

R5's nonce-in-state-file leak is genuinely fixed: the nonce now travels supervisor→runner over an anonymous pipe (`execution-supervisor.py:157-160`), only its SHA-256 is persisted (`:150`), the runner closes the fd before spawning any child (`managed-agent-runner.mjs:88`), and `MANAGED_TERMINAL_FD` is stripped from child env (`:115`). Command-evidence was deleted entirely, closing C2/H1's exfiltration and `/bin/true` oracle. Strict mode is now the default with an explicit `--allow-exit-code-terminal` escape (`:146-148`), closing M1. `createAdmission` is idempotent (`index.js:115-123`), closing M2. `ptrace_scope` is `1` on this host, so the agent cannot read the nonce out of the runner's memory.

---

## CRITICAL

### C1 — The terminal nonce is still handed to the managed agent, on disk, in its own working directory

The nonce moved from `execution-supervisor-state.json` to `RESULT.json`, but `RESULT.json` sits in the same agent-writable `taskRoot`.

- `managed-agent-runner.mjs:154` and `:164` both write `terminalNonce` verbatim into `args.result`.
- `args.result` is `<taskRoot>/RESULT.json` (`index.js:133`, `:179`), the same directory as `MANAGED_OUTCOME.json` (`:134`), whose absolute path is given to the agent in the contract instruction (`managed-agent-runner.mjs:103-104`).
- `execution-supervisor.py:138-141` persists `command` (full runner argv including `--result <path>`), `terminalEvidencePath`, and `pid` into `<taskRoot>/execution-supervisor-state.json`. Confirmed on disk: `state/tasks/managed-admission/d188cd04-.../execution-supervisor-state.json:10-27`.
- The managed worker has unrestricted tools: `index.js:113` returns `null` for `agent:main:managed:*`, so `before_tool_call` (`:218-224`) never engages.

Failure scenario (no race required):
1. Agent reads `<taskRoot>/execution-supervisor-state.json` → `terminalEvidencePath`, `pid` (the runner).
2. `ps -o ppid= -p <pid>` → the supervisor. `kill -9` it. `PR_SET_DUMPABLE` (`:154`) blocks memory inspection, not signals.
3. The runner finishes normally and writes `RESULT.json` — containing a valid `terminalNonce` on **both** the success path (`:154`) and the failure path (`:164`).
4. Agent rewrites `RESULT.json` as `{"terminalStatus":"SUCCEEDED","contractValidated":true,"terminalNonce":"<the real one>"}`.
5. The plugin's recovery tick (`index.js:271-276`, `pollMs: 2000` in the live config) runs `recover`; `execution-supervisor.py:195-197` validates the nonce hash, accepts, and `finalize` persists `SUCCEEDED` + notifies the owner.

Without step 2 the same forgery works against the 250 ms poll window (`:179`) via a background poller the agent leaves behind — see H1, which makes that survivable.

This reproduces R5's C1 exactly: zero packages, zero gates, no evidence, no independent review. The nonce's disclosure was deferred in time, not eliminated. The architectural note in R5 stands — a same-uid secret written into the agent's own directory cannot be the authorization mechanism for terminal state. The fix shape is to return the terminal envelope over a supervisor-held write-fd (the agent can neither open nor forge it), or a separate uid.

---

## HIGH

### H1 — Slice children are spawned detached and are never reaped; supervisor kills miss them

`managed-agent-runner.mjs:27` spawns each `openclaw agent` slice with `detached: true`, i.e. its own process group. The only kill is the per-slice timeout timer (`:34`).

- On supervisor timeout or interrupt, `os.killpg(process.pid, ...)` (`execution-supervisor.py:175`, `:182`) kills the runner's group only. Every detached slice child survives.
- When the runner exits normally (`:157`, `:168`) it makes no attempt to kill outstanding descendants.

Consequence: after the supervisor has reported `TIMED_OUT`/`INTERRUPTED`/`FAILED` and notified the owner, a fully-privileged agent process is still running, still writing `MANAGED_OUTCOME.json`, and still able to read `RESULT.json`. This is what makes C1 exploitable without winning a tight race, and it corrupts any subsequent run reusing the directory.

### H2 — A transient slice-1 failure permanently dooms the run

`managed-agent-runner.mjs:127` locks the baseline only when `slice === 1`. `:131` then appends `"locked plan is missing"` to every slice `> 1` when `baseline` is null.

Slice 1 is reached exactly once. If it produces an invalid outcome — or if the `openclaw` process merely exits non-zero, which `:134-137` explicitly treats as retryable and `continue`s from — the plan can never be locked, so slices 2…12 each accumulate a fatal validation error and the run burns its full budget before writing `FAILED` at `:164`. R5 filed this as L1; the retry path at `:134-137` makes it materially more reachable than "invalid model output", because a single network blip on the first slice is enough.

---

## MEDIUM

### M1 — `evidenceErrors` has a declared time budget that is never enforced

`managed-agent-runner.mjs:50-51` declares `budgetMs = 120000` and computes `evidenceStarted`; neither is read again. The loop at `:58-67` hashes every declared evidence file with `readFile` (whole file into memory) with no cap on count or size. A terminal candidate declaring many or large files consumes the 130 s review reserve (`:113`) and can push the runner past the supervisor deadline. Half-finished implementation sitting directly on the "timeout budgeting" axis.

### M2 — Evidence paths are unconfined

`managed-agent-runner.mjs:61` resolves relative paths against `process.cwd()` and accepts any absolute path with no workspace-root check — inconsistent with the plugin's own `safePath` policy (`index.js:56-60`). An agent can cite any pre-existing file on the host (`/etc/os-release`, another task's artifacts) as gate evidence and pass hash verification, since it authors both the claim and the hash.

### M3 — `notify_once` is called outside the finalize lock; outbox exactly-once is not multi-process safe

`execution-supervisor.py:194` calls `notify_once` from `recover()` with no `flock`, while `finalize` (`:121-129`) holds one. The scan-then-append in `:104-112` is not atomic across processes: two concurrent recoveries (plugin tick + manual CLI, or two gateway processes) can both find no matching `id` and both append. `acknowledge` (`:204-208`) likewise does an unlocked read-modify-write of `state.json` that can clobber a concurrent `recover` write (`:199`). README:7-8 stakes the exactly-once claim on this ledger.

### M4 — Owner notification is send-then-ack, i.e. at-least-once

`index.js:238-244`: `sendText` is awaited, then a separate `python3 … ack` subprocess is spawned. If the ack fails or the gateway dies in between, `notificationDelivered` stays false and the next tick re-sends. Exactly-once then rests entirely on the outbound adapter honoring `deliveryQueueId`. R5's L4, unchanged.

### M5 — `recover` trusts a bare PID

`execution-supervisor.py:198` uses `pid_alive(int(state["pid"]))` with no start-time or identity check. After a crash with PID reuse, an unrelated process makes `recover` report `RUNNING` indefinitely; the plugin's tick (`index.js:271-276`) then never finalizes and the owner is never notified — a never-once failure on the same axis as M3/M4.

### M6 — The schema-minimum timeout yields unusable slices

`index.js:181` gives the runner `timeoutSeconds - 150`; `managed-agent-runner.mjs:113` reserves a further fixed 130 s per slice. At the schema minimum `managedAgentTimeoutSeconds: 300` (`index.js:20`, `openclaw.plugin.json:19` — raised from 60 in this change) the runner budget is 150 s, so slice 1 gets ~20 s, slice 2 ~15 s, and the mandatory independent review floors at 15 s (`:146`). Since `:126` forces slice 1 to `CONTINUE`, no real objective can terminate. The lower portion of the documented config range is non-functional. Related: `:146` allows the review up to 300 s against a 130 s reserve, so the runner can overrun its own deadline (absorbed today only by the 150 s supervisor cushion).

---

## LOW

- **L1** — `execution-supervisor.py:174-178`: the timeout path finalizes `TIMED_OUT` without re-reading terminal evidence. Now that the nonce makes forgery infeasible, the mid-run evidence check removed in this diff was over-broadly deleted: a run that wrote a valid envelope moments before the deadline is reported as a timeout.
- **L2** — `execution-supervisor.py:125` returns `4` on the already-terminal path where `:130` returns `124` for `TIMED_OUT`; `:127` returns the *child's* exit code, mixing code spaces with the supervisor's 0/4/124 contract.
- **L3** — `managed-agent-runner.mjs:34-35`: `child.on("error", reject)` leaves the timer pending and the rejection is unhandled at `:116`, so a spawn failure kills the runner before the `:163-167` fallback can write a terminal envelope. Contained (supervisor sees exit≠0 + no evidence → `FAILED`), but the runner's "always write an envelope" invariant is broken.
- **L4** — `managed-agent-runner.mjs:16-20`: `atomicJson` does not `fsync` the file or the parent directory before/after `rename`, unlike the Python side (`execution-supervisor.py:39`). `RESULT.json` is the terminal proof. Fails closed on a torn read, but "atomicity" is an explicit focus area.
- **L5** — `index.js:221-222`: the `admission.status === "DISPATCHED"` ternary branch is unreachable; `:220` already returned. R5's L3, unchanged.
- **L6** — `index.js:56-60`: `safePath` resolves but does not `realpath` the *target*, so a symlink inside the workspace pointing outside passes. The reconciled state file's own `evidencePath`/`outboxPath` are then used unvalidated for writes (`:232-245`). Owner-gated, so low.
- **L7** — `index.js:271` walks `state/tasks` recursively every `pollMs` (2000 ms live), and `execution-supervisor.py:167` rewrites `state.json` with an fsync every 250 ms for the entire run (up to 24 h). Both are avoidable steady-state I/O.
- **L8** — Undocumented breaking config change: `authorizedSessionPrefixes` was removed from a schema with `additionalProperties: false` (`index.js:29`, `openclaw.plugin.json:14`), and the `managedAgentTimeoutSeconds` minimum went 60→300. Any config still setting either now fails validation and the plugin will not load. README:39-45 documents the tool removal and thinking defaults but not these. The live config (`~/.openclaw/openclaw.json:480-487`) sets only `pollMs` and `authorizedSenderIds`, so nothing breaks today.
- **L9** — `managed-agent-runner.mjs:5-6` imports `node:crypto` twice. `:60-66` re-validates via `terminalStatus()` (`managed-outcome-contract.mjs:61`) after `:121` already did. `:10-13` `argumentsMap` assumes strict flag/value pairing and silently misparses any bare flag.

---

## Test quality

The two newest and most security-relevant validators have **zero coverage**:

- `planErrors` (`managed-agent-runner.mjs:39-48`) — no test removes or renames a package/gate after slice 1. The plan-lock guarantee is untested.
- `evidenceErrors` (`:50-69`) — the fake agent (`managed-agent-runner.test.mjs:42-52`) always writes a real path with a real hash. Missing file, empty file, hash mismatch, and unsupported `kind` are all untested.
- The independent reviewer always returns `PASS` (`test.mjs:45`). The reject-and-continue path (`managed-agent-runner.mjs:150-152`) is never exercised.
- H2's failure mode is not covered: `test.mjs:75` uses a *permanently* failing exit code, not a transient slice-1 failure followed by success.
- `index.test.mjs:120-121` asserts `sessions_spawn` is unblocked, but the admission is already `DISPATCHED` at that point, so the assertion is vacuous — it duplicates `:105-106` rather than testing what its placement implies.
- `test_execution_supervisor.py` has no coverage for `recover` against a live vs. reused PID (M5), no concurrent-`notify_once` test (M3), and `test_delivery_context_is_persisted` (`:68-77`) exercises only the legacy `--allow-exit-code-terminal` path.

Positive: `test_forged_terminal_is_not_accepted_while_child_is_running` (`:38-41`), `test_strict_stale_terminal_is_removed_before_launch` (`:42-44`), and `test_outbox_deduplicates_after_state_intent_loss` (`:57-62`) are well-targeted regression tests for real prior defects, and `index.test.mjs:129-133` is a correct exactly-once assertion across a service restart.

---

## Requirement status

| Requirement | Status |
|---|---|
| Exit code 0 alone cannot prove completion | ✅ strict is now the default (`:146-148`) |
| Terminal envelope unforgeable by the agent | ❌ C1 |
| Objective decomposed into locked packages/gates | ⚠️ locked (`:127-130`) but H2 makes the lock a single point of failure |
| Partial work continues in bounded slices | ⚠️ M6 at the low end of the config range |
| SUCCEEDED requires all PASSED with evidence | ⚠️ structural only; agent authors file + hash (M2) |
| BLOCKED requires evidenced external dependency | ⚠️ `blocker.external` still self-asserted (`managed-outcome-contract.mjs:49`) — R5's H2, unchanged |
| Terminal state reconciled and delivered once | ⚠️ M3, M4, M5 |
| Process lifetime bounded by the supervisor | ❌ H1 |

---

## FAIL

C1 is disqualifying and is the same defect R5 rejected — relocated from `execution-supervisor-state.json` to `RESULT.json`, not closed. The managed agent runs same-uid with unrestricted tools in the directory the nonce lands in, knows the exact target path from its own state file, and can kill the supervisor to convert the 250 ms race into an unbounded window; the recovery path then accepts the forged envelope. H1 supplies the surviving process that makes this practical even without killing the supervisor.

Minimum to re-review: (1) never write the nonce to a path the agent can read — return the terminal envelope over a supervisor-held fd, or run the agent under a separate uid; (2) kill the slice process group when the runner exits or is terminated (`managed-agent-runner.mjs:27`, `execution-supervisor.py:175/182`); (3) allow the plan to lock on the first *valid* outcome rather than only `slice === 1` (`:127`, `:131`); (4) enforce the declared `budgetMs` and confine evidence paths.

I did not edit any files, and I was unable to run the test suites in this session.
