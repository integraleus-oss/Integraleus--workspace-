# Independent harness qualification review

Review only the current uncommitted diff in:

- `state/tasks/2026-08-12-orchestrator-integration/trusted_review_builder.py`
- `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_trusted_review_builder.py`

Spec axis:

1. Direct builder calls must permit only attempts 1 and 2.
2. Attempt 2 must require the frozen acceptance-criteria digest and reject a
   mismatch.
3. Authenticated builder repair must carry the same frozen digest even when
   attempt-1 gates failed before a review binding was completed.
4. Exact files inside a newly untracked directory must be checked against the
   allowlist as individual paths.
5. Existing two-attempt production behavior must remain functional.
6. Unknown/infrastructure failures must not become implementation repair.

Standards axis:

- fail-closed behavior;
- no hidden third review path;
- no scope expansion or unrelated changes;
- deterministic tests;
- no regression in the 177-test suite.

Return a concise verdict: ACCEPTED or REWORK. List blocker/major findings first,
then minor/nit. Do not modify files. Treat EVIDENCE.md and historical result
summaries as context only; verify claims from code and tests.
