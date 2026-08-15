# Reviewer control-character transport closure

Status: ACCEPTED
Owner: Stanislav
Risk: MEDIUM — local orchestrator code/tests and external model smoke; no deploy

## Goal

Keep strict rejection of decoded JSON control characters, while making every
bounded reviewer retry explicitly restate the transport invariant. Prove the
behavior with a red-capable controller test, then repeat the isolated real-project
smoke from a clean baseline.

## Boundaries

Allowed:

- `state/tasks/2026-08-12-orchestrator-integration/live_review_cycle.py`;
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_live_review_cycle.py`;
- this task folder and isolated run/worktree artifacts.

Forbidden:

- validator relaxation, JSON sanitization, or silent control-character rewriting;
- source `home-agent-factory` changes, dependency changes, deploy/push/cron/Gateway;
- more than two Codex attempts or the existing bounded reviewer retry chain.

## Acceptance

- retry prompts explicitly forbid decoded `U+0000` through `U+001F` and explain
  safe textual encoding;
- a deterministic test reproduces a contract-repair verdict containing decoded
  `U+0009`, then proves the bounded retry can produce an admissible verdict;
- existing integration/core tests and `git diff --check` pass;
- a fresh real-project smoke reaches a terminal policy result or retains a
  precise fail-closed blocker without modifying the source project.

## Checklist

- [x] Task packet created and dirty-worktree boundary recorded.
- [x] Red-capable regression added.
- [x] Minimal controller change implemented.
- [x] Focused and full checks pass.
- [x] Fresh isolated real-project smoke completed.
- [x] Evidence, rollback, and commit decision recorded.
