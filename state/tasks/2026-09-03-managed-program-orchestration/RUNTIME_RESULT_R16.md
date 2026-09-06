I read all five files. Findings below.

## HIGH defects

**1. Heartbeat resurrects a concurrently-finalized state → duplicate terminal notifications**
`scripts/execution-supervisor.py:211-219`

The 5s heartbeat takes the finalize lock but writes the **in-memory** dict back verbatim (`state["status"] = "RUNNING"`, line 217) without re-reading the persisted file. `recover` can legitimately finalize a live run: `recover` → `managed_runner_alive` true → elapsed ≥ timeout → `killpg` + `finalize(..., "TIMED_OUT")` (lines 245-250), and the plugin runs `recover` against RUNNING states every 5s (`index.js:319-323`).

Sequence: recover finalizes TIMED_OUT and appends `exec-<runId>-timed_out` to the outbox → heartbeat fires and reverts the state file to `RUNNING` (notificationId back to `None`) → supervisor observes the SIGTERM'd child, `finalize` re-reads the clobbered `RUNNING` (line 162-163 guard passes) and writes `CRASHED` → `notify_once` scans the outbox for `exec-<runId>-crashed`, doesn't find it, and appends a **second** terminal event (line 149-150). The owner gets two contradictory completion messages for one run, and EVIDENCE.md/state can end up disagreeing. Compare `recover:251-254`, which does re-read under the lock and re-check `TERMINAL` — the heartbeat is missing exactly that check.

**2. Recovery substitutes a self-reported exit code for the observed one**
`scripts/execution-supervisor.py:256-262` (with `terminal_exit_code`, line 89-95)

In the live path the "exit 0 alone is never SUCCEEDED" invariant holds, because `code` comes from `process.poll()` (lines 205-210). In the recovery path there is no independent exit observation: `recovered_exit` is read from the `exitCode` field of the **same RESULT.json the supervised process wrote**, then used to gate `observed == "SUCCEEDED"` (line 260) and persisted as the run's exit code (line 261). Both sides of the cross-check are the same attacker-controlled file, so the check is vacuous — a runner that exits non-zero but writes `{"terminalStatus":"SUCCEEDED","contractValidated":true,"exitCode":0,"terminalNonce":<nonce>}` is recorded SUCCEEDED. This is reachable without a crash: the plugin polls `recover` every 5s against RUNNING states, and there is a window of up to `--poll` (0.25s) between child exit and the supervisor's own finalize where `managed_runner_alive` is already false.

The same line breaks the honest case in the other direction: a real success recovered after a supervisor crash is downgraded to `CRASHED` whenever RESULT.json has no `exitCode` (`None != 0` → true). A runner cannot know its own exit code before exiting, which is why `test_execution_supervisor.py:78-93` has to hand-write `"exitCode": 0` to make recovery pass — the test encodes the flaw rather than catching it.

**3. Owner delivery target is taken from workspace files the supervised agent can write**
`projects/execution-supervisor-taskflow/index.js:274-278` and `290-298`

`reconcileState` validates `admission.json` against the state file only for self-consistency (`statePath`/`flowId`/`sessionKey` equality, lines 276-277). Both files live under `state/tasks/managed-admission/`, inside the workspace root handed to the managed agent (`MANAGED_WORKSPACE_ROOT`, line 214). The recovery service auto-discovers *any* `execution-supervisor-state.json` under that tree (line 319). A managed agent that creates a directory containing a mutually-consistent `admission.json` + state file with `status: "SUCCEEDED"`, `notificationDelivered: false`, and an arbitrary `deliveryContext` passes `validate_recovery_state` (the sibling-path check is satisfiable by writing correct absolute paths) and then reaches line 293-298, where the plugin loads an arbitrary channel adapter and sends text with attacker-chosen `to`/`threadId`, with attacker-chosen `status`/`flowId`/`runId` interpolated into the body. The supervisor itself acknowledges this threat model (`execution-supervisor.py:215-216`: "disk state is never authoritative"), but the reconciler trusts disk state for routing.

**4. Post-dispatch foreground work is not blocked; the blocking branch is dead code**
`projects/execution-supervisor-taskflow/index.js:259-264`

Line 261 returns early when `admission.status === "DISPATCHED"`, so the ternary at line 262 (`"...already detached; foreground work is blocked."`) is unreachable — its condition can never be true at that point. The intent was clearly to keep the admitted turn from doing the work in the foreground while the detached run proceeds; as written, once `execution_supervisor_dispatch` returns, `bash`, `sessions_spawn`, `apply_patch` etc. are all permitted in the same turn, duplicating the managed run. `index.test.mjs:109-110` and `124-125` lock in the permissive behavior.

## Items that check out

- Exit code 0 without validated terminal evidence → `FAILED` (`execution-supervisor.py:210`), and `SUCCEEDED` + non-zero → `CRASHED` (line 208); covered by tests at `test_execution_supervisor.py:31-33`.
- Terminal capability is never persisted: only `sha256` is stored (line 186), delivered out-of-band over a one-shot pipe rather than argv/state (lines 192-197), and `test_execution_supervisor.py:37` asserts absence of `terminalNonce` in state. Caveat: `pass_fds` marks the fd inheritable and `MANAGED_TERMINAL_FD` is in the full child environment, so anything the runner execs before draining the pipe can steal the nonce — containment depends on `managed-agent-runner.mjs`, which is outside this review's scope.
- Terminal evidence is only read after `process.poll()` returns (lines 205-207); the timeout branch never consults it (`test_..._forged_terminal_is_not_accepted_while_child_is_running`), and stale RESULT.json is unlinked pre-launch (line 173).
- `notify_once` dedupes by scanning the outbox for the event id under the finalize lock, and `ack` is lock-guarded — sound apart from defect 1.
- Admission is idempotent for the normal paths: `wx`-flagged writes with EEXIST-read-back (lines 147-164), deterministic ingress id (line 43), and terminal admissions rotate to a fresh id (lines 124-126). Russian and English large-objective patterns are covered (lines 10-15, 35-36). Thinking level is passed as `high` by default and enforced by the fake runner (line 213, `index.test.mjs:22`). `execution_supervisor_start` is gone; only `dispatch`/`recover` are registered (lines 333-364, `openclaw.plugin.json:7-10`, asserted at `index.test.mjs:65`).

## Lower-severity, worth noting

- `index.js:237` — the ingress path passes `messages: []`, so `CONTEXT.json` is always empty for the path that actually handles owner requests (`before_dispatch` returns `handled: true`); the context capture at line 146 only ever fires on the `before_agent_run` path.
- `index.js:184-198` — `dispatch.lock` staleness is broken by unlink-then-recurse, which two racers can both perform; a double dispatch produces two supervisors on one state file with distinct `runId`s, hence two non-deduplicable outbox events.
- `execution-supervisor.py:184` — `--require-validated-terminal` is accepted but never read; strictness is implied by `--terminal-evidence`. Harmless (stricter), but the flag is misleading.
- `openclaw.plugin.json:6-11` — `contracts` declares only `tools`; the four `api.on(...)` hooks are undeclared. I could not verify whether the host gates hook registration on declared contracts without reading files outside the permitted set.

**FAIL**
