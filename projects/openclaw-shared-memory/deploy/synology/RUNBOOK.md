# Synology Runbook

## Preflight

- Confirm explicit approval for NAS-level changes.
- Confirm Synology Docker or Container Manager is available.
- Confirm target path and share permissions.
- Confirm the database must stay LAN/Tailscale-only.
- Generate a strong database password outside git.

## Deploy

Create the package locally:

```bash
scripts/package_synology_deploy.sh
```

Copy the generated package contents from `dist/synology-openclaw-shared-memory/` to:

```text
/volume1/docker/openclaw-shared-memory
```

On Synology:

```bash
cd /volume1/docker/openclaw-shared-memory
cp .env.synology.example .env
# edit .env and set POSTGRES_PASSWORD before start
docker compose --env-file .env up -d
docker compose ps
```

Expected:

- container: `openclaw-shared-memory-postgres`
- health: `healthy`
- port: `55432`

## OpenClaw Home Connection Check

From OpenClaw Home:

```bash
psql "postgresql://openclaw_memory:<password>@192.168.68.103:55432/openclaw_memory" -c "select version();"
psql "postgresql://openclaw_memory:<password>@192.168.68.103:55432/openclaw_memory" -c "\\dt"
```

## Apply Migration Manually

If the migration did not run on first boot:

```bash
psql "postgresql://openclaw_memory:<password>@192.168.68.103:55432/openclaw_memory" \
  -f migrations/001_initial_schema.sql
```

## Smoke Test

From this project on OpenClaw Home:

```bash
export OPENCLAW_MEMORY_DATABASE_URL="postgresql://openclaw_memory:<password>@192.168.68.103:55432/openclaw_memory"
PYTHONPATH=src python3 -m openclaw_shared_memory.server propose_memory \
  --record-type decision \
  --title "Synology shared memory smoke" \
  --body "This is a candidate smoke record." \
  --privacy-class shared_safe \
  --source runbook \
  --created-by openclaw-main \
  --reason "Synology deployment smoke"
```

Promote only disposable smoke records during testing.

## Backup

```bash
OPENCLAW_MEMORY_DATABASE_URL="postgresql://openclaw_memory:<password>@192.168.68.103:55432/openclaw_memory" \
OPENCLAW_MEMORY_BACKUP_DIR="./backups" \
scripts/backup_memory.sh
```

## Restore Drill

Use a disposable database, not production:

```bash
OPENCLAW_MEMORY_DRILL_DATABASE_URL="postgresql://openclaw_memory:<password>@192.168.68.103:55432/openclaw_memory_drill" \
scripts/restore_drill.sh backups/openclaw-memory-YYYYMMDDTHHMMSS+0300.dump
```

## Rollback

For initial testing:

```bash
docker compose down
```

Do not delete `data/` unless Stanislav explicitly approves destructive cleanup.
