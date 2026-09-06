Test execution was blocked (Bash denied for the test commands), so this is a static review of the five files. I did not edit anything.

## Verdict per requirement

| Requirement | Result |
|---|---|
| exit 0 alone is never SUCCEEDED | **PASS** |
| terminal capability not in plaintext state | **PASS** |
| terminal capability not inherited by the model | **FAIL** (H3) |
| terminal evidence read only after runner exit | **FAIL** (H4 — recover window) |
| finalization/outbox race-safe | **PASS** (with M9 on delivery) |
| admission idempotent | **FAIL** (H1, M7) |
| RU/EN large objectives | **FAIL** (M8 — gaps both ways) |
| high thinking | **PASS** |
| arbitrary-command start removed | **PASS** |
| owner-delivery reconciliation | **FAIL** (H2) |

## HIGH defects

**H1 — `dispatch.lock` is never released on failure; one dispatch error permanently bricks the admission and the session.**
`projects/execution-supervisor-taskflow/index.js:177` takes the `wx` lock *before* all fallible work (`createManaged` :188, `spawn` :202, `writeFile` :207). Any throw leaves the lock on disk with `admission.json` still `ADMITTED`. Every retry then takes the EEXIST branch (`index.js:180-186`), polls 100×50 ms for a `DISPATCHED` status that can never appear, and throws `concurrent admission dispatch did not settle`. Meanwhile `before_tool_call` (`index.js:240-246`) keeps blocking every tool for that session.
Concrete triggers: `admission.sessionKey` is `null` (ctx without sessionKey) → non-string argv element at `index.js:197` → Node `ERR_INVALID_ARG_TYPE`; or `python3` absent from PATH → `child.once("error", fail)` at `:203`. Outcome: the owner session can neither work nor dispatch, permanently.

**H2 — `config.delivery` fallback is unreachable; a missing origin means the owner is never notified, in a 5 s error loop forever.**
`index.js:325`: `ctx.deliveryContext ?? deliveryFromDispatch({}, ctx) ?? config.delivery`. `deliveryFromDispatch` always returns an object (`index.js:171-172`), so `?? config.delivery` is dead code and the `delivery` block in `openclaw.plugin.json:23-32` is never consulted. With no `ctx.channelId`/`ctx.conversationId` the delivery context serializes to `{}`; `reconcileState` then throws `missing originating delivery context` at `index.js:273` *before* the ack, so `notificationDelivered` stays false, the tick's skip condition at `index.js:302` never holds, and the service retries and logs every `pollMs` indefinitely with zero delivery.

**H3 — the terminal capability is inheritable by the whole descendant tree, not scoped to the runner.**
`scripts/execution-supervisor.py:181-186` writes the nonce into a pipe and exports `MANAGED_TERMINAL_FD` into the child environment via `pass_fds`. The fd is handed over without `FD_CLOEXEC` and the env var propagates, so every grandchild of `managed-agent-runner.mjs` — including the model/agent process it spawns — can `os.read()` the fd and write a `{contractValidated:true, terminalNonce}` RESULT.json, turning an unproven run into `SUCCEEDED` (`execution-supervisor.py:92-95`). The only possible mitigation (consume-and-close before the model starts) lives in `managed-agent-runner.mjs`, outside the review scope, so the supervisor itself does not establish the property. Also note `prctl(PR_SET_DUMPABLE, 0)` at `:179` protects only the supervisor — dumpable resets to 1 across the child's `execve`, so the nonce-holding runner is not protected.
The plaintext half is fine: only the sha256 is persisted (`:174-175`, asserted `test_execution_supervisor.py:36`).

**H4 — `recover` can declare a live run CRASHED, and the live supervisor then kills it.**
`execution-supervisor.py:187` persists the state file with `pid` but no `pidStartTicks`; `:188` adds them in a *second* write. `managed_runner_alive` short-circuits to `False` when `pidStartTicks` is absent (`:81`), so a `recover` landing in that window skips the liveness check entirely, reads the (absent) terminal evidence at `:245`, and finalizes `CRASHED` at `:247` — terminal, with an outbox notification. The still-running supervisor's heartbeat (`:199-207`) then sees the TERMINAL status and SIGTERMs the process group. The plugin runs a tick at service start and every 5 s (`index.js:299-308`), so it can land there. This is also the one path where terminal evidence is consulted while the runner is alive. Fix: one atomic write containing both `pid` and `pidStartTicks`.

**H5 — `recover` accepts SUCCEEDED without the non-zero-exit guard the run loop applies.**
`execution-supervisor.py:196` downgrades a validated `SUCCEEDED` to `CRASHED` when the runner exited non-zero. `recover` (`:245-247`) has no equivalent guard and passes `state.get("exitCode")` (`None`). A runner that writes valid SUCCEEDED evidence and then dies non-zero reports `SUCCEEDED` whenever the supervisor was itself lost, and `CRASHED` when it survived — the same physical outcome yields two different truths.

