# Evidence: Phase 6.1 Skill Wording Cleanup

Status: ready
Date: 2026-07-24

## Scope

Clean up proposal-era wording in the live `agent-workflow-v2` skill through
Skill Workshop update/apply.

Approved command:

```text
approve Phase 6.1 cleanup agent-workflow-v2 live wording via Skill Workshop update and apply only
```

## Boundaries

- [x] Do not manually edit `skills/agent-workflow-v2/SKILL.md`.
- [x] Do not change workflow gates by intent.
- [x] Do not change OpenClaw runtime/MCP config.
- [x] Do not write to the Shared Memory DB.
- [x] Do not import, promote, reject, archive, or supersede memory records.
- [x] Do not change markdown source-of-truth status.

## Checklist

- [x] Read live skill wording.
- [x] Create Skill Workshop update proposal.
- [x] Inspect update proposal.
- [x] Apply update proposal.
- [x] Re-read live skill wording.
- [x] Update TODO/plan/evidence.
- [x] Run project checks.
- [x] Commit artifacts and live skill update.

## Skill Workshop Update

Used Skill Workshop:

```text
action=update
skill_name=agent-workflow-v2
```

Result:

```text
Created skill update proposal agent-workflow-v2-20260724-8fa58cd92a (pending) for agent-workflow-v2.
```

## Proposal Inspection

Used Skill Workshop:

```text
action=inspect
proposal_id=agent-workflow-v2-20260724-8fa58cd92a
```

Result:

```text
Proposal: agent-workflow-v2-20260724-8fa58cd92a
Status: pending
Kind: update
Skill: agent-workflow-v2
Version: v1
Scan: clean
```

## Apply

Used Skill Workshop:

```text
action=apply
proposal_id=agent-workflow-v2-20260724-8fa58cd92a
```

Result:

```text
Applied skill proposal agent-workflow-v2-20260724-8fa58cd92a.
```

## Post-Apply Inspection

Used Skill Workshop:

```text
action=inspect
proposal_id=agent-workflow-v2-20260724-8fa58cd92a
```

Result:

```text
Proposal: agent-workflow-v2-20260724-8fa58cd92a
Status: applied
Kind: update
Skill: agent-workflow-v2
Version: v1
Scan: clean
```

## Live Skill Check

`skills/agent-workflow-v2/SKILL.md` now says:

```text
Status: live skill
```

The previous proposal-era phrases `pending proposal, not applied`, `not a live
rule`, `not installed`, and `later apply` are absent. The remaining phrase
`pending proposal files` appears only in the general Skill Workshop boundary
about not manually editing proposal lifecycle files.

## Result

Phase 6.1 cleanup is complete. The live skill wording now matches its applied
state, and no workflow gate was intentionally changed.

## Verification Summary

- `.venv/bin/python -m compileall -q src scripts` -> passed
- `.venv/bin/python -m pytest` -> `2 passed`
- `git diff --check -- projects/openclaw-shared-memory skills/agent-workflow-v2` -> passed
- `rg -n "pending proposal, not applied|not a live rule|not installed|later apply" skills/agent-workflow-v2/SKILL.md` -> no matches
