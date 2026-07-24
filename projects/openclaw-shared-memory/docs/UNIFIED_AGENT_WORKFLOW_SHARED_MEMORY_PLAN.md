# Unified Plan: Agent Workflow / OpenClaw Shared Memory

Status: draft, replaces `IMPLEMENTATION_PLAN_V2.md` as the practical development roadmap
Date: 2026-07-22

## Purpose

Unify two related tracks:

- **OpenClaw Shared Memory**: controlled shared canon for decisions, state, facts, preferences, tasks, and incidents.
- **Agent Workflow**: the operating procedure that defines how agents receive work, prepare task packets, redact context, collect evidence, request review, and decide whether anything may enter the shared canon.

The combined project is an infrastructure layer for long-running multi-agent work. It must reduce context drift without turning private notes, Synology files, chats, or review packets into uncontrolled shared memory.

## Current State

- Baseline scaffold committed as `acccbae`.
- Phase 0 hardening committed as `8f68760`.
- Phase 1 disposable local DB pilot committed as `f262317`.
- Phase 1 proved role-scoped login users, candidate lifecycle, RLS/privacy denial, mirror allowlist, backup/restore drill, and unsafe guard checks.
- Agent Workflow templates exist at the workspace root, outside this project directory: `/home/stanislav/.openclaw/workspace/agents/main/templates/agent-workflow/`.
  - `TASK_NOTE.md`
  - `TASK_PACKET.md`
  - `AUDIT_PACKET.md`
  - `EVIDENCE.md`
  - `SECURITY_PRECHECK.md`
  - `ROLLBACK.md`
  - `AGENT_BRIEF.md`
- Pending Skill Workshop proposal exists: `agent-workflow-v2-20260722-747ac395f5`.

## Design Decision

Shared Memory is the canon. Agent Workflow is the admission and operating layer.

```text
Agent/local work
  -> TASK_NOTE / TASK_PACKET / SECURITY_PRECHECK
  -> bounded implementation or review
  -> EVIDENCE / AUDIT_PACKET
  -> optional Memory Candidate
  -> human-approved promote_to_shared
  -> Postgres/pgvector shared canon with audit
  -> filtered retrieval, mirror, backup, restore drill
```

No artifact becomes canon by existing on disk. It becomes canon only through an explicit memory workflow with source, actor, reason, confidence, scope, privacy class, and audit trail.

## Hard Boundaries

- Synology deployment, DSM/root/Docker/firewall/share/user/task changes require explicit owner approval.
- OpenClaw runtime/MCP config changes require explicit approval.
- Existing markdown memory remains operational source until migration is explicitly approved.
- Real memory import is not automatic.
- Real promotion, supersede, reject, and archive remain human-approved.
- External review packets must be redacted and must not contain secrets, `.env`, raw Synology contents, private chats, dumps, backups, or unnecessary local context.
- Plaintext mirror is allowlist-only. Current safe default is `shared_safe`; `project`, `personal_stanislav`, and `external_forbidden` must not enter plaintext mirror unless a later explicit policy changes this.
- `personal_stanislav` and `external_forbidden` must not enter external review packets.
- Backups containing real memory must be encrypted.
- Direct DB access by other machines is pilot/diagnostic only; final client path should be through OpenClaw Home MCP/API gateway.

## Authority Model

### Source Layers

- **Local agent notes**: private, fast, not canon.
- **Task packets and evidence**: project-local operational record, not canon by default.
- **Markdown memory files**: current operational source until migration decision.
- **Postgres shared canon**: future durable source for approved shared records only.
- **Markdown mirror**: recovery/bootstrap output from canon, not source of truth.
- **Backups**: encrypted recovery artifact, not query source.

### Record Admission

1. Agent creates work artifact: `TASK_NOTE.md` for low risk, `TASK_PACKET.md` for medium/high risk.
2. Security-sensitive work adds `SECURITY_PRECHECK.md`.
3. Work produces `EVIDENCE.md`.
4. External or second-pass review uses `AUDIT_PACKET.md` with redacted context.
5. Agent proposes a short Memory Candidate in chat.
6. Only after owner approval, candidate may become a `candidate` record.
7. Only after explicit promotion with reason/source/confidence/scope/privacy class, record becomes shared canon.

