# Evidence: Phase 3 OpenClaw Home Pilot Deployment

Status: in progress
Date: 2026-07-23
Approval: Telegram topic `HOME:1751`, message at 2026-07-23 14:42 MSK

## Approved Scope

- Deploy OpenClaw Shared Memory pilot to `openclaw-home`.
- Bind Postgres to LAN IP `192.168.68.125`, port `55432`.
- Use strong local secrets outside git.
- Use disposable smoke records only.

## Explicitly Not Approved

- Synology package/runtime changes.
- WAN/public exposure.
- Wildcard bind `0.0.0.0`.
- OpenClaw runtime/MCP changes.
- Real memory import.
- External review/send.

## Files Created Or Changed

- `deploy/home/docker-compose.home.yml` - compose profile for `openclaw-home`.
- `deploy/home/README.md` - local deployment notes and boundaries.
- `docs/PHASE3_HOME_DEPLOY_EVIDENCE.md` - this evidence file.
- `TODO.md` - pending update after verification.

## Commands Run

```bash
hostname
ip -4 addr show
docker --version
docker compose version
ss -ltnp | grep :55432 || true
docker ps -a --filter name=openclaw-shared-memory-postgres --format '{{.Names}} {{.Status}} {{.Ports}}'
docker compose --env-file ~/.local/share/openclaw-shared-memory/.env -f deploy/home/docker-compose.home.yml up -d
docker inspect -f '{{.Name}} {{.State.Status}} {{.State.Health.Status}}' openclaw-shared-memory-home-postgres
ss -ltnp | grep :55432 || true
docker exec openclaw-shared-memory-home-postgres psql -U openclaw_memory -d openclaw_memory -At -c '<schema and role checks>'
<repository smoke with local secrets sourced from ~/.local/share/openclaw-shared-memory/>
scripts/export_markdown_mirror.py
scripts/backup_memory.sh
scripts/restore_drill.sh
ssh openclaw-admin@192.168.68.103 '<python tcp connect to 192.168.68.125:55432>'
sudo /usr/sbin/ufw status verbose
```

Result:

- Host is `openclaw-home`.
- LAN IP `192.168.68.125/24` exists on `eno1`.
- Tailscale IP `100.114.189.16/32` exists, but is not selected for bind.
- Docker is available.
- Port `55432` was free before deployment.
- Old local test container `openclaw-shared-memory-postgres` exists stopped and is not used by the home deployment profile.
- Runtime `.env` and role secret file were created outside git under `~/.local/share/openclaw-shared-memory/` with mode `0600`; runtime directories are mode `0700`.
- Compose project started container `openclaw-shared-memory-home-postgres`.
- Container is `running healthy`.
- Bind is `192.168.68.125:55432`, not wildcard.
- UFW allows LAN sources; read-only status check showed no new firewall rule was needed.
- Synology was able to open a TCP connection to `192.168.68.125:55432`, confirming LAN reachability.
- Schema exists: `memory_records`, `memory_embeddings`, `memory_audit_log`.
- LOGIN role attributes verified:
  - `ocsm_home_backup:true`
  - `ocsm_home_promoter:false`
  - `ocsm_home_reader:false`
  - `ocsm_home_writer:false`
- Repository smoke passed: propose, promote, audit retrieval, privacy denial, direct reader/write denial, direct writer/update denial, and backup visibility of a forbidden smoke record.
- Mirror export wrote 1 `shared_safe` row; forbidden smoke content did not appear in plaintext mirror.
- Test-only plaintext backup passed.
- Restore drill passed against disposable DB `openclaw_memory_home_drill`.
- `restore_drill.sh` initially printed a full drill URL containing credentials; the local pilot admin password was rotated immediately and the script was patched to redact URLs in future output. A follow-up restore drill confirmed redacted output.
- Current smoke DB contents are disposable only: one `shared_safe` smoke record and one `external_forbidden` smoke record.

## Checks

- [x] runtime `.env` created outside git
- [x] compose project started
- [x] container healthy
- [x] bind verified as `192.168.68.125:55432`, not wildcard
- [x] schema present
- [x] LOGIN roles provisioned with strong local passwords
- [x] backup LOGIN has `BYPASSRLS`, other app LOGIN roles do not
- [x] role-scoped smoke passed
- [x] mirror allowlist passed
- [x] backup passed
- [x] restore drill passed against disposable DB
- [x] OpenClaw runtime/MCP unchanged
- [x] no real memory import

## Residual Risks

- The DB pilot is now running on `openclaw-home` and reachable from LAN clients.
- OpenClaw runtime/MCP is not connected yet; markdown memory remains operational source.
- Test-only plaintext backup and mirror contain disposable smoke data only. Real-data backups must be encrypted before any real memory import.
- A stopped older local test container named `openclaw-shared-memory-postgres` remains from prior local checks and is not part of this pilot.

## Handoff

- DB pilot is running. Do not proceed to MCP/runtime wiring without separate approval.
