# Orchestrator Review-to-Repair and R4 Closure

Status: IN_PROGRESS

## Goal

Close the confirmed review-loop defect exposed by Universal Integration R4,
qualify it with deterministic regression coverage, then prepare a bounded R4
repair packet from the sealed review evidence.

## Boundaries

- Orchestrator code: `state/tasks/2026-08-12-orchestrator-integration/**`.
- R4 source implementation remains isolated in its existing worktree.
- Do not modify canonical `/home/stanislav/projects/alpha-bpr`.
- Do not transfer, commit, push, or deploy Alpha BPR product code.
- Do not weaken scope, ignored-state, timeout, gate, or review admission checks.

## Acceptance criteria

- Cross-cutting review findings are contract-valid and deterministically mapped.
- A review with blocker/major findings can drive at most one bounded repair
  attempt inside a controlled cycle.
- Gates rerun after repair and closure review remains independent.
- Scope, timeout, ignored-state, infrastructure, and malformed review failures
  remain fail-closed.
- Existing and new orchestrator regression tests pass.
- A fresh R4 repair packet is sealed only after the infrastructure change is
  reviewed and qualified.

## Checklist

- [x] Add red regression cases for the R4 failure mode.
- [x] Implement the minimal review-to-repair change.
- [x] Run orchestrator regression and independent review.
- [x] Record evidence and stable checkpoint.
- [ ] Prepare bounded R4 repair packet and publish a separate RUN digest.
