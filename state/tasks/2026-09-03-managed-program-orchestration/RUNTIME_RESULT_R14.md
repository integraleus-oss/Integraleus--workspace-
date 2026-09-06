Test execution was denied by the sandbox, so this is static analysis only (no files edited, no prior review files read).

## HIGH defects

**1. `recover()` can never return SUCCEEDED — validated success is reported as CRASHED**
`scripts/execution-supervisor.py:250`

```python
if observed == "SUCCEEDED" and state.get("exitCode") != 0: observed = "CRASHED"
```
`exitCode` is initialized to `None` (`:165`) and is only ever assigned inside `finalize()` (`:155`), which simultaneously sets a terminal status. `recover()` returns early for terminal states (`:232`), so every state reaching `:250` has `exitCode is None` → `None != 0` → the SUCCEEDED branch is unreachable. Failure scenario: the supervisor is killed (host restart) while the detached runner keeps working; the runner exits after writing a nonce-validated `RESULT.json` with `terminalStatus: SUCCEEDED`; the recovery service runs `recover`, and the task is finalized `CRASHED`, the TaskFlow is `fail()`ed (`projects/execution-supervisor-taskflow/index.js:275`), and the owner is notified of a failure that did not happen. Crash recovery — the entire purpose of this path — cannot produce a truthful success.

**2. Runner liveness is keyed on a hardcoded basename, so a configured runner path gets healthy tasks killed**
`scripts/execution-supervisor.py:84`, with `projects/execution-supervisor-taskflow/index.js:193`

```python
return "managed-agent-runner.mjs" in cmdline and str(...RESULT.json) in cmdline
```
`managedRunnerPath` is a first-class config option (`index.js:193`, `openclaw.plugin.json:18`) with no constraint on its filename. If it is set to anything whose path doesn't contain the literal `managed-agent-runner.mjs`, `managed_runner_alive()` returns `False` for a perfectly healthy runner. The recovery service reconciles *every* non-delivered state every 5 s (`index.js:306-315`), including `RUNNING` ones, so within ~5 s of dispatch: `recover` falls through to `:248-251`, finds no `RESULT.json` yet, and finalizes `CRASHED`; then the live supervisor's heartbeat sees the persisted terminal status and SIGTERM/SIGKILLs the still-working process group (`:205-209`). A running task is killed and reported crashed purely from a config value. The plugin test uses `fake-managed-runner.mjs` (`index.test.mjs:18`), which itself would not match — so no test covers this.

**3. Owner delivery reconciliation has no fallback and wedges permanently on a partial context**
`projects/execution-supervisor-taskflow/index.js:224` and `:279-280`

The ingress path passes `deliveryFromDispatch(event, ctx)` straight through with no `config.delivery` fallback — unlike the tool path, which does fall back (`:333`). `deliveryFromDispatch` returns `{channel, accountId, to: ctx.conversationId}` for any session key not matching the two Telegram shapes, so `to` can be `undefined`; `JSON.stringify` drops it and the supervisor persists `deliveryContext: {"channel":"telegram"}` (`:198`). Then `reconcileState` throws `missing originating delivery context` (`:280`) on a *terminal, successful* run. Consequences compound: the TaskFlow has already been `finish()`ed (`:274`), the owner is never notified, the terminal-cleanup block at `:292-297` is skipped so `admission.json` is never marked terminal and `admissionsByRun`/`admissionsBySession` are never cleared, and the tick retries and throws every 5 s forever with the error visible only in the service logger.

**4. `dispatch.lock` is a non-expiring lock with no owner check — one crash wedges an admission and blocks the session**
`projects/execution-supervisor-taskflow/index.js:176-187` (unlink only at `:211`/`:214`)

The lock is created with `flag: "wx"` and written with `process.pid`, but the PID is never read back and there is no staleness check or startup sweep. If the host dies between `:177` and the `spawn` at `:203`, the lock survives while `admission.json` is still `ADMITTED` (written at `:157`) and no supervisor state file exists — so the recovery scanner (`:307`) never sees it and never rotates the id. Every retry hits `EEXIST`, polls 5 s for a `DISPATCHED` that will never arrive, and throws (`:186`). Because ingress admission ids are `sha256(sessionKey + prompt)` (`:42-44`), resending the same request lands on the same wedged directory. In-process, the throw leaves the record `ADMITTED` in `admissionsBySession`, and `before_tool_call` (`:247-253`) then blocks every work tool for that session key with no TTL and no cleanup path.