## Development Phases

### Phase 0 - Shared Memory Hardening

Status: done.

Evidence:

- `docs/PHASE0_HARDENING_EVIDENCE.md`
- commit `8f68760`

### Phase 1 - Disposable Local DB Pilot

Status: done.

Evidence:

- `docs/PHASE1_LOCAL_PILOT_EVIDENCE.md`
- commit `f262317`

Remaining before Phase 2, assigned to Phase 1.5:

- Make backup LOGIN `BYPASSRLS` provisioning explicit in Synology/deploy runbook.
- Tighten negative tests to assert expected DB/app error types.
- Fold mirror, backup, restore, and container-stop checks into an automated pilot runner.

### Phase 1.5 - Agent Workflow Integration Pilot

Status: next local work package.

Objective:

Use the Agent Workflow templates on this project itself before any Synology or runtime work. The goal is to prove that agent work can be packaged, reviewed, redacted, evidenced, and optionally converted into Memory Candidates without leaking private context or bypassing canon gates.

Tasks:

- Add `docs/AGENT_WORKFLOW_BRIEF.md` for this project, based on `/home/stanislav/.openclaw/workspace/agents/main/templates/agent-workflow/AGENT_BRIEF.md`.
- Add a task packet for the Phase 2 preparation package.
- Add `SECURITY_PRECHECK.md` for any Claude/Codex review packet.
- Add a redacted `AUDIT_PACKET.md` template instance for the next review.
- Add an evidence note showing which raw context is allowed locally and which context is excluded from review.
- Add one sample redacted Memory Candidate derived only from evidence.
- Close the three pre-Phase2 follow-ups:
  - explicit backup LOGIN `BYPASSRLS` provisioning in Synology/deploy runbook;
  - negative tests assert expected error types;
  - mirror, backup, restore, and container-stop checks are automated in the pilot runner.
- Confirm that Skill Workshop proposal `agent-workflow-v2-20260722-747ac395f5` remains pending unless explicitly applied.

Exit gate:

- Templates are exercised on a real project task.
- Redacted review packet contains only allowed context.
- No external send occurs without explicit approval.
- No Synology/runtime/real memory changes.
- A concise Memory Candidate can be produced from evidence without raw private data.
- The three pre-Phase2 follow-ups are resolved or explicitly carried as blockers.

### Phase 2 - Synology Deployment Preparation

Status: planned, no NAS changes.

Objective:

Prepare a NAS deployment package and approval request, but do not touch Synology.

Tasks:

- Verify Synology runbook includes explicit backup LOGIN `BYPASSRLS` provisioning from Phase 1.5.
- Make endpoint choice explicit:
  - preferred: Tailscale-only bind;
  - fallback: LAN IP `192.168.68.103` only if approved.
- Regenerate deploy package.
- Verify package contains migrations, compose, runbook, checklist, rollback notes, and no secrets.
- Write `TASK_PACKET.md`, `SECURITY_PRECHECK.md`, `ROLLBACK.md`, and `EVIDENCE.md` for Phase 2.
- Prepare exact approval request for Phase 3 with commands/actions listed.

Exit gate:

- Package is self-contained.
- No secrets in git/package.
- Runbook avoids passwords in shell argv.
- Approval request is concrete enough to approve or reject.
- No NAS state changed.

### Phase 3 - Synology Pilot Deployment

Status: blocked until explicit approval.

Objective:

Run the hardened DB on Synology as LAN/Tailscale-only pilot storage, still not an OpenClaw runtime dependency.

Tasks after approval:

- Copy approved package to approved Synology path.
- Create `.env` on Synology locally, outside git.
- Start container.
- Verify bind host is Tailscale IP or approved LAN IP, never wildcard.
- Verify no WAN reachability.
- Run direct role-scoped smoke from OpenClaw Home.
- Run encrypted backup and restore drill.
- Record evidence and rollback path.

Exit gate:

