# Phase 3 Approval Request: Synology Pilot Deployment

Status: draft, not approved
Date: 2026-07-23

## Request

Approve or reject the Phase 3 Synology pilot deployment for OpenClaw Shared
Memory.

Nothing in this request has been executed on Synology. Phase 2 only prepared the
package and checks.

## Deployment Boundary

Approved target, if granted:

- Host: Synology NAS `192.168.68.103`
- Network boundary: local network only
- Preferred bind for this boundary: LAN IP `192.168.68.103`
- VPN use: allowed only as a private route into the home LAN, not as public exposure
- Tailscale-only bind: optional later hardening if Synology has a stable Tailscale IP and Stanislav explicitly selects it
- Path: `/volume1/docker/openclaw-shared-memory`
- Port: `55432`
- Public internet exposure: forbidden
- Real memory import: forbidden
- OpenClaw runtime/MCP config change: forbidden unless separately approved

## Required Human Choices

- [ ] Approve deployment: yes/no
- [x] Select network boundary: local network only, with VPN allowed only as a private route into the home LAN
- [ ] Confirm bind address: LAN `192.168.68.103`, unless Stanislav later selects a Synology Tailscale IP
- [ ] Approve target path: `/volume1/docker/openclaw-shared-memory`
- [ ] Confirm where generated passwords should be stored locally
- [ ] Confirm encrypted backup recipient for real data before any real-data backup

## Proposed Phase 3 Actions

After explicit approval only:

1. Copy the verified package from local `dist/synology-openclaw-shared-memory/`
   to Synology target path.
2. Create Synology `.env` from `.env.synology.example` locally on Synology.
3. Set:
   - `POSTGRES_PASSWORD`
   - `OPENCLAW_MEMORY_BIND_HOST`
   - `OPENCLAW_MEMORY_PORT`
   - mirror and backup directories
4. Start the compose project:

```bash
cd /volume1/docker/openclaw-shared-memory
docker compose --env-file .env up -d
docker compose --env-file .env ps
```

5. Apply migrations manually only if first boot did not apply them.
6. Provision distinct LOGIN roles:
   - reader: `NOBYPASSRLS`
   - writer: `NOBYPASSRLS`
   - promoter: `NOBYPASSRLS`
   - backup: `BYPASSRLS`
7. Verify role attributes with `pg_roles`.
8. Run smoke checks from OpenClaw Home:
   - read-only connection;
   - schema present;
   - disposable candidate lifecycle;
   - mirror allowlist;
   - encrypted backup if real data is involved;
   - restore drill against disposable DB.
9. Record evidence and stop before any MCP/runtime wiring.

## Explicitly Not Approved By This Request

- importing `MEMORY.md`, `STATE.md`, `DECISIONS.md`, daily notes, chats, or Synology file contents;
- exposing Postgres to WAN or wildcard `0.0.0.0`;
- treating "VPN enabled" as permission for public exposure;
- changing Synology users, DSM firewall, shares, scheduled tasks, packages, or root-level settings unless separately approved;
- changing OpenClaw runtime/MCP config;
- enabling agent writes to canon;
- sending raw data or review packets externally.

## Rollback

Prepared rollback artifact:

- `deploy/synology/ROLLBACK.md`

Minimum rollback:

```bash
cd /volume1/docker/openclaw-shared-memory
docker compose --env-file .env down
```

Do not delete `data/`, `backups/`, `mirror/`, `.env`, logs, or package files
without a separate explicit cleanup approval.

## Approval Record

- Decision: pending
- Approver: Stanislav
- Channel/message: pending
- Timestamp: pending
