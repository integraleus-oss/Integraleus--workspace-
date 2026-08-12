# Bounded authority closure review

Read only these files:

- `../orchestrator-integration/managed_one_cycle.py`
- `../orchestrator-integration/managed_policy_review.py`
- `../orchestrator-integration/tests/test_managed_one_cycle.py`
- `live-provenance-trial/review-1/cycle-result.json`
- `live-provenance-trial/review-1/admitted-review.json`
- `live-provenance-trial/review-2/cycle-result.json`
- `live-provenance-trial/honest-closure-review/cycle-result.json`
- `live-provenance-trial/honest-closure-review-r2/cycle-result.json`
- `live-provenance-trial/honest-closure-review-r2/admitted-review.json`

Check only: deterministic outcome authority; digest/path fail-closed admission;
REWORK packet derivation; evidence that fresh live REWORK and actual
subject-bound fresh ACCEPTED both passed admission; and that two malformed or
misbound closure responses produced no policy decision. Do not edit. Report
blocker/major/nit, then end exactly `ONE_CYCLE_CLOSURE_PASS` or
`ONE_CYCLE_CLOSURE_REWORK`.
