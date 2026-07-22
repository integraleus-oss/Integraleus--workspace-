# OpenClaw Shared Memory Implementation Plan

Status: audited draft
Date: 2026-07-22

## Goal

Deploy a LAN/Tailscale-only shared memory canon for OpenClaw agents, backed by Postgres + pgvector, hosted on Synology NAS, with OpenClaw Home acting as the controlled MCP/API gateway.

## Non-Negotiable Boundaries

- No public internet exposure.
- No Synology root-level or Docker/Container Manager changes without explicit owner approval.
- No import of existing markdown memory or private notebooks without explicit owner approval.
- No automatic promotion to shared canon.
- No raw Synology file contents leave the home network.
- Current markdown memory remains operational source until the pilot passes and migration is approved.

## Target Architecture

```text
Local PCs / OpenClaw agents
        |
        | LAN or Tailscale only
        v
OpenClaw Home MCP/API gateway
        |
        | restricted DB roles
        v
Synology Postgres + pgvector
        |
        +-- encrypted backups
        +-- privacy-filtered markdown mirror
        +-- append-only audit log
```

## Phase 0 — Hardening Patch Before Any Deployment

Objective: make the scaffold safe enough to test on a disposable local DB.

Tasks:

- Add an additive, idempotent `002_hardening.sql`; do not edit `001_initial_schema.sql` as if no database ever existed.
- Bind Synology compose to an explicit host IP, not `0.0.0.0`.
- Add `OPENCLAW_MEMORY_BIND_HOST` to Synology env example.
- Add DB roles for least privilege:
  - owner/admin for migrations only
  - app_writer for proposals
  - app_promoter for promotion/supersession/rejection/archive
  - app_reader for retrieval
  - backup_reader for dumps
- Wire application code to actually use least-privilege roles, not a single all-powerful `OPENCLAW_MEMORY_DATABASE_URL`.
- Add row-level security policy foundations keyed on `privacy_class`.
- Add `content_hash` and idempotent proposal handling.
- Add `current_shared_canon` view.
- Enforce audit immutability with DB trigger or revoked privileges.
- Add `reject_candidate`, `archive_record`, and `list_candidates`.
- Restrict `supersede` to current `shared` records only.
- Add server-side privacy filters for search/get/list operations.
- Add mirror export privacy allowlist.
- Add restore drill guard: production URL must not equal drill URL.
- Add sha256 verification before restore.
- Add encrypted backup option before any real data is dumped.
- Remove password-in-command examples from runbooks; prefer env/`.pgpass` style.
- Document additive migration application for already-initialized databases.
- Update docs to state search is text-only until embeddings are wired.

Acceptance:

- `scripts/validate_schema.py` proves Phase 0 hardening artifacts, including roles, RLS, audit immutability, `content_hash`, `current_shared_canon`, explicit bind host, privacy-filtered mirror/search, restore guard, and `.gitignore` protection.
- Python compile passes.
- Model/unit smoke passes without DB.
- DB-backed safety tests pass against a disposable local database:
  - reader cannot read forbidden privacy classes
  - audit log rejects update/delete
  - `supersede` rejects non-shared records
  - restore drill refuses production/same-host+dbname targets
  - mirror omits `personal_stanislav` and `external_forbidden`
- Dry-run markdown import still works without DB.
- Synology package contains bind-host and migration files.
- Second-pass review finds no blocker that would expose data outside LAN/Tailscale.

## Phase 1 — Disposable Local DB Pilot

Objective: prove workflows locally before touching Synology.

Tasks:

- Start local Postgres/pgvector using root `docker-compose.yml`.
- Apply migration to local disposable DB.
- Apply both `001_initial_schema.sql` and `002_hardening.sql`; do not rely only on Docker first-boot init scripts for already-initialized databases.
- Create candidate smoke record.
- Promote one smoke candidate.
- Reject one smoke candidate.
- Supersede one shared smoke record.
- Verify `list_candidates`, `search_memory`, `get_with_audit`.
- Export markdown mirror with privacy allowlist.
- Create backup.
- Restore into a disposable drill DB.
- Verify restore count and audit chain.

Acceptance:

- Candidate -> shared -> superseded audit chain is correct.
- Rejected candidates do not appear in canon.
- `personal_stanislav` and `external_forbidden` do not appear in markdown mirror.
- Restore drill refuses to run against production URL.
- Restore drill passes against disposable URL.

## Phase 2 — Synology Deployment Preparation

Objective: prepare NAS deployment without changing NAS yet.

Tasks:

- Choose endpoint mode:
  - preferred: Tailscale-only bind
  - fallback: LAN IP bind `192.168.68.103`