**H6 — session-wide tool lockout with no TTL and no escape hatch.**
`index.js:240-246` blocks *every* tool for any turn resolving to a DISPATCHED admission via `admissionsBySession` (`index.js:111-112`). The map entry clears only when `reconcileState` observes a TERMINAL state (`index.js:288-289`). Until then — up to `managedAgentTimeoutSeconds` (max 86400), or forever if no state file was ever created (see H1) — every *unrelated* request in that Telegram topic has all tools blocked. `index.test.mjs:109-110` asserts this as intended, so it is a deliberate design, but as written the block is keyed on session rather than on the originating turn and has no expiry.

## MEDIUM defects worth fixing

**M7 — admission is not idempotent across the two entry points.** `index.js:118` derives the id from `ctx.runId` when present and otherwise from `sha256(sessionKey, prompt)`. Ingress (`before_dispatch`, no runId) and `before_agent_run` (runId) therefore produce different ids and different `state/tasks/managed-admission/<id>` directories for the same message. Today `before_dispatch` returns `{handled:true}` which should suppress the agent run, but nothing enforces that — and when ingress is skipped by the `authorizedSenderIds` gate (`:214-215`) while `before_agent_run` still admits (`:228-232`), the same objective is admitted twice under two ids.

**M8 — `requiresManagedExecution` (`index.js:32-37`) misses and over-fires.** Misses: the stems must be followed by whitespace/`,`/`:`, so Russian infinitives ("Нужно выполнить весь план…", "Прошу реализовать…") match none of the five patterns, and English `migrate`/`refactor`/`rewrite`/`create`/`design`/`ship` are absent from `:36`, so a large objective runs foreground and unmanaged. Over-fires: `:36` admits *any* ≥600-char message containing a standalone `fix`/`build`/`execute` — a pasted log or a long question locks the session (H6) and detaches an agent.

**M9 — delivery is at-least-once with no cross-process guard.** `index.js:274-282` sends, then acks in a separate `python3 ack` process; nothing holds the supervisor's finalize lock across the pair, so a crash between them or a second plugin instance resends. `deliveryQueueId: state.notificationId` is the sole dedup and depends on the adapter honoring it.

**M10 — `authorizedSenderIds` is not an effective allowlist.** Enforced only at `index.js:215`; `before_agent_run` (`:229`) and the dispatch tool (`:320`) gate on `isTrustedOwnerContext`, which ORs `senderIsOwner` (`:54-57`), so an excluded sender flagged as owner still reaches dispatch.

**M11 — `safePath` doesn't canonicalize the target.** `index.js:60-65` realpaths only the root and prefix-matches `resolve(requested)`; a symlink under the workspace pointing outside passes. Bounded by `validate_recovery_state` (`execution-supervisor.py:65-76`) and the admission cross-check (`index.js:257-258`), and owner-only.

**M12 — unhandled `TimeoutExpired` in the heartbeat kill path.** `execution-supervisor.py:205` `process.wait(timeout=5)` is not wrapped, unlike `:211-212` and `:218-219`; a slow-dying child raises past the `except KeyboardInterrupt` at `:215`, so the supervisor exits with a traceback and never escalates to SIGKILL.

**M13 — `--require-validated-terminal` is dead.** Defined at `execution-supervisor.py:265`, but `:173` overwrites the value with `bool(args.terminal_evidence)`. It fails safe (strict is always on when terminal evidence is configured), but `index.js:198` passes it as if it were meaningful.

## What holds up

- Exit 0 alone is never SUCCEEDED: `execution-supervisor.py:195-198` maps exit 0 with no validated evidence to `FAILED`, and validated-SUCCEEDED with non-zero exit to `CRASHED`; covered by `test_execution_supervisor.py:30, 32, 43`. Forged nonces are rejected (`test:37-40`) and stale `RESULT.json` is unlinked pre-launch (`:162`, `test:41-43`).
- Evidence is read only after `process.poll()` returns (`:193-195`) — the run path is clean; only `recover` has the H4 window.
- Finalization is flock-serialized on `<state>.finalize.lock` across `finalize`/`recover`/`ack`/heartbeat (`:148-157, 201-207, 230-233, 240-243, 251-255`), each re-reading persisted state under the lock; the outbox dedups by event id (`:131-137`). No lock re-entrancy hazard: no path calls `finalize` while already holding the lock.
- Arbitrary-command start is gone: no `execution_supervisor_start` (asserted `index.test.mjs:65`), and `execution_supervisor_dispatch` takes a closed empty object (`index.js:318`).
- High thinking is wired end to end: `index.js:201` default `"high"`, schema defaults at `index.js:22-24` and `openclaw.plugin.json:20`, and the fake runner exits 9 otherwise (`index.test.mjs:22`).
- Nested managed sessions cannot recurse (`index.js:117`, asserted `index.test.mjs:143-145`).

## FAIL

H1 and H2 are permanent-wedge failures reachable from ordinary configuration; H3 leaves the SUCCEEDED capability forgeable by the very process it is meant to constrain; H4 can kill a healthy managed run and report it as CRASHED. Also note that `.finalize.lock` and `dispatch.lock` artifacts are never cleaned up and are already showing as untracked files in the working tree.