## Verification results per criterion

| Criterion | Result |
|---|---|
| Exit code 0 alone is never SUCCEEDED | **Pass.** `:196-199` requires validated terminal evidence; bare exit 0 → `FAILED`, and a validated SUCCEEDED with nonzero exit is downgraded to `CRASHED` (`:197`). With `--terminal-evidence` absent, `terminal_from_evidence(None,…)` returns `None`, still `FAILED`. |
| Capability not persisted in plaintext | **Pass.** Only `terminalNonceHash` is written to state; nonce never enters state/EVIDENCE/outbox/argv, and it is generated in-process under `PR_SET_DUMPABLE=0` (`:174-179`). |
| Capability not inherited by the model | **Unverifiable in scope.** The supervisor hands the nonce over via `MANAGED_TERMINAL_FD` plus a `pass_fds` descriptor with CLOEXEC cleared (`:180-186`); both the env var and the fd propagate to every descendant of the runner by default. Whether the model can reach them depends entirely on `scripts/managed-agent-runner.mjs` draining and scrubbing before spawning the model — out of the requested scope. |
| Terminal evidence read only after runner exit | **Pass.** Read only under `code is not None` (`:195-196`) and, in recovery, only after the liveness check fails (`:248`). |
| Finalization / outbox race-safe | **Pass.** All four mutators (`finalize`, run heartbeat, `recover`, `ack`) `flock` the same derived path; `notify_once` dedupes by scanning the outbox before an `O_APPEND`+`fsync` write and is only invoked under that lock; state writes are tmp+fsync+rename; ordering (outbox before `notificationId`) survives a crash. No nested/self-deadlocking acquisition. |
| Admission idempotent | **Partial.** In-memory maps + on-disk `admission.json` + terminal-id rotation (`:124-126`) work, but the loser of a concurrent dispatch returns success details while leaving *its own* record `ADMITTED` (`:182-183`) — it keeps blocking tools and re-enters dispatch; and defect 4 breaks idempotent retry entirely. `admissionId()` (`:40`) also collapses distinct runIds that differ only in stripped characters into one task root. |
| Russian/English large objectives | **Pass.** `:32-37` covers the explicit Russian/English completion-notification forms, the Russian "full plan" form, and a ≥600-char imperative fallback in both languages. |
| High thinking | **Pass.** `--thinking config.managedAgentThinkingLevel ?? "high"` (`:202`); both schemas default to `high`. |
| Arbitrary-command start removed | **Pass.** No `execution_supervisor_start`; `execution_supervisor_dispatch` takes an empty closed object (`:325`) and the entire argv is plugin-derived (`:195-202`), spawned without a shell. Asserted at `index.test.mjs:65`. |
| Owner delivery reconciled | **Fail** — defect 3. |

## Lower-severity notes

- `execution-supervisor.py:173` — `requireValidatedTerminal` is derived from `bool(args.terminal_evidence)`, so the `--require-validated-terminal` flag (`:269`) is dead. Fail-closed, but the CLI contract is misleading and `test_strict_*` isn't actually testing the flag.
- `test_execution_supervisor.py:37-40` — the "forged terminal" test asserts `TIMED_OUT`, exercising the timeout path, not the nonce check. There is no test for the important case: well-formed `RESULT.json` with a wrong nonce plus a clean exit 0.
- `openclaw.plugin.json:6-11` declares only `contracts.tools`, while `register()` installs four hooks and a service. If the host gates activation on declared contracts (as the tool list implies), the admission gate and recovery service would be inert at startup — and the tests could not detect it, since they invoke handlers straight from the `hooks` map. Worth confirming against the plugin SDK, which was outside the inspection scope.
- `index.js:250-252` — the `blockReason` ternary re-tests `status === "DISPATCHED"`, already excluded at `:249`; the branch is dead.

**FAIL**
