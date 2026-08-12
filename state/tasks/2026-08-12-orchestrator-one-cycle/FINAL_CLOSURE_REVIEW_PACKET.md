# Independent closure review

Review the completed bounded one-cycle provenance increment. Read only:

- `../orchestrator-integration/managed_one_cycle.py`
- `../orchestrator-integration/managed_policy_review.py`
- `../orchestrator-integration/live_review_cycle.py`
- `../orchestrator-integration/tests/test_managed_one_cycle.py`
- `../orchestrator-integration/tests/test_live_review_cycle.py`
- `TASK_PACKET.md`
- `EVIDENCE.md`
- `live-provenance-trial/review-1/cycle-result.json`
- `live-provenance-trial/review-1/admitted-review.json`
- `live-provenance-trial/review-2/cycle-result.json`
- `live-provenance-trial/honest-closure-review/cycle-result.json`
- `live-provenance-trial/honest-closure-review-r2/cycle-result.json`
- `live-provenance-trial/honest-closure-review-r2/admitted-review.json`

Verify whether authority is deterministic, digest/path admission is fail-closed,
and the evidence honestly proves fresh live `REWORK` followed by an actual
subject-bound fresh closure and mechanical `ACCEPTED`. Treat the two rejected
closure attempts as evidence of fail-closed behavior, not success. Report only
blocker/major/nit findings and end exactly `ONE_CYCLE_CLOSURE_PASS` or
`ONE_CYCLE_CLOSURE_REWORK`. Do not edit files.
