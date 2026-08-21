# Independent review: criteria-normalization diagnostics

Review only the current diff in these files:

- `state/tasks/2026-08-12-orchestrator-integration/review_projection.py`
- `state/tasks/2026-08-12-orchestrator-integration/live_review_cycle.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_integration.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_live_review_cycle.py`

Goal: when bounded transport normalization makes full-review criteria coverage
incomplete, the one contract-only retry must receive the exact semantic errors
and normalization actions that caused the loss of evidence. It must remain
fail-closed, must not invent evidence, and must not make unrelated projection
errors retryable.

Report blocker/major/nit findings. Verify both Standards and Spec. Do not edit
files. Return concise Markdown.
