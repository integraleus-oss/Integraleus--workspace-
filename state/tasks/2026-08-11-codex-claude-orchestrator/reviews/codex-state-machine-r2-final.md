Implemented State Machine Targeted R2 entirely under `implementation/`; no commit made.

Key changes:

- Canonically sorts history for every merged registry record, including untouched records.
- Defines occurrence identity as `(review_id, occurrence_id)`.
- Preserves existing matching entries without overwriting.
- Allows the same `occurrence_id` across different reviews.
- Added exact SM-07 accepted-path permutation regression.
- Added cross-review reuse and next-invocation validation regression.
- Documented the invariant in [STATE_MACHINE.md](/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-11-codex-claude-orchestrator/implementation/STATE_MACHINE.md).
- Appended verification details to [EVIDENCE.md](/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-11-codex-claude-orchestrator/implementation/EVIDENCE.md).

Verification passed:

- Focused policy tests: 57
- All tests: 79
- Both schema self-checks
- Policy fixtures
- `py_compile`
- `git diff --check`
- Supplemental whitespace scan

No reviewer-contract files, reports, task packets, shared files, or files outside `implementation/` were edited.