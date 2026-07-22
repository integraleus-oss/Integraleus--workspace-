# Synology Deployment Profile

Target: Synology NAS on the home LAN.

This profile is for running the OpenClaw shared memory Postgres/pgvector store on Synology so local PCs and OpenClaw nodes can connect over the LAN.

## Why Synology

- Stable home-network host.
- Shared LAN endpoint for multiple local PCs.
- Data stays inside the home network.
- Backups can stay on NAS storage.
- OpenClaw Home and local machines can use one canonical memory database.

## Security Boundary

- Do not expose this database to the public internet.
- Bind to the LAN only, preferably Synology firewall allowlist for trusted LAN/Tailscale hosts.
- Use a strong password in `.env`; do not commit it.
- Do not import Synology file contents into memory canon unless Stanislav explicitly approves that source.
- Root-level Synology changes require explicit approval before execution.

## Expected Paths

Recommended Synology share layout:

```text
/volume1/docker/openclaw-shared-memory/
  docker-compose.yml
  .env
  migrations/
  data/
  backups/
  mirror/
```

If using Container Manager, create a Project from this folder.

## LAN Endpoint

Default compose mapping:

```text
192.168.68.103:55432 -> postgres:5432
```

Connection string example:

```text
postgresql://openclaw_memory:<password>@192.168.68.103:55432/openclaw_memory
```

## First Run

1. Build a self-contained deploy package with `scripts/package_synology_deploy.sh`.
2. Copy the package contents to Synology as `/volume1/docker/openclaw-shared-memory/`.
3. Rename `.env.synology.example` to `.env` and set a strong password.
4. Start the stack with Synology Container Manager or `docker compose up -d`.
5. Check health.
6. From OpenClaw Home, run a read-only connection check.
7. Apply migration manually only if it was not applied by first boot.
8. Run candidate/shared/mirror/backup/restore drill.

## Not Done Automatically

This profile does not configure Synology firewall, users, DSM permissions, snapshots, or scheduled tasks. Those are NAS-level changes and should be approved separately.
