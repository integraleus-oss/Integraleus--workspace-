# Local orchestrator controlled-manual-use assessment

Date: 2026-08-16

Verdict: READY FOR A SEPARATELY APPROVED CONTROLLED MANUAL OPENCLAW PILOT;
NOT ACTIVATED; NOT READY FOR UNATTENDED USE

## What was proved

- Nine bounded real manual tasks were attempted (`manual-001` through
  `manual-009`). Five reached `ACCEPTED / R17_ACCEPT`; four ended fail-closed
  `ESCALATED`.
- Accepted: 001, 004, 006, 007, 008.
- Escalated: 002, 003, 005, 009.
- Three accepted results were separately transferred and committed to source:
  manual-004 (`6e56761`), manual-006 (`f25e001`), and manual-007 (`8985b8e`).
- manual-008 is accepted but remains isolated pending a separate transfer.
- manual-009 exposed a real major runtime/schema mismatch and then stopped on
  an invalid repaired reviewer contract; its diff remains prohibited.
- The controller preserved source boundaries, enforced allowed paths and
  attempt limits, retained sealed evidence, required deterministic admission,
  handled interruption structurally, and left no orphan continuation.
- No task performed automatic push, deploy, Gateway/runtime/config change,
  cron, systemd/daemon activation, or unattended execution.

## Operating quality

- Safety: strong. No false acceptance was observed; ambiguous, timed-out, or
  invalid reviews stopped fail-closed.
- Engineering usefulness: demonstrated. Accepted tasks produced tested source
  improvements, while failed tasks found material defects before transfer.
- Efficiency: moderate to poor. Claude timeouts and exact-JSON/contract repairs
  created long cycles and several safe but operationally expensive
  escalations.
- Operator burden: still material. Task packets, isolated worktrees, review
  retries, evidence recording, and source transfer remain supervised steps.

## Recommended OpenClaw pilot boundary

Permit only a separately approved thin manual trigger that starts one existing
foreground production-cycle task and returns structured status/evidence to the
operator. Keep these restrictions:

- one task per invocation and one approved repository/worktree;
- explicit task packet, allowed paths, gates, budgets, and timeouts;
- maximum two Codex implementations plus one review-only final-full leg;
- no automatic source transfer, commit, push, deploy, or external send;
- no cron, daemon, background continuation, or unattended retry;
- operator-visible `ACCEPTED`, `ESCALATED`, `FAILED_INFRA`, or `INTERRUPTED`;
- manual approval remains required for source transfer and every higher-risk
  runtime/deployment action;
- kill switch is foreground interruption, which must retain structured
  `INTERRUPTED` evidence and prevent continuation.

## Remaining work, intentionally bounded

1. Decide whether to transfer accepted manual-008 in a separate source step.
2. If the capability-grant change is still desired, create one fresh task for
   the manual-009 major; never transfer its current diff.
3. Before unattended use, materially improve reviewer response reliability and
   run a new readiness assessment. This is not required for the limited manual
   OpenClaw pilot because failures remain safe and visible.

## Decision gate

This report does not activate or integrate the orchestrator. OpenClaw
runtime/config/Gateway changes remain a materially separate action requiring
Stanislav's explicit approval after reviewing this recommendation.
