# Phase 6 Prep: Agent Workflow Skill Decision

Status: prepared, no Skill Workshop lifecycle action applied
Date: 2026-07-24

## Approved Scope

Stanislav approved:

```text
approve Phase 6 agent workflow skill decision prep only
```

## Goal

Compare the pending Skill Workshop proposal
`agent-workflow-v2-20260722-747ac395f5` against actual OpenClaw Shared Memory
Phase 1.5-5 practice and prepare a recommendation.

## Boundaries

- Do not apply the pending skill proposal.
- Do not revise the pending skill proposal in Skill Workshop during prep.
- Do not reject or quarantine the proposal.
- Do not change live skills.
- Do not change OpenClaw runtime/MCP config.
- Do not write to Shared Memory DB.
- Do not change markdown memory source-of-truth status.

## Proposal Inspected

Skill Workshop returned:

```text
Proposal: agent-workflow-v2-20260722-747ac395f5
Status: pending
Kind: create
Skill: agent-workflow-v2
Version: v1
Scan: clean
```

## What Still Matches

- The overall intake -> plan gate -> implementation -> evidence -> review ->
  commit/handoff workflow matches the project practice.
- The LOW/MEDIUM/HIGH risk tier split is still useful.
- The external-send boundary matches Shared Memory privacy practice.
- The autonomous-agent ceiling matches the heartbeat/cron safety model.
- Template references match the actual workspace template set.
- The approval boundary correctly says the proposal is not live until
  separately approved.

## Gaps Against Actual Phase 1.5-5 Practice

The pending proposal should not be applied as-is because it predates the real
Shared Memory pilot evidence.

Missing or too generic:

- Shared Memory admission rule: artifact on disk is not canon by itself.
- Candidate lifecycle: Memory Candidate -> owner approval -> DB candidate ->
  separate promotion approval -> shared canon.
- Runtime gate: read-only MCP tools are allowed separately from write tools.
- Write gate: candidate writes, promotion, reject/archive/supersede, and
  source-of-truth migration each require separate approvals.
- Privacy classes: `shared_safe`, `project`, `personal_stanislav`,
  `external_forbidden`, mirror allowlist, and external-review exclusions.
- Markdown source-of-truth boundary until explicit migration decision.
- Synology/home-LAN split learned during Phase 3: Synology blocked by missing
  Docker/Container Manager, home pilot bound to `192.168.68.125:55432`.
- Role-scoped DB practice: reader/writer/promoter/backup separation and
  audit-backed promotion.
- Evidence-first execution strengthened by later phases: each risky gate got a
  task packet/evidence/checklist before DB/runtime changes.
- Dirty worktree discipline from this pilot: unrelated `STATE.md` and
  `website/spectech/*` changes must remain outside Shared Memory commits.

## Recommendation

Revision has been approved and completed after this prep step.

Current next action:

```text
approve Phase 6 apply revised agent-workflow-v2 proposal
```

Applying the revised proposal is still a separate Skill Workshop lifecycle
action. Leaving it pending deliberately is also acceptable if the workflow
should remain advisory for now.

## Explicitly Not Recommended Yet

- Do not apply `agent-workflow-v2-20260722-747ac395f5` without separate
  approval.
- Do not reject it; it is structurally sound.
- Do not quarantine it; scan is clean and there is no safety incident.
- Do not begin Phase 7 migration/source-of-truth decision until the workflow
  skill decision is closed or deliberately postponed.
