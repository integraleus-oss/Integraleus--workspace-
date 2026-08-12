# Targeted closure of REWORK directive coverage

Read only:

- `../orchestrator-integration/managed_policy_review.py`
- `../orchestrator-integration/tests/test_managed_one_cycle.py`
- `FINAL_CLOSURE_REVIEW_R2.md`

Verify that the earlier major is closed: every accepted policy REWORK rule
(`R09`, `R11`, `R13`, `R15`) has a bounded, policy-derived packet path; finding
IDs must resolve against trusted projection; malformed/unsupported directives
fail closed; regressions cover added paths. Do not edit. End exactly
`DIRECTIVE_CLOSURE_PASS` or `DIRECTIVE_CLOSURE_REWORK`.
