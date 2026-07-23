# Task Packet: Phase 2 Synology Deployment Preparation

Status: active
Risk: MEDIUM
Owner: main agent
Date: 2026-07-23

## Goal

- Prepare the Phase 2 Synology deployment package, review packet, and approval request without changing NAS, runtime, MCP, production, or real memory state.

## Why Now

- Phase 0 and Phase 1 proved the local DB hardening and disposable pilot.
- Phase 1.5 must prove Agent Workflow packaging before the project moves toward NAS deployment.

## Risk Tier

Selected tier: MEDIUM

Rationale:

- The work is local documentation and disposable automation, but it prepares a privacy-sensitive infrastructure project and future Synology deployment.
- It must keep external review redacted and prevent accidental real-memory or NAS changes.

Auto-escalate to HIGH if the task touches private data, customer data, personal messages, secrets, production systems, access rights, Synology root/DSM settings, destructive actions, or external send.

## Scope

Allowed:

- `docs/AGENT_WORKFLOW_BRIEF.md`
- `docs/PHASE2_PREP_TASK_PACKET.md`
- `docs/PHASE2_SECURITY_PRECHECK.md`
- `docs/PHASE2_AUDIT_PACKET.md`
- `docs/PHASE2_PREP_EVIDENCE.md`
- `docs/PHASE2_MEMORY_CANDIDATE_SAMPLE.md`
- `deploy/synology/RUNBOOK.md`
- `scripts/run_phase0_safety_tests.py`
- `scripts/run_phase1_local_pilot.py`
- `scripts/run_phase1_pilot_checks.sh`
- `TODO.md`
- local disposable test databases only

Forbidden:

- secrets/tokens/passwords/API keys;
- `.env` contents unless explicitly needed and kept local;
- production deploys or access changes without explicit approval;
- direct writes to `/opt` unless explicitly approved;
- root-level changes without explicit approval;
- Synology root-level or DSM changes without explicit approval;
- external send without explicit approval and `SECURITY_PRECHECK.md`;
- customer/public messages without explicit approval;
- destructive operations without explicit approval;
- unrelated refactors.

## Source Of Truth

- `docs/UNIFIED_AGENT_WORKFLOW_SHARED_MEMORY_PLAN.md`
- `TODO.md`
- Agent Workflow templates under `/home/stanislav/.openclaw/workspace/agents/main/templates/agent-workflow/`
- Phase 0/1 evidence docs

## Inputs

- Stanislav's Telegram command: "делай Phase 1.5" on 2026-07-23.
- Existing unified roadmap commits `5e9a434` and `6c1dddb`.
- Existing Phase 0/1 scripts and Synology deploy profile.

## Assumptions

- No external review will be sent during Phase 1.5 unless Stanislav separately approves it.
- Test automation may use disposable local databases whose names include `phase1`, `drill`, `test`, or `scratch`.
- Container stop/start checks are allowed only for the local compose project and only when explicitly enabled with an environment flag.

## Open Questions

- [ ] Whether to actually run an external Claude review after redaction is a separate approval decision.

## Plan

- [x] Research/source review
- [x] Create Agent Workflow artifacts for this project
- [x] Implement pre-Phase2 follow-up fixes
- [x] Evidence capture
- [x] Review gate if required
- [ ] Handoff/final report

## Required Evidence

- commands run;
- files changed;
- tests/smoke checks;
- unresolved risks.

## Review Gate

Mandatory review if:

- risk becomes HIGH;
- an external packet is actually sent;
- access boundaries, migrations, schemas, cron/background automation, or runtime config are changed.

Reviewer:

- main self-review for local Phase 1.5;
- Claude/Codex external review only after explicit approval and redaction.

## Approval Gate

Explicit approval required before:

- production deploy;
- external send;
- public/customer-facing send;
- root-level/system changes;
- Synology root-level/DSM changes;
- destructive operation;
- migration switchover/IP swap/storage pool change.

Approval record:

- none for local Phase 1.5 documentation and disposable automation.

## Done Means

- [x] Goal achieved or blocker documented
- [x] Evidence captured
- [x] Review findings resolved or accepted as residual risk
- [ ] User-facing report sent if needed
- [ ] Commit/handoff state recorded when relevant
