# Managed one-cycle orchestrator

Status: COMPLETED_COMMITTED
Baseline: `bada693`
Risk: MEDIUM

## Goal

Implement one bounded coordinator cycle: Codex attempt -> Claude review ->
deterministic decision -> at most one Codex rework -> Claude closure -> final
decision.

## Boundaries

- Local synthetic fixture only; isolated workspace and single-use evidence dirs.
- Maximum two Codex attempts and two Claude reviews.
- No Gateway/config/systemd/cron, GitHub/push, deploy, Synology, secrets, or
  unattended execution.
- `ESCALATED`, unknown failure, malformed output, or exhausted budget stops.
- `ACCEPTED` records status only; it never commits, pushes, or deploys.

## Checklist

- [x] Task packet created.
- [x] Implement deterministic cycle controller.
- [x] Test ACCEPTED, REWORK, FAILED_INFRA, ESCALATED, and budget exhaustion.
- [x] Run synthetic bounded agent-path trial.
- [x] Independent review and bounded authority rework.
- [x] Add fail-closed admission from live contract/projection/policy evidence.
- [x] Prove both live trial decisions through the admitted automatic chain.
- [x] Prove fresh live REWORK through contract/projection/policy/admission.
- [x] Generate an honest closure contract bound to the actual synthetic repo.
- [x] Admit fresh closure as `ACCEPTED / R17_ACCEPT`.
- [x] Independent closure review.
- [x] Scoped local commit (`1da5c7c`).
- [x] Final tests and scoped local commit.
