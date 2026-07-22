# Task Note: Phase 0 Template Dry Run

Status: draft
Risk: LOW
Owner: main agent
Date: 2026-07-22

## Use When

This is a harmless dry-run task for Phase 0 of the agent workflow rollout. It verifies that the new templates exist and pass basic whitespace checks.

LOW is void and must be reclassified to MEDIUM or HIGH if private data, customer data, personal messages, secrets, production systems, access rights, Synology root/DSM settings, destructive actions, or external send appear.

## Goal

- Verify that Phase 0 templates were created in `templates/agent-workflow/`.
- Verify that the new markdown artifacts pass `git diff --check`.

## Scope

Allowed:

- read newly created Phase 0 artifacts;
- run `rg --files`;
- run `git diff --check`.

Forbidden:

- canonical rule edits;
- secrets or `.env` reads;
- production deploy/access/config changes;
- Synology root-level or DSM changes;
- external send;
- unrelated cleanup.

## Touched Files

- `templates/agent-workflow/TASK_NOTE.md`
- `templates/agent-workflow/TASK_PACKET.md`
- `templates/agent-workflow/AUDIT_PACKET.md`
- `templates/agent-workflow/EVIDENCE.md`
- `templates/agent-workflow/SECURITY_PRECHECK.md`
- `templates/agent-workflow/ROLLBACK.md`
- `templates/agent-workflow/AGENT_BRIEF.md`
- `state/tasks/2026-07-22-agent-workflow-rollout/PLAN_V2.md`
- `state/tasks/2026-07-22-agent-workflow-rollout/DRY_RUN_TASK_NOTE.md`

## Checks

- [x] `rg --files templates/agent-workflow`
- [x] `git diff --check -- templates/agent-workflow state/tasks/2026-07-22-agent-workflow-rollout`

## Result

- Pass. All seven template files are present.
- Pass. `git diff --check` reported no whitespace errors.

## Next

- If checks pass, Phase 0 is ready for the Shared Memory pilot.
