---
name: "agent-workflow-v2"
description: "Reusable agent workflow with risk, evidence, and memory gates."
---

# Agent Workflow v2

Status: pending proposal, not applied

## Purpose

Provide a reusable workflow for internal and external agent work across OpenClaw, Codex, Claude Code, subagents, cron/background jobs, Skill Workshop, and project-specific automation.

The workflow defines how agent work is admitted, scoped, evidenced, reviewed, and optionally proposed for durable shared memory without leaking private context or bypassing owner approval.

## Current Phase

This is a revised pending proposal based on the OpenClaw Shared Memory Phase 1.5-5 pilot.

It must not be applied, installed, or treated as canonical policy until Stanislav explicitly approves a later apply step.

## Core Workflow

1. Intake: identify project, goal, owner, risk tier, expected artifact, source of truth, and external-send risk.
2. Artifact gate: create a durable `TASK_NOTE.md`, `TASK_PACKET.md`, or equivalent checklist before meaningful autonomous work.
3. Context and security gate: locate local rules, privacy boundaries, approvals, secrets, Synology/home-LAN limits, and runtime constraints before edits or external review.
4. Implementation: make small scoped increments; keep subagents within assigned boundaries; do not expand scope silently.
5. Evidence: record changed files, commands, checks, screenshots/logs/counts, IDs, commits, and residual risks as relevant.
6. Review: use independent review for HIGH work and objective MEDIUM triggers; redact review packets before any external send.
7. Memory candidate gate: propose concise durable memories in chat; only owner-approved candidates may enter the memory admission flow.
8. Commit or handoff: report artifacts, checks, commit IDs, dirty worktree boundaries, pending approvals, and next gate.

## Risk Tiers

LOW: read-only or local low-risk work. Use `TASK_NOTE.md` or a small checklist. LOW auto-escalates if private data, secrets, production, access rights, Synology root/DSM, destructive actions, DB writes, memory promotion, source-of-truth migration, or external send appear.

MEDIUM: code, docs, process, local automation, or controlled non-production state changes without production deployment or external/customer send. Use `TASK_PACKET.md` or `PLAN.md`, checklist, and `EVIDENCE.md`/`REPORT.md`. Privacy-sensitive MEDIUM work requires a security precheck and review when practical.

HIGH: secrets, production deploys, root/system changes, Synology root/DSM, external/customer/public sends, access rights, destructive actions, real migration switchover, IP swap, storage pool changes, runtime gateway changes, write-capable MCP exposure, memory source-of-truth changes, or canonical memory promotion at scale. Requires `TASK_PACKET.md`, `SECURITY_PRECHECK.md`, `ROLLBACK.md`, `EVIDENCE.md`, explicit human approval, and review when practical.

## Approval Gates

Separate approval is required for each materially different gate:

- Synology, DSM, root, Docker, firewall, user, share, scheduler, or storage changes.
- OpenClaw runtime, gateway, model, auth, MCP, or config changes.
- External sends of prompts, packets, diffs, logs, screenshots, files, reports, or private/customer context.
- DB writes, even when candidate-only.
- Memory candidate import from existing markdown or notes.
- Promotion from candidate to shared canon.
- Reject, archive, supersede, or bulk memory lifecycle actions.
- Write-capable MCP/API exposure.
- Migration or source-of-truth changes.
- Applying, rejecting, or quarantining Skill Workshop proposals.

Prep packages, dry runs, and read-only inspection do not imply approval for the next gate.

## Shared Memory Admission

No artifact becomes shared canon by existing on disk, being committed, or being mentioned in chat.

Durable memory admission follows this path:

```text
work artifact / evidence
  -> Memory Candidate in chat
  -> owner approval
  -> candidate record with source, actor, reason, confidence, scope, privacy
  -> separate review / promotion approval
  -> shared canon with audit trail
```

Candidate import and promotion are separate actions. Automatic promotion is not allowed.

Markdown memory remains the operational source of truth until a separate migration decision explicitly changes that status. A markdown mirror generated from DB canon is a recovery/bootstrap artifact, not automatically the source of truth.

## Privacy Classes

Use explicit privacy classification for durable memory and review packets:

- `shared_safe`: safe for broad internal sharing and plaintext mirror by default.
- `project`: project-scoped; not for external review or plaintext mirror unless separately allowed.
- `personal_stanislav`: private to Stanislav/main context; do not expose in group/shared/external contexts.
- `external_forbidden`: never send externally; exclude from external review packets and hosted tools.

