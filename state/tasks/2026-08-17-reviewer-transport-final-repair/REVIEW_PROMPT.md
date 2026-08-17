Review only the current diff in these files:

- `state/tasks/2026-08-12-orchestrator-integration/review_projection.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_integration.py`

Goal: safely normalize two formal reviewer transport defects without inventing
or upgrading evidence. Unknown fingerprint properties must be removed
deterministically before derived-ID normalization. Evidence kinds that require
a structured command (`command_output`, `test_result`, `build_log`) must be
discarded when `command` is missing. Positive claims weakened by discarded
evidence must fail closed as `not_verifiable`; a `still_open` result must remain
open so normalization cannot erase a persisting-defect claim. Malformed shapes
outside this narrow repair must remain contract failures.

Review both axes:

- Standards: determinism, schema/semantic safety, no evidence invention,
  minimal scope, regression coverage.
- Spec: exact behavior above, including final-full criteria, targeted positive
  claims, and preservation of `still_open`.

Do not edit files. Report findings grouped by blocker, major, and nit. End with
one line exactly in this form:

`VERDICT: ACCEPT` or `VERDICT: REWORK`
