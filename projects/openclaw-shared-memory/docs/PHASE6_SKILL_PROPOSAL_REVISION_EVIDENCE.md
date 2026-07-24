# Evidence: Phase 6 Skill Proposal Revision

Status: ready
Date: 2026-07-24

## Scope

Revise the pending Skill Workshop proposal
`agent-workflow-v2-20260722-747ac395f5` from OpenClaw Shared Memory phase
evidence.

Approved command:

```text
approve Phase 6 revise agent-workflow-v2 proposal from Shared Memory phase evidence
```

## Boundaries

- [x] Do not apply the proposal.
- [x] Do not reject or quarantine the proposal.
- [x] Do not change live skills.
- [x] Do not change OpenClaw runtime/MCP config.
- [x] Do not write to the Shared Memory DB.
- [x] Do not import, promote, reject, archive, or supersede memory records.
- [x] Do not change markdown source-of-truth status.

## Inputs

- `docs/PHASE6_SKILL_DECISION_PREP.md`
- `docs/PHASE6_SKILL_DECISION_EVIDENCE.md`
- `docs/UNIFIED_AGENT_WORKFLOW_SHARED_MEMORY_PLAN.md`
- Skill Workshop inspection of
  `agent-workflow-v2-20260722-747ac395f5`

## Checklist

- [x] Inspect pending Skill Workshop proposal.
- [x] Revise proposal through Skill Workshop.
- [x] Re-inspect revised proposal.
- [x] Update this evidence file with result.
- [x] Run project checks.
- [x] Commit documentation/evidence changes.

## Skill Workshop Revision

Used Skill Workshop:

```text
action=revise
proposal_id=agent-workflow-v2-20260722-747ac395f5
```

Result:

```text
Revised skill proposal agent-workflow-v2-20260722-747ac395f5 (pending) for agent-workflow-v2.
```

## Re-Inspection

Used Skill Workshop:

```text
action=inspect
proposal_id=agent-workflow-v2-20260722-747ac395f5
```

Result:

```text
Proposal: agent-workflow-v2-20260722-747ac395f5
Status: pending
Kind: create
Skill: agent-workflow-v2
Version: v2
Scan: clean
```

## Revision Summary

The revised proposal remains pending and unapplied. It now includes concrete
gates learned from the Shared Memory pilot:

- artifact-first execution;
- separate approvals for prep, runtime, DB writes, candidate import, promotion,
  lifecycle actions, write-capable MCP, and source-of-truth migration;
- Memory Candidate -> owner approval -> DB candidate -> separate promotion ->
  shared canon;
- explicit privacy classes: `shared_safe`, `project`, `personal_stanislav`,
  and `external_forbidden`;
- markdown source-of-truth boundary until separate migration approval;
- read-only MCP and write-capable MCP separation;
- role-scoped DB practice;
- Synology/home-LAN boundaries;
- dirty-worktree discipline.

## Stop Gate

The next action is a separate owner decision: apply revised proposal, leave it
pending, reject, or quarantine. This revision did not apply it.

## Verification Summary

- `.venv/bin/python -m compileall -q src scripts` -> passed
- `.venv/bin/python -m pytest` -> `2 passed`
- `git diff --check -- projects/openclaw-shared-memory` -> passed
