# Controlled failure drills

Status: COMPLETE WITH ONE DEFECT

These drills exercise fail-closed behavior without modifying any source
repository. Exact commands and observed outcomes are recorded below as they run.

## Checklist

- [x] Mandatory gate failure produces no false success.
- [x] Allowlisted known infrastructure failure is classified distinctly.
- [x] Unknown implementation failure escalates and stops.
- [x] Invalid Claude response receives only bounded repair (observed live in
  T03; preserved under its sealed run evidence).
- [x] Repeated invalid Claude response is rejected fail-closed.
- [x] Foreground operator interruption stops and does not continue
  automatically; structured terminal evidence is deficient (see below).

## Deterministic harness results

The following focused drills passed:

- `TrustedReviewBuilderTests.test_rejects_failed_or_unallowlisted_gate`
- `LocalIntegrationTests.test_known_infrastructure_failure_uses_allowlist_policy`
- `ManagedOneCycleTests.test_known_and_unknown_implementation_failure`
- `LiveReviewCycleTests.test_format_retry_is_single_and_second_malformed_reply_fails_closed`

The first combined command passed its first three drills and exposed an
incorrect Python import path for the fourth. Re-running the fourth with
`PYTHONPATH=.:tests` passed. This operator command error did not affect product
state and was not hidden.

The complete integration suite was then run with:

`PYTHONPATH=.:tests python3 -m unittest discover -v tests`

Result: 86 tests run, 86 passed, 0 failures, 0 errors in 7.483 seconds.

## Live invalid-review evidence

T03's real Claude review initially failed trusted contract admission. The
bounded repair path produced an admissible exact contract and no unbounded
retry occurred. The review then reached `R15_NEED_FULL_REVIEW`, followed by a
review-only `R17_ACCEPT` leg.

## Live foreground interruption

The operator-interruption packet passed strict validation and ran against a
clean detached worktree at the fixed baseline. The operator sent `Ctrl-C`
during the Codex launch.

Observed:

- foreground CLI exited immediately with code 1;
- no Codex or orchestrator child process remained;
- no automatic continuation occurred;
- the detached worktree remained clean;
- no `cycle-result.json` was created;
- `attempt-1/codex/input-prompt.md` remained as partial evidence;
- the terminal output was an unhandled `KeyboardInterrupt` traceback.

Defect: manual interruption is operationally effective, but the CLI does not
catch the signal, terminate through a documented state, or write a structured
`INTERRUPTED` terminal record. The evidence is therefore insufficient for the
pilot's auditability criterion.
