# OpenClaw Shared Memory Implementation Plan v2

Status: ready for Phase 0 implementation
Date: 2026-07-22
Supersedes: `docs/IMPLEMENTATION_PLAN.md`

## Purpose

Build a shared memory canon for OpenClaw agents that is useful, auditable, and private by default.

The intended production-like placement is Synology NAS on the home network. OpenClaw Home will be the controlled MCP/API gateway. Existing markdown memory remains authoritative until an explicitly approved migration decision.

## Hard Boundaries

- Database is never exposed to the public internet.
- Synology deployment is LAN/Tailscale-only.
- Synology root-level, Docker, firewall, share, permission, snapshot, or scheduled-task changes require explicit owner approval.
- Existing markdown memory and private agent notebooks are not imported automatically.
- `promote_to_shared`, `supersede`, `reject_candidate`, and `archive_record` remain human-approved until a later explicit policy changes that.
- `personal_stanislav` and `external_forbidden` records must not be exported into plaintext markdown mirror.
- Backups containing real memory must be encrypted.
- No OpenClaw runtime dependency on shared memory until read-only pilot passes.

## Target Shape

```text
Trusted local clients
  - OpenClaw Home
  - selected local PCs
  - future local agents
        |
        | Tailscale preferred; LAN fallback only with explicit acceptance
        v
OpenClaw Home MCP/API gateway
  - caller identity
  - privacy policy
  - audit-aware retrieval
        |
        | least-privilege DB roles
        v
Synology Postgres + pgvector
  - canonical records
  - embeddings
  - append-only audit
  - encrypted backups
  - privacy-filtered markdown mirror
```

## Required Visualizations

Control artifact:

`docs/VISUAL_ARCHITECTURE.html`

The visualization is part of the safety evidence, not decorative documentation. It must show:

- knowledge-base ownership and storage layers;
- agent-local notes versus shared canon;
- `propose_memory` candidate path;
- human review and promotion gate;
- reject/archive/supersede paths;
- read path through caller identity and privacy policy;
- Postgres/pgvector on Synology as LAN/Tailscale-only store;
- least-privilege DB roles and RLS boundary;
- append-only audit log;
- markdown mirror with privacy allowlist;
- encrypted backup and restore-drill path;
- blocked flows:
  - public internet exposure;
  - silent promotion;
  - direct uncontrolled DB writes;
  - forbidden privacy classes entering plaintext mirror/cloud sync.

The diagram must be updated in the same change when the architecture, trust boundary, storage location, or memory lifecycle changes.

## Phase 0 — Local Hardening Only

Do not start Synology deployment in this phase.

### Objective

Turn the scaffold into a testable, safety-gated implementation that cannot pass validation while obvious privacy controls are missing.

### Required Changes

1. Add `migrations/002_hardening.sql`.
   - Add DB roles: `memory_migrator`, `memory_reader`, `memory_writer`, `memory_promoter`, `memory_backup`.
   - Add explicit grants and revokes.
   - Add RLS policy foundations for `memory_records`.
   - Add audit immutability protection.
   - Add `content_hash`.
   - Add `current_shared_canon` view.
   - Add consistency checks for supersession chains.

2. Make application connections role-aware.
   - Replace the single effective connection setting with per-operation URLs:
     - `OPENCLAW_MEMORY_READER_DATABASE_URL`
     - `OPENCLAW_MEMORY_WRITER_DATABASE_URL`
     - `OPENCLAW_MEMORY_PROMOTER_DATABASE_URL`
     - `OPENCLAW_MEMORY_BACKUP_DATABASE_URL`
     - keep `OPENCLAW_MEMORY_DATABASE_URL` only as local-dev fallback.
   - Reads must use reader role.
   - Proposals must use writer role.
   - Promote/reject/archive/supersede must use promoter role.

3. Fix workflow completeness.
   - Add `reject_candidate`.
   - Add `archive_record`.
   - Add `list_candidates`.
   - Restrict `supersede` to `shared` records with no `superseded_by_id`.
   - Make `propose_memory` idempotent using `content_hash`.

4. Enforce privacy in code and DB.
   - `search_memory` must never use raw `SELECT *`.
   - `search_memory`, `get_with_audit`, and `list_candidates` must accept caller/privacy policy.
   - Default reader policy must deny `personal_stanislav` and `external_forbidden`.
   - DB RLS must backstop Python checks.
   - Semantic search through embeddings is deferred until a later phase; Phase 0 and Phase 1 retrieval are lexical/privacy-policy tests only.

