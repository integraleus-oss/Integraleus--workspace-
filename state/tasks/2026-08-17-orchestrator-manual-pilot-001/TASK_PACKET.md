# Controlled manual OpenClaw pilot 001

Status: COMPLETE — ESCALATED; TRANSFER PROHIBITED
Risk: MEDIUM
Owner: Stanislav / main agent

## Goal

Run one useful foreground task through the existing bounded Codex → Claude
orchestrator: freshly close the capability-grant runtime/schema mismatch found
by manual-009. The rejected manual-009 diff is not reused.

## Fixed point

- Source: `/home/stanislav/projects/home-agent-factory` at `8985b8e`.
- Detached worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant`.
- New run root: `/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant-run`.

## Allowed paths

- `src/core/policy.js`
- `schemas/capability-grant.schema.json`
- `test/policy.test.js`

## Hard boundaries

- Foreground, one task, bounded timeouts and attempts.
- No reuse or transfer of the manual-009 diff.
- No source commit or transfer even if accepted.
- No push, deploy, dependency/network, Gateway/config, systemd, cron,
  unattended continuation, or external-system change.
- Stop fail-closed on scope drift, failed gates, invalid review contract,
  unresolved blocker/major, timeout, or interruption.

## Checklist

- [x] Owner approved controlled manual pilot in Telegram message `3321`.
- [x] Detached clean worktree created at the fixed source commit.
- [x] Fresh implementation/review packet created.
- [x] Managed cycle reached terminal `ESCALATED` after one implementation.
- [x] Evidence, changed paths, gates, and worktree state recorded.
- [ ] Any accepted source transfer remains a separate approval.
