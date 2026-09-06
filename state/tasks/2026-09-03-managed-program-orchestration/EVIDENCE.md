# Managed Program Orchestration Evidence

Status: BLOCKED_EXTERNAL_REVIEW_TIMEOUT
Last verified: 2026-09-04T13:24:00+03:00

## R20 checkpoint

- Remediated R12-R19 HIGH/CRITICAL findings across the runner, supervisor and
  TaskFlow bridge, including evidence binding, immutable objective snapshots,
  review TOCTOU checks, atomic PID persistence, dispatch idempotency, trusted
  delivery derivation, fail-closed cold recovery, and child process cleanup.
- Latest local gate: runner PASS; supervisor 14/14 PASS; TaskFlow integration
  PASS; syntax PASS; plugin doctor PASS; git diff check PASS.
- R20 core and runtime independent reviews both timed out at 300 seconds and
  produced no valid verdict. No reviewer process remains.
- No commit, Gateway restart, or live drill was performed.
Last verified: 2026-09-04T12:48:00+03:00
Last verified: 2026-09-04T12:17:00+03:00

## R13 execution-truth correction

- Completed: atomic initial persistence of PID plus pidStartTicks; bounded
  SIGTERM-to-SIGKILL handling in the terminal heartbeat branch; recovery
  rejects SUCCEEDED when no zero exit code is recorded.
- Checks completed at 09:53: supervisor tests 13/13 PASS, Python syntax PASS,
  and git diff check PASS.
- No work process remained after the foreground turn; no managed continuation,
  R13 review, commit, Gateway restart, or live drill existed.
- The prior RUNNING_R13_REWORK label became unsupported and is corrected to
  STALE_R13_REWORK.
Last verified: 2026-09-04T09:52:00+03:00
Last verified: 2026-09-04T09:42:00+03:00
Last verified: 2026-09-04T09:37:00+03:00
Last verified: 2026-09-03T23:20:00+03:00
Last verified: 2026-09-03T23:02:00+03:00

## Initial finding

- ZSR runner exited 0 after 458405 ms while reporting `PARTIAL_BLOCKED`.
- Supervisor persisted `SUCCEEDED` because runner exit code 0 was treated as task success.
- No machine-readable objective-completion contract or continuation loop existed.

## Dirty-worktree boundary

- Existing modified/untracked files outside the scoped implementation are user-owned and untouched.
- The uncommitted dashboard project is unrelated and excluded from this change.

## Checks

- [x] Runner unit tests: PASS, including success, two-slice continuation,
  invalid completion, rejected `PARTIAL_BLOCKED`, invalid/valid external
  blocker, and child crash.
- [x] Supervisor unit/recovery tests: 13/13 PASS.
- [x] Plugin integration tests: PASS.
- [x] Syntax checks: PASS for contract, runner, and plugin.
- [x] `git diff --check`: PASS for scoped files.
- [x] `openclaw plugins doctor`: no plugin issues detected.
- [ ] Independent Standards review
- [ ] Independent Spec review

## Implemented behavior

- Added `MANAGED_OUTCOME.json`, validated independently from agent prose.
- Added durable work packages and acceptance gates with evidence requirements.
- `SUCCEEDED` now requires every package/gate PASSED and
  `objectiveComplete=true`.
- `CONTINUE` launches another agent turn in the same managed session.
- `PARTIAL_BLOCKED` and self-declared `FAILED` are not accepted terminal
  outcomes; they continue until a valid result or execution budget failure.
- `BLOCKED` requires an external reason, evidence, and owner action.
- Managed slices use `high` thinking by default instead of inheriting `low`.
- Supervisor and TaskFlow now preserve `BLOCKED` as a real terminal state.
- Terminal capability travels once through an inherited pipe, is removed before
  model execution, and only its SHA-256 hash is persisted. The supervisor does
  not inspect terminal files until the runner process has exited.
- The locked package/gate plan is stored separately and survives failed slices.
- A failed slice is retried up to a bounded limit; it does not immediately end
  the complete objective.
- Candidate terminal outcomes require an independent high-reasoning review in
  a separate managed session before the runner can emit terminal evidence.
- The arbitrary-command supervisor start tool was removed.
- Model-authored evidence commands were removed; contracts can reference only
  durable file artifacts, which the independent reviewer must inspect.
- The complete package/gate plan is authored before execution by a separate
  high-reasoning planner session; the executor cannot narrow it.
- Evidence must be new for the current run, unique per claim, non-empty,
  hash-matching, and contained inside the configured workspace.
- Exit code 0 without a validated objective contract is always `FAILED`; the
  legacy CLI success escape hatch was removed.

## Activation boundary

- Gateway was not restarted and live runtime was not changed.
- Plugin source version is 0.3.0; live process remains on the previously loaded
  implementation until explicit activation approval.
- No commit or push was performed.

## Review gate blocker

- R11 core review: not started; provider session limit.
- R11 runtime review: not started; provider session limit.
- Provider-reported reset: 00:30 Europe/Moscow.
- Safe continuation: rerun the two bounded R11 review packets, fix any
  HIGH/CRITICAL findings, then commit, restart Gateway, and run a real Telegram
  live drill only after both verdicts are PASS.

## R12 review outcome

- Core review: FAIL (`CORE_RESULT_R12.md`). HIGH findings include forgeable
  mtime-only evidence freshness, missing terminal result after locked-plan
  deletion, insufficient deterministic verification, and missing adversarial
  tests.
- Runtime review: FAIL (`RUNTIME_RESULT_R12.md`). HIGH findings include a
  permanent dispatch-lock wedge, broken delivery fallback, capability/fd scope
  concerns, recovery races and inconsistent recovery success handling, plus a
  session-wide lockout without a safe expiry.
- Both reviewer processes exited normally. No live review process remains.
- No commit, Gateway restart, or live drill was performed.