Plaintext mirror is allowlist-only. The safe default is `shared_safe` only.

External review packets must exclude secrets, `.env`, raw Synology contents, private chats, database dumps/backups, unredacted auth logs, customer confidential data unless approved/redacted, private pricing/discounts/negotiation context, and unnecessary local context.

## Runtime And MCP Boundaries

Read-only MCP/API tools and write-capable tools are different gates.

Read-only tools may be approved for limited retrieval with caller identity, privacy policy enforcement, audit-aware output, logs without secrets, and markdown fallback on failure.

Write-capable tools, candidate imports, promotion/reject/archive/supersede flows, and source-of-truth migration require separate explicit approvals. Do not expose write MCP tools merely because read-only MCP works.

Shared Memory DB access should be role-scoped. Separate reader, writer, promoter, backup, and owner/admin responsibilities where practical. Promotion should be audit-backed.

## Synology And Home LAN Boundaries

Synology is private infrastructure. Root-level Synology changes require explicit personal approval. Read-only diagnostics are allowed; changing DSM, Docker/Container Manager, firewall, packages, services, users, shares, rights, disks, tasks, or files is not.

The Shared Memory pilot learned that Synology may be blocked by missing Docker/Container Manager. OpenClaw Home can host a LAN-bound pilot, but direct DB access by other machines should remain pilot/diagnostic. The preferred final client path is OpenClaw Home MCP/API gateway.

Never bind services to wildcard/public interfaces unless explicitly approved. Backups containing real memory must be encrypted.

## External Send Boundary

Any prompt, packet, diff, screenshot, log excerpt, report, artifact, or file sent to Claude, Codex/OpenAI, web tools, hosted review services, browser/marketplace pages, remote servers outside the home LAN, public channels, customer channels, or other third parties is an external send.

Before external review or external send, use `SECURITY_PRECHECK.md` when privacy-sensitive or HIGH-risk data may be involved.

## Autonomous Agent Ceiling

Cron, heartbeat, and unattended background agents may run read-only checks, collect status, update internal state, create notes, notify about findings, and queue/propose next work.

They may not perform HIGH-risk actions, deploy, change access rights, change root/system/Synology settings, send customer/public messages, send private data externally, mutate canonical rules, delete/move data, rotate secrets, expose write tools, or change firewall/VPN/router state without explicit approval.

Each job needs an owner, expected output, timeout, runtime/model, failure mode, kill-switch/disable path, and notification threshold.

## Dirty Worktree Discipline

Assume the worktree may contain user or unrelated generated changes.

Before editing, inspect status. Keep commits scoped to the approved work. Do not revert unrelated files. If unrelated dirty files are present, name them in evidence/final status and leave them alone.

If changes in a required file appear unrelated or user-owned, read carefully and work with them. Ask only when they make the requested work impossible or unsafe.

## Template Files

Use existing workspace templates when available:

- `templates/agent-workflow/TASK_NOTE.md`
- `templates/agent-workflow/TASK_PACKET.md`
- `templates/agent-workflow/AUDIT_PACKET.md`
- `templates/agent-workflow/EVIDENCE.md`
- `templates/agent-workflow/SECURITY_PRECHECK.md`
- `templates/agent-workflow/ROLLBACK.md`
- `templates/agent-workflow/AGENT_BRIEF.md`

Keep artifacts close to the project being worked on, usually under `docs/`, `state/tasks/...`, or an equivalent project-local task folder.

## Skill Workshop Boundary

Creating, updating, revising, applying, rejecting, or quarantining reusable skills must go through Skill Workshop. Do not manually edit pending proposal files to change lifecycle state.

Revision is not application. Applying a proposal remains a separate explicit approval unless the user explicitly approves apply.

## Pilot Basis

This revised proposal incorporates lessons from the OpenClaw Shared Memory Phase 1.5-5 pilot:

- artifact-first task packets and evidence before risky work;
- read-only MCP before write-capable tools;
- candidate-only import before promotion;
- separate manual promotion approval;
- role-scoped DB access;
- audit trail checks;
- privacy classes and mirror allowlist;
- markdown source-of-truth boundary;
- Synology/home-LAN deployment split;
- dirty-worktree discipline.

## Approval Boundary

This proposal is still not a live rule, not installed, and not applied. Canonical workflow changes require a separate explicitly approved apply step after inspection of the revised proposal.
