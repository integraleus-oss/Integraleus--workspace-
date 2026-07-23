# Agent Brief: OpenClaw Shared Memory

Status: active for Phase 1.5 pilot
Owner: main agent with Stanislav approval gates
Date: 2026-07-23

## Purpose

- Build a controlled shared memory canon for OpenClaw agents.
- Exercise Agent Workflow artifacts before any Synology, runtime, MCP, or real-memory migration work.
- Keep task packets, evidence, redaction, review, and Memory Candidate handling explicit and auditable.

## Canonical Root

- `/home/stanislav/.openclaw/workspace/agents/main/projects/openclaw-shared-memory`

## Source Of Truth

- `docs/UNIFIED_AGENT_WORKFLOW_SHARED_MEMORY_PLAN.md`
- `TODO.md`
- `docs/MCP_TOOLS.md`
- `migrations/*.sql`
- `src/openclaw_shared_memory/`
- `scripts/`
- `deploy/synology/`
- workspace Agent Workflow templates at `/home/stanislav/.openclaw/workspace/agents/main/templates/agent-workflow/`

## Safe To Read

- This project directory.
- Workspace Agent Workflow templates.
- Project-local test output and generated disposable artifacts.
- Daily workspace notes needed to continue this topic.

## Safe To Edit

- This project directory only, unless Stanislav explicitly expands scope.
- `docs/`, `scripts/`, `tests/`, `deploy/synology/`, and project `TODO.md`.

## Never Edit Without Approval

- canonical workspace rules and long-term memory files;
- secrets, `.env`, session files, databases, backups;
- `/opt` symlink targets unless approved deployment flow says so;
- production configs/deployments/access rights;
- root-owned system configs;
- Synology root-level/DSM settings;
- firewall/VPN/router state;
- customer/public-facing materials after draft stage.

## Privacy Boundaries

- Real markdown memory remains operational source until migration is explicitly approved.
- Real memory import is not automatic.
- Raw Synology file contents must not leave the home network and must not be included in review packets.
- `personal_stanislav` and `external_forbidden` content must not be sent to external review.
- Plaintext mirror default is allowlist-only: `shared_safe`.
- Phase 1.5 may use disposable smoke records only.

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

- `git status --short --branch`
- `python3 -m pytest`
- `python3 -m compileall src scripts`
- `OPENCLAW_MEMORY_PHASE1_ADMIN_DATABASE_URL=... scripts/run_phase1_pilot_checks.sh` when disposable Postgres is available.
- `git diff --check`

## Stop Conditions

- scope expands beyond Phase 1.5 packaging or local disposable checks;
- private data would leave allowed boundary;
- secret or raw private content is required;
- production/root/Synology/access/destructive change is needed;
- external send is needed without approval;
- verification cannot be performed.

## Known Decisions

- Shared Memory is the canon layer; Agent Workflow is the admission and operating layer.
- No artifact becomes canon merely by existing on disk.
- Synology work is Phase 2 preparation only until explicit Phase 3 approval.
- Skill Workshop proposal `agent-workflow-v2-20260722-747ac395f5` remains pending unless Stanislav explicitly applies it.

## Open Questions

- [ ] Phase 3 endpoint preference is still approval-gated: Tailscale-only preferred, LAN IP fallback only if approved.
- [ ] Migration of existing markdown memory to DB canon remains undecided.
