# Phase 0 Hardening Evidence

Date: 2026-07-22
Scope: local hardening only for OpenClaw Shared Memory.

## Checklist

- [x] Baseline commit recorded
- [x] SQL hardening migration added
- [x] Role-scoped application config added
- [x] Repository/server workflows hardened
- [x] Mirror export privacy allowlist and fail-closed behavior added
- [x] Backup/restore scripts hardened
- [x] Synology package bind guard added
- [x] Static validator updated
- [x] Disposable DB safety tests added
- [x] No-DB smoke checks run
- [x] DB-backed safety checks run
- [x] Synology/runtime untouched
- [x] Git status recorded

## Boundaries

- No Synology SSH, DSM, Docker, firewall, share, user, package, cron, or service changes.
- No OpenClaw runtime config changes.
- No import of existing real memory into the shared canon.
- No promotion of real records.

## Results

- Baseline scaffold commit: `acccbae docs: add OpenClaw shared memory scaffold`.
- Added `migrations/002_hardening.sql` with:
  - `content_hash` active-record dedup key;
  - self-contained `pgcrypto` extension requirement;
  - role groups: reader, writer, promoter, backup, admin;
  - forced RLS policies for records, embeddings, and audit;
  - append-only audit trigger blocking update/delete/truncate;
  - `current_shared_canon` as a security-invoker view.
- Added role-scoped app settings:
  - `OPENCLAW_MEMORY_READER_DATABASE_URL`
  - `OPENCLAW_MEMORY_WRITER_DATABASE_URL`
  - `OPENCLAW_MEMORY_PROMOTER_DATABASE_URL`
  - `OPENCLAW_MEMORY_BACKUP_DATABASE_URL`
- Hardened repository/server:
  - idempotent `propose_memory` via `content_hash`;
  - `propose_memory` refuses privacy classes outside `project,shared_safe`;
  - `promote_to_shared` requires allowlisted actor and repeated privacy/scope/source/confidence confirmation;
  - added `reject_candidate`, `archive_record`, `list_candidates`;
  - `supersede` is blocked unless old record is `shared`;
  - `search_memory`, `get_with_audit`, and `list_candidates` default to `project,shared_safe` privacy allowlist.
- Hardened mirror:
  - default plaintext mirror allowlist is `shared_safe`;
  - export fails closed for every class except `shared_safe`, including `project`.
- Hardened backup/restore:
  - real-data backups require `OPENCLAW_MEMORY_BACKUP_AGE_RECIPIENT`;
  - restore drill requires checksum;
  - restore drill refuses same/prod URL;
  - restore target DB must include `drill`, `test`, or `scratch`.
- Hardened Synology package:
  - compose now requires `OPENCLAW_MEMORY_BIND_HOST`;
  - package script fails if explicit bind guard is missing;
  - Synology README/RUNBOOK avoid passwords in shell commands.
- Created `scripts/run_phase0_safety_tests.py`, a pytest-free DB-backed safety runner.
- Created `docs/HOME_KNOWLEDGE_BASE_TOPIC_AUDIT.md` as the Home KB topic audit requested before Phase 0.
- Started a local Docker Postgres only on `127.0.0.1:55432`, applied migrations to disposable DB `openclaw_memory_phase0`, ran checks, and stopped the container with `docker compose down`.
- Synology was not accessed or changed.
- OpenClaw runtime config was not changed.
- Existing real memory was not imported or promoted.

## Command Log

- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -q -e '.[dev]'`
- `.venv/bin/python scripts/validate_schema.py` -> `VALIDATION_OK`
- `.venv/bin/python -m compileall -q src scripts` -> OK
- `.venv/bin/python -m pytest -q` -> `2 passed in 0.01s`
- `scripts/package_synology_deploy.sh` -> `PACKAGE_OK .../dist/synology-openclaw-shared-memory`
- `docker compose up -d` -> local Postgres started
- Applied `migrations/001_initial_schema.sql` to `openclaw_memory_phase0` -> OK
- Applied `migrations/002_hardening.sql` to `openclaw_memory_phase0` -> OK
- `OPENCLAW_MEMORY_TEST_DATABASE_URL=...openclaw_memory_phase0 .venv/bin/python scripts/run_phase0_safety_tests.py` -> `PHASE0_DB_SAFETY_OK`
- DB safety runner coverage includes reader/write denial, writer/promote denial, forbidden app propose denial, non-allowlisted actor denial, get_with_audit forbidden denial, list_candidates privacy filtering, audit update/delete/truncate denial, idempotent propose, promotion confirmation mismatch, shared-only supersede, reject, archive, and search privacy filtering.
- CLI lifecycle smoke on disposable DB -> `CLI_LIFECYCLE_SMOKE_OK`
- `OPENCLAW_MEMORY_MIRROR_PRIVACY_CLASSES=external_forbidden .venv/bin/python scripts/export_markdown_mirror.py` refused export -> `MIRROR_GUARD_OK`
- `OPENCLAW_MEMORY_REAL_DATA=1 scripts/backup_memory.sh` refused plaintext real-data backup -> `BACKUP_GUARD_OK`
- Restore drill with same prod/drill URL refused -> `RESTORE_GUARD_OK`
- Test-only plaintext backup on disposable DB -> `BACKUP_OK plaintext-test-only`
- Restore drill to `openclaw_memory_phase0_drill` -> `RESTORE_DRILL_OK`, `records=6`
- Reran `migrations/002_hardening.sql` on the disposable DB -> `MIGRATION_002_RERUN_OK`
- `docker compose down` -> local test container stopped and removed
- `docker ps --format ... | rg 'openclaw-shared-memory|55432' || true` -> no running container
- Claude implementation review before commit:
  - output: `/home/stanislav/agent-runs/2026-07-22-openclaw-shared-memory-phase0-review/logs/claude-phase0-review.json`
  - verdict was `NO_GO` mainly because untracked security-critical files were absent from the review payload
  - actionable fixes applied before commit: mirror denies `project` plaintext export, restore checksum is basename-safe, `002_hardening.sql` constraint creation is rerunnable, repository advisory-lock calls cast UUIDs to text, DB safety runner now covers repository workflow guards
- Claude implementation review after commit:
  - output: `/home/stanislav/agent-runs/2026-07-22-openclaw-shared-memory-phase0-review/logs/claude-phase0-review-after-commit.json`
  - verdict was `GO` for local Phase 0
  - additional pre-Phase-1 fixes applied after the review: forced RLS, self-contained pgcrypto, audit truncate guard, writable privacy allowlist, distinct role URL examples, extended safety runner
- Current touched-path status before commit:
  - modified project files under `projects/openclaw-shared-memory/`
  - new `docs/HOME_KNOWLEDGE_BASE_TOPIC_AUDIT.md`
  - new `docs/PHASE0_HARDENING_EVIDENCE.md`
  - new `migrations/002_hardening.sql`
  - new `scripts/run_phase0_safety_tests.py`
  - unrelated pre-existing `state/knowledge-base-review-2026-06-21.md` remains untracked outside this project
