# Independent RUN_EVIDENCE review

Review only the staged diff (`git diff --cached`) for these files. The new
files are intentionally staged so they are present in the review payload:

- `state/tasks/2026-08-12-orchestrator-integration/run_evidence.py`
- `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/managed_one_cycle.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_run_evidence.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_managed_one_cycle.py`

Spec axis:

1. Every admitted production run creates `RUN_EVIDENCE.jsonl` before agent
   execution.
2. Events are versioned, monotonic, append-only and hash-chained.
3. Existing, malformed, externally modified, or post-terminal streams fail
   closed.
4. ACCEPTED, ESCALATED/FAILED_INFRA, ERROR and INTERRUPTED all receive one
   terminal event.
5. Builder runs record agent, exact changed paths, gates and review summaries.
6. Evidence must not contain raw prompts, secrets, tokens or reviewer prose.
7. The existing two-attempt ceiling and clean-new-run-root invariant remain
   effective.

Standards axis:

- race/symlink/path safety;
- crash durability and error preservation;
- deterministic, meaningful tests;
- compatibility with legacy validation/replay behavior;
- no scope expansion or unrelated edits.

The local focused suite passed 55/55. The full suite passed 184/184 and
`git diff --check` passed. Verify rather than trust these claims.

Return `ACCEPTED` or `REWORK`, with blocker/major findings first and minor/nit
afterward. Do not modify files.