5. Harden mirror and backup.
   - Markdown mirror exports only allowlisted privacy classes.
   - Default mirror allowlist: `shared_safe`, `project`.
   - Mirror must fail closed if a forbidden class would be exported.
   - Add encrypted backup option before any real memory backup.
   - Keep unencrypted backup only for disposable local smoke data.

6. Harden restore drill.
   - Require sha256 sidecar and verify it before restore.
   - Refuse restore if drill target matches production URL.
   - Refuse restore if drill target resolves to same host plus same database name.
   - Keep `pg_restore --clean` only for disposable drill DBs.

7. Harden Synology package without deploying it.
   - Add `OPENCLAW_MEMORY_BIND_HOST`.
   - Compose port must be `${OPENCLAW_MEMORY_BIND_HOST}:${OPENCLAW_MEMORY_PORT}:5432`.
   - Recommended bind host is Tailscale IP; LAN IP is fallback.
   - Runbook must avoid passwords in shell command arguments.
   - Runbook must state that DSM firewall alone is not the Docker port boundary.

8. Upgrade validation.
   - `scripts/validate_schema.py` must assert the presence of Phase 0 controls.
   - Add DB-backed safety test script for disposable DB.
   - Keep no-DB smoke tests for model/config/import dry-run.

### Phase 0 Evidence

Required files:

- `migrations/002_hardening.sql`
- `docs/VISUAL_ARCHITECTURE.html`
- updated `src/openclaw_shared_memory/config.py`
- updated `src/openclaw_shared_memory/repository.py`
- updated `src/openclaw_shared_memory/server.py`
- updated `scripts/export_markdown_mirror.py`
- updated `scripts/backup_memory.sh`
- updated `scripts/restore_drill.sh`
- updated `scripts/validate_schema.py`
- new DB-backed safety test script
- updated Synology deploy profile
- updated runbooks

Required checks:

```bash
python3 scripts/validate_schema.py
python3 -m compileall -q src scripts
PYTHONPATH=src python3 scripts/import_markdown_candidates.py --record-type decision ../../DECISIONS.md
```

DB-backed checks against disposable local DB:

- reader role cannot read denied privacy classes.
- writer role cannot promote.
- reader role cannot write.
- writer and promoter roles cannot bypass denied privacy classes through RLS.
- audit log rejects update/delete for reader, writer, and promoter roles.
- `supersede` rejects candidate/rejected/superseded records.
- `search_memory` does not return forbidden classes under default reader policy.
- `get_with_audit` and `list_candidates` deny forbidden privacy classes under default reader policy.
- mirror export omits forbidden classes and fails closed if a forbidden class would be exported by misconfiguration.
- real-data backup refuses to run unencrypted.
- duplicate `propose_memory` calls with the same canonical content return one record through `content_hash` idempotency.
- restore drill refuses same production target.

### Phase 0 Exit Gate

Phase 0 is complete only when:

- all Phase 0 files exist;
- all no-DB checks pass;
- all DB-backed safety checks pass against disposable DB;
- Synology package binds to explicit host;
- visual architecture shows trust zones, write path, read path, mirror, backup, and blocked public/uncontrolled paths;
- visual architecture matches the actual hardening implementation;
- `.gitignore` protects `.env`, dumps, checksums, generated mirror markdown, and package build output;
- no real memory was imported;
- no Synology changes were made;
- a second-pass review reports no blocker.

## Phase 1 — Disposable Local DB Pilot

Do not touch Synology in this phase.

### Objective

Prove the complete lifecycle locally using disposable smoke data.

### Tasks

- Start local Postgres/pgvector.
- Apply `001_initial_schema.sql`.
- Apply `002_hardening.sql` explicitly.
- Create smoke candidates for multiple privacy classes.
- Promote one `shared_safe` record.
- Reject one candidate.
- Supersede one shared record.
- Verify audit chain for every transition.
- Run search/get/list under reader policy.
- Export markdown mirror.
- Create unencrypted disposable backup.
- Run restore drill into disposable DB.
- Record evidence.

### Exit Gate

