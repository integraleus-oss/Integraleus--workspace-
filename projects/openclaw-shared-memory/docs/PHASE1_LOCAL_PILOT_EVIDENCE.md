# Phase 1 Local Pilot Evidence

Date: 2026-07-22
Scope: disposable local DB pilot with distinct role-scoped login users.

## Checklist

- [x] Phase 0 commit recorded
- [x] Disposable local DB created
- [x] Distinct login users provisioned for reader/writer/promoter/backup
- [x] Repository configured with distinct role-scoped DB URLs
- [x] Writer can propose candidate and idempotent duplicate returns existing
- [x] Writer cannot promote/update/archive/reject
- [x] Reader can search/get allowed records
- [x] Reader cannot write
- [x] Promoter can promote/reject/supersede/archive with actor gate and confirmation checks
- [x] Forbidden/private classes remain denied through repository reads
- [x] Markdown mirror exports only `shared_safe`
- [x] Test-only backup and restore drill succeed
- [x] Real-data plaintext backup is refused
- [x] Restore-to-prod/same-target is refused
- [x] Local container stopped
- [x] Synology/runtime/real memory untouched
- [x] Claude review completed
- [x] Git status recorded

## Boundaries

- No Synology access or changes.
- No OpenClaw runtime config changes.
- No import of existing real memory.
- No promotion of real memory records.
- Test credentials are disposable local DB users only.

## Results

- Phase 0 base before Phase 1: `8f68760 feat: harden shared memory phase 0`.
- Added `scripts/run_phase1_local_pilot.py`.
- Phase 1 pilot provisions distinct disposable login users:
  - `ocsm_phase1_reader`
  - `ocsm_phase1_writer`
  - `ocsm_phase1_promoter`
  - `ocsm_phase1_backup`
- Repository is configured with distinct DB URLs for reader/writer/promoter/backup.
- Pilot verified:
  - writer can `propose_memory`;
  - duplicate proposal returns the existing row with `idempotent=true`;
  - reader cannot insert;
  - writer cannot directly update/promote;
  - app refuses forbidden/private propose;
  - non-allowlisted actor cannot promote;
  - promote confirmation mismatch fails;
  - promoter can promote, supersede, reject, archive;
  - `get_with_audit` denies a forbidden record id;
  - `search_memory` and `list_candidates` return only `project/shared_safe`;
  - backup login can see forbidden records for recovery.
- Phase 1 provisioning grants `BYPASSRLS` to the actual disposable backup login; `002_hardening.sql` documents that this must happen during credential provisioning because BYPASSRLS is not inherited from a NOLOGIN group role.
- Markdown mirror exported only `shared_safe` rows to `/tmp/openclaw_phase1_mirror`.
- Backup ran through `ocsm_phase1_backup` and restore drill loaded `5` records into `openclaw_memory_phase1_drill`.
- Real-data plaintext backup guard refused as expected.
- Same prod/drill restore guard refused as expected.
- Local Docker container was stopped with `docker compose down`.
- Synology was not accessed or changed.
- OpenClaw runtime config was not changed.
- Existing real memory was not imported or promoted.

## Command Log

- `docker compose up -d` -> local Postgres started on loopback compose config.
- Created disposable DB `openclaw_memory_phase1`.
- Applied `migrations/001_initial_schema.sql` -> OK.
- Applied `migrations/002_hardening.sql` -> OK.
- `OPENCLAW_MEMORY_PHASE1_ADMIN_DATABASE_URL=...openclaw_memory_phase1 .venv/bin/python scripts/run_phase1_local_pilot.py` -> `PHASE1_LOCAL_PILOT_OK`.
- `OPENCLAW_MEMORY_DATABASE_URL=...openclaw_memory_phase1 OPENCLAW_MEMORY_MIRROR_DIR=/tmp/openclaw_phase1_mirror OPENCLAW_MEMORY_MIRROR_PRIVACY_CLASSES=shared_safe .venv/bin/python scripts/export_markdown_mirror.py` -> `EXPORT_OK rows=2`.
- Mirror privacy grep for `external_forbidden|personal_stanislav|project` -> `MIRROR_PHASE1_OK`.
- `OPENCLAW_MEMORY_BACKUP_DATABASE_URL=postgresql://ocsm_phase1_backup:...@127.0.0.1:55432/openclaw_memory_phase1 scripts/backup_memory.sh` -> `BACKUP_OK plaintext-test-only`.
- Restore drill to `openclaw_memory_phase1_drill` -> `RESTORE_DRILL_OK`, `records=5`.
- `OPENCLAW_MEMORY_REAL_DATA=1 scripts/backup_memory.sh` -> refused plaintext real-data backup, `BACKUP_GUARD_OK`.
- Restore drill with same prod/drill URL -> refused, `RESTORE_GUARD_OK`.
- `.venv/bin/python scripts/validate_schema.py` -> `VALIDATION_OK`.
- `.venv/bin/python -m compileall -q src scripts` -> OK.
- `.venv/bin/python -m pytest -q` -> `2 passed in 0.01s`.
- `scripts/package_synology_deploy.sh` -> `PACKAGE_OK`.
- Reran `migrations/002_hardening.sql` on disposable DB -> `MIGRATION_002_RERUN_OK`.
- `docker compose down` -> local test container stopped and removed.
- `docker ps --format ... | rg 'openclaw-shared-memory|55432' || true` -> no running container.
- Phase 1 files are committed after Claude review and follow-up tightening.
- Claude review:
  - output: `/home/stanislav/agent-runs/2026-07-22-openclaw-shared-memory-phase1-review/logs/claude-phase1-review.json`
  - verdict: `GO`
  - follow-up tightened before final amend: removed misleading `BYPASSRLS` from the NOLOGIN backup group role and documented that the actual backup LOGIN role must receive it during provisioning.
