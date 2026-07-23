# Synology Rollback

Status: prepared, not executed
Date: 2026-07-23

## Scope

This rollback applies only to the Synology pilot package for OpenClaw Shared
Memory. It is for Phase 3 after explicit deployment approval. It must not be
run during Phase 2 preparation.

## Stop Service

From the approved Synology deployment directory:

```bash
cd /volume1/docker/openclaw-shared-memory
docker compose --env-file .env down
```

Expected:

- `openclaw-shared-memory-postgres` stops.
- Port `55432` no longer accepts connections on the approved bind address.
- Existing `data/`, `backups/`, and `mirror/` directories remain in place.

## Verify From OpenClaw Home

```bash
pg_isready -d "postgresql://openclaw_memory@<approved-host>:55432/openclaw_memory"
```

Expected:

- the connection check fails after the container is stopped.

## Preserve Evidence

Keep these artifacts unless Stanislav explicitly approves cleanup:

- `.env` on Synology;
- `data/`;
- `backups/`;
- `mirror/`;
- deployment logs or screenshots collected during the pilot.

## Destructive Cleanup

Do not remove deployment files or data directories unless Stanislav explicitly
approves the exact cleanup action.

Potential cleanup commands after explicit approval only:

```bash
cd /volume1/docker/openclaw-shared-memory
docker compose --env-file .env down
# Explicit approval required before any rm/trash/delete operation below.
```

## Restore Service

If rollback was accidental or the pilot should resume:

```bash
cd /volume1/docker/openclaw-shared-memory
docker compose --env-file .env up -d
docker compose --env-file .env ps
```

Expected:

- container health becomes `healthy`;
- role-scoped connection checks pass again.