- Lifecycle smoke passes.
- Privacy checks pass.
- Mirror contains only allowed classes.
- Restore drill passes into disposable DB.
- Restore drill refuses production-like target.
- Local DB can be destroyed without losing any real data.

## Phase 2 — Synology Deployment Preparation

No NAS state changes until explicit approval.

### Objective

Prepare a self-contained, reviewed NAS deployment package.

### Tasks

- Choose endpoint mode:
  - preferred: Tailscale-only bind;
  - fallback: LAN IP `192.168.68.103` only if explicitly accepted.
- Prepare `.env` template with no secrets.
- Generate password outside git after approval.
- Build package.
- Verify package contains migrations, compose, runbook, checklist.
- Prepare rollback instructions.
- Prepare NAS approval request with exact actions.

### Exit Gate

- Package is self-contained.
- No secrets in git.
- Runbook avoids password-in-argv examples.
- Owner approval request is specific enough to approve or reject.

## Phase 3 — Synology Pilot Deployment

Requires explicit owner approval.

### Objective

Run the hardened shared-memory DB on Synology as a private pilot, not yet part of OpenClaw runtime.

### Tasks

- Copy deploy package to approved Synology path.
- Create `.env` on Synology with strong password.
- Start container.
- Verify Postgres health and pgvector.
- Verify binding is only Tailscale or explicit LAN IP.
- Verify no public reachability.
- Run smoke workflow from OpenClaw Home using direct role-scoped DB access. The MCP/API gateway boundary becomes real in Phase 4.
- Run encrypted backup.
- Run restore drill against disposable DB.
- Record evidence.

### Exit Gate

- Container healthy.
- Access limited to approved local/Tailscale clients.
- Smoke lifecycle passes.
- Encrypted backup produced.
- Restore drill passes.
- No real memory imported.

## Phase 4 — Read-Only MCP Pilot

Requires explicit approval for OpenClaw runtime config changes.

### Objective

Allow OpenClaw to read shared canon without depending on it.

### Tasks

- Build MCP/API adapter.
- Expose read-only tools:
  - `search_memory`
  - `get_with_audit`
  - `list_candidates`
- Enforce caller identity and privacy policy.
- Add markdown fallback on read failure.
- Log access without secrets.
- Test with smoke records only.

### Exit Gate

- Read-only retrieval works.
- Failure does not break normal OpenClaw operation.
- Privacy policy is demonstrated.
- Runtime config change is documented and approved.

## Phase 5 — Controlled Write Pilot

Requires explicit approval.

### Objective

Allow proposal writes while keeping canon changes human-approved.

### Tasks

- Enable `propose_memory` for trusted direct agents.
- Import a small approved subset from markdown as candidates.
- Review candidate queue.
- Promote 1-3 low-risk records manually.
- Compare retrieval with markdown source.
- Monitor duplicate and stale records.

### Exit Gate

- Proposals include source, actor, reason, confidence, scope, and privacy class.
- No automatic promotion occurs.
- Candidate review is usable.
- Markdown remains authoritative.

## Phase 6 — Migration Decision

Requires explicit owner approval.

### Objective

Decide whether the shared canon becomes the durable memory source of truth.

### Tasks

- Review pilot evidence.
- Review audit logs.
- Review privacy controls.
- Review backup/restore evidence.
- Decide source split:
  - DB canon for approved durable records;
  - markdown mirror for bootstrap and recovery;
  - daily logs for raw session notes;
  - local notebooks for private agent memory.
- Update `STATE.md` and `DECISIONS.md` only after approval.

### Exit Gate

- Owner approves migration, or project remains experimental/inert.

## Explicit Human Approval Gates

- Deploying anything to Synology.
- Changing Synology Docker/Container Manager.
- Changing Synology firewall, shares, users, permissions, snapshots, scheduled tasks, or services.
- Adding OpenClaw MCP/runtime config.
- Importing existing memory.
- Promoting, superseding, rejecting, or archiving real records.
- Exporting memory outside LAN/Tailscale.
- Deleting/purging DB data.
- Treating DB canon as authoritative.

## Immediate Next Work Package

Only Phase 0 should be implemented next.

Deliverable:

- one hardening patch;
- one updated validation suite;
- one disposable-DB safety test script;
- one regenerated Synology package;
- one evidence note.

Stop after Phase 0 evidence. Do not start a DB pilot, Synology deployment, or runtime wiring in the same work package.
