# Agent Brief: <project or workflow>

Status: draft
Owner: <main agent / project owner>
Date: <YYYY-MM-DD>

## Purpose

- <what this project/workflow is for>

## Canonical Root

- <path or "unknown, discovery required">

## Source Of Truth

- <docs, files, services, repos>

## Safe To Read

- <paths/systems>

## Safe To Edit

- <paths/systems>

## Never Edit Without Approval

- canonical rules and memory files;
- secrets, `.env`, session files, databases, backups;
- `/opt` symlink targets unless approved deployment flow says so;
- production configs/deployments/access rights;
- root-owned system configs;
- Synology root-level/DSM settings;
- firewall/VPN/router state;
- customer/public-facing materials after draft stage.

## Privacy Boundaries

- <project-specific private data rules>

External send requires:

- `SECURITY_PRECHECK.md`;
- explicit approval if private/customer/personal data is involved;
- redacted packet.

## Standard Task Artifacts

LOW:

- `TASK_NOTE.md`

MEDIUM:

- `TASK_PACKET.md` or `PLAN.md`;
- checklist;
- `EVIDENCE.md` or `REPORT.md`.

HIGH:

- `TASK_PACKET.md`;
- `SECURITY_PRECHECK.md`;
- `ROLLBACK.md`;
- `EVIDENCE.md`;
- approval record;
- review when practical.

## Standard Checks

- <commands and manual checks>

## Stop Conditions

- scope expands beyond packet;
- private data would leave allowed boundary;
- secret or raw private content is required;
- production/root/Synology/access/destructive change is needed;
- external send is needed without approval;
- verification cannot be performed.

## Known Decisions

- <decision>

## Open Questions

- [ ] <question>
