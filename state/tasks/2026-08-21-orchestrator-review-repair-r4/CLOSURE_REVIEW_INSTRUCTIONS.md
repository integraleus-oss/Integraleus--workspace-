# Targeted closure review

Verify only whether the current diff closes these previously reported major
findings without regression:

1. Diagnostics must cover normalization-caused criteria loss generally, not
   only command-evidence discard, and must identify affected criteria.
2. Contract-only repair must mechanically reject every newly introduced or
   changed command block, including under a new evidence ID.
3. Diagnostics must remain bounded, pointer-safe, content-redacted, and
   fail-closed; unrelated ProjectionError values must remain non-retryable.

Review these files only:

- `state/tasks/2026-08-12-orchestrator-integration/review_projection.py`
- `state/tasks/2026-08-12-orchestrator-integration/live_review_cycle.py`
- the corresponding changed tests.

Do not expand scope. Report blocker/major only if one of the three closure
claims is still false or the repair introduced a direct regression. Otherwise
return ACCEPTED_WITH_NOTES and list nits separately. Do not edit files.
