# Orchestrator review-loop reduction

## Goal

Reduce review churn while preserving fail-closed safety.

## Required policy

- Freeze acceptance criteria before implementation.
- `ACCEPTED` is impossible with open blocker or major findings.
- At most two substantive review passes per task: initial full, then targeted
  closure. No automatic third final-full review.
- New non-blocking concerns discovered after the initial full review become
  follow-up items unless they are regressions caused by the bounded rework or
  violations of frozen criteria.
- Small tasks may use a light profile: gates plus one full review and separate
  transfer.
- Exhaustion produces a clear escalation/follow-up record, not an endless loop.

## Boundaries

- Modify orchestrator code, tests, schemas/docs only where required.
- Do not change Gateway, systemd, model/auth configuration or deployed agents.
- No push or deploy.
- Commit/transfer to canonical project remains a separate gate if work is done
  in an isolated worktree.

## Checks

- Targeted policy/runtime tests.
- Full orchestrator integration suite.
- `git diff --check`.
- Independent review of Standards and Spec.
