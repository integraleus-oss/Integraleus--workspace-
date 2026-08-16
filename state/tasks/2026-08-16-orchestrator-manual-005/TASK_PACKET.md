# Manual-005 — requestedModelClass contract hardening

Status: ESCALATED; TRANSFER PROHIBITED

## Goal

Close the non-blocking `manual-004` reviewer nit by validating and normalizing
the requested model class before policy decisions and grant construction.

## Fixed point and scope

- Source: `/home/stanislav/projects/home-agent-factory`.
- Fixed commit: `6e56761030812f0387dbbe570a199b37c3088ca5`.
- Detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-005-model-class`.
- Run evidence:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-005-model-class-run`.
- Allowed files: `src/core/policy.js`, `test/policy.test.js`.
- Forbidden: every other source path, dependencies, network, source transfer,
  commit, push, deploy, Gateway, cron, systemd, daemon, unattended execution,
  and system changes.

## Acceptance criteria

- [ ] `requestedModelClass` is a primitive string and exactly `local` or
  `cloud`, whether supplied by request context, pack default, or fallback.
- [ ] Invalid types and unknown/case-variant values fail closed with a stable
  controlled `PolicyError` before approval logic or grant construction.
- [ ] Precedence remains request context, then pack default, then `local`.
- [ ] The accepted scalar is stored in the deeply frozen grant without adding
  dependencies or weakening existing policy checks.
- [ ] Tests cover both sources, fallback, precedence, invalid types, unknown
  values, and the cloud/private-data approval branch.
- [ ] `npm test` and `git diff --check` pass; only the two allowed files change.

## Budgets and stop conditions

- Maximum two Codex implementation attempts.
- Maximum one policy-triggered review-only final-full Claude leg.
- Standard single contract-only reviewer repair.
- Gate and agent timeout: 60 seconds and 600 seconds respectively.
- Unknown failure, forbidden path, unresolved major finding, exhausted budget,
  invalid verdict, or interruption means STOP without transfer.

## Checklist

- [x] Task packet and boundaries created before autonomous work.
- [x] Detached worktree created cleanly at the fixed commit.
- [x] Managed production cycle completed with terminal `ESCALATED`.
- [x] Evidence and changed paths independently checked.
- [x] Result recorded; source remains unchanged and transfer is prohibited.