- Generate a strong DB password outside git.
- Build Synology deploy package.
- Prepare copy checklist for `/volume1/docker/openclaw-shared-memory/`.
- Prepare Synology Container Manager steps.
- Prepare Synology firewall/allowlist proposal if needed.
- Prepare rollback checklist.
- Prefer Tailscale-only endpoint unless LAN plaintext is explicitly accepted.
- Prepare TLS/`sslmode=require` option if LAN IP endpoint is used.

Acceptance:

- No secrets stored in git.
- Package is self-contained.
- Runbook includes exact start, smoke, backup, restore, rollback steps.
- Runbook does not put passwords directly into shell command arguments.
- Owner approves Synology Docker/Container Manager changes before execution.

## Phase 3 — Synology Pilot Deployment

Objective: deploy on NAS as a private pilot, still not used by OpenClaw runtime.

Tasks:

- Copy deployment package to Synology.
- Create `.env` with strong password.
- Start container.
- Confirm Postgres health.
- Confirm pgvector extension.
- Confirm access only from approved LAN/Tailscale clients.
- Run smoke workflow from OpenClaw Home.
- Run backup and restore drill.
- Record evidence in project docs.

Acceptance:

- DB is not reachable from public internet.
- DB is reachable only from approved local/Tailscale clients.
- Smoke workflow passes.
- Backup and restore drill pass.
- No real memory imported yet.

## Phase 4 — Read-Only MCP Retrieval Pilot

Objective: let OpenClaw read from canon without depending on it.

Tasks:

- Implement real MCP server wrapper or OpenClaw tool adapter.
- Expose read-only tools first:
  - `search_memory`
  - `get_with_audit`
  - `list_candidates` for review only
- Enforce caller identity and privacy classes.
- Configure OpenClaw Home in a non-critical path.
- Add fallback to markdown files if MCP read fails.
- Log access without storing secrets.

Acceptance:

- OpenClaw can retrieve one smoke shared record.
- Failed MCP read does not break normal agent operation.
- Privacy filters are demonstrated.
- Runtime config change is separately approved and recorded.

## Phase 5 — Controlled Write Pilot

Objective: allow proposal writes, but keep promotion manual.

Tasks:

- Enable `propose_memory` for trusted direct agents.
- Keep `promote_to_shared`, `supersede`, `reject_candidate`, and `archive_record` human-approved.
- Import a small owner-approved subset of `DECISIONS.md` and `STATE.md` as candidates.
- Manually promote 1-3 low-risk records.
- Compare retrieval quality against markdown.
- Monitor duplicates and stale state.

Acceptance:

- New candidates include source, actor, confidence, privacy, scope, and reason.
- No automatic shared promotion occurs.
- Owner can review candidate queue.
- Existing markdown remains authoritative until explicit migration approval.

## Phase 6 — Migration Decision

Objective: decide whether shared canon becomes operational source for durable memory.

Tasks:

- Review pilot evidence.
- Review privacy/audit logs.
- Review restore drill history.
- Decide source-of-truth split:
  - shared canon for durable approved records
  - markdown mirror for bootstrap/recovery
  - daily logs for raw narrative
  - private SQLite/notebooks for agent-local notes
- Update `STATE.md` and `DECISIONS.md` only after owner approval.

Acceptance:

- Owner explicitly approves or rejects migration.
- If approved, record decision and update agent instructions.
- If rejected, keep project as experimental/inert.

## Human Approval Gates

- Deploying to Synology.
- Changing Synology firewall, shares, permissions, snapshots, scheduled tasks, or Docker projects.
- Adding runtime MCP config to OpenClaw.
- Importing existing memory.
- Promoting records to shared canon.
- Exporting or sending any memory outside LAN/Tailscale.
- Deleting or purging any database data.

## First Implementation Batch

Implement Phase 0 only:

1. Additive `002_hardening.sql` with roles, grants, RLS, audit immutability, `content_hash`, and `current_shared_canon`.
2. Config/repository wiring for least-privilege read/write/promote/backup roles.
3. Repository workflow fixes: reject/archive/list candidates, supersede status guard, idempotent proposals.
4. Privacy-filtered mirror/search/get/list.
5. Safer restore drill with sha256 and same-host+dbname guard.
6. Synology bind-host packaging.
7. Encrypted backup option.
8. Updated validation and DB-backed safety tests.

Stop before Phase 1 until reviewed.

## Claude Audit Result

Audit artifact:

`/home/stanislav/agent-runs/2026-07-22-openclaw-shared-memory-plan-audit/logs/claude-plan-audit.json`

Verdict:

- Go to begin Phase 0 implementation.
- No-go on declaring Phase 0 complete under the original acceptance criteria.

Required changes from audit:

- Least-privilege DB roles must be used by app connections, not merely created.
- Hardening must be additive as `002_hardening.sql`.
- Privacy must be enforced at DB/RLS layer and in Python.
- Backup encryption must be implemented or removed from the architecture claim.
- `validate_schema.py` must validate hardening controls, not only existing scaffold snippets.
- Phase 0 exit must include DB-backed safety tests.
