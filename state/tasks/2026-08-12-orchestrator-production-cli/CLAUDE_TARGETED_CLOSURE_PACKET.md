# Targeted closure: bounded production CLI

Review the current versions of:

- `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-production-cli/TASK_PACKET.md`
- prior findings in `state/tasks/2026-08-12-orchestrator-production-cli/CLAUDE_REVIEW.md`.

Do not edit or inspect unrelated files. Verify specifically:

1. MAJOR 1: write-enabled Codex project roots are restricted to approved local
   bases and Git repo/worktree roots.
2. MAJOR 2: CLI exit codes and validate-only/error behavior have exact tests.
3. TOCTOU: review inputs are copied without following symlinks and rescanned.
4. A write-Codex timeout escalates rather than being marked retryable infra.
5. Invalid UTF-8/path errors and missing attempt-2 rework fail closed.

Report any remaining blocker/major with file:line evidence. End exactly
`PRODUCTION_CLI_CLOSURE_PASS` if none remain, otherwise end exactly
`PRODUCTION_CLI_CLOSURE_REWORK`.