- Container healthy.
- Access limited to approved clients.
- Smoke lifecycle passes.
- Encrypted backup and restore drill pass.
- No real memory imported.

### Phase 4 - Read-Only MCP/API Gateway Pilot

Status: blocked until explicit runtime approval.

Objective:

Expose safe read-only memory tools through OpenClaw Home without making OpenClaw depend on the DB.

Tools:

- `search_memory`
- `get_with_audit`
- `list_candidates`

Requirements:

- caller identity;
- privacy policy enforcement;
- audit-aware retrieval;
- markdown fallback on failure;
- logs without secrets;
- smoke records only.

Exit gate:

- Read-only retrieval works through gateway.
- Failure does not break normal OpenClaw operation.
- Privacy denial demonstrated.
- Runtime change documented and approved.

### Phase 5 - Controlled Write Pilot

Status: prep package prepared, write pilot still human-approved only.

Objective:

Allow agents to propose records while canon-changing actions remain human-approved.

Tasks:

- Prepare a controlled candidate import task packet, precheck, approval request,
  synthetic fixture, and dry-run planner before any real import.
- Enable `propose_memory` for trusted agents through gateway.
- Import a tiny owner-approved subset from markdown as candidates, not shared records.
- Review candidate queue.
- Promote 1-3 low-risk records manually.
- Compare DB retrieval with markdown source.
- Monitor duplicates, stale records, and audit quality.

Exit gate:

- Proposals include source, actor, reason, confidence, scope, and privacy class.
- No automatic promotion.
- Candidate review is usable.
- Markdown remains operational source until migration decision.
- Prep-only dry runs do not read or write real memory by default.

### Phase 6 - Agent Workflow Skill Decision

Status: revised proposal pending; final skill decision still blocked.

Objective:

Decide whether Agent Workflow should become a live reusable skill/process, and whether the pending proposal should be applied, revised, or rejected.

Tasks:

- Inspect pending proposal `agent-workflow-v2-20260722-747ac395f5` through Skill Workshop.
- Compare proposal with this unified plan and real Phase 1.5-5 usage.
- Revise if the proposal misses Shared Memory boundaries.
- Apply only after explicit approval.

Exit gate:

- Skill proposal is applied, revised, rejected, or left pending deliberately.
- Live skill, if applied, matches actual project practice.
- Revised proposal is inspected before any final apply/reject/quarantine/leave
  pending decision.

### Phase 7 - Migration Decision

Status: blocked until pilot evidence exists.

Objective:

Decide whether DB canon becomes durable memory source of truth.

Tasks:

- Review Phase 0-5 evidence.
- Review audit logs and privacy behavior.
- Review backup/restore evidence.
- Decide source split:
  - DB canon for approved durable records;
  - markdown mirror for bootstrap/recovery;
  - daily logs for raw session notes;
  - local notebooks for private agent memory.
- Update `STATE.md` and `DECISIONS.md` only after approval.

Exit gate:

- Owner approves migration, or project remains experimental/inert.

## Immediate Next Work Package

Do Phase 1.5 only.

Deliverables:

- `docs/AGENT_WORKFLOW_BRIEF.md`
- `docs/PHASE2_PREP_TASK_PACKET.md`
- `docs/PHASE2_SECURITY_PRECHECK.md`
- `docs/PHASE2_AUDIT_PACKET.md`
- `docs/PHASE2_PREP_EVIDENCE.md`
- `docs/PHASE2_SAMPLE_MEMORY_CANDIDATE.md`
- updated `TODO.md`

Stop after the local planning/evidence package. Do not deploy to Synology, do not change OpenClaw runtime config, do not import real memory, and do not apply the pending Skill Workshop proposal without explicit approval.

## Open Questions

- Phase 4: should the future gateway expose `propose_memory` before Synology pilot, or only after Synology is stable?
- Phase 1.5: should plaintext mirror remain `shared_safe` only for production-like usage? Current plan assumes yes.
- Phase 3: which endpoint should Synology prefer: Tailscale IP only or LAN IP `192.168.68.103`?
- Phase 3/5: should backup/restore jobs live on Synology Task Scheduler later, or remain driven from OpenClaw Home?
