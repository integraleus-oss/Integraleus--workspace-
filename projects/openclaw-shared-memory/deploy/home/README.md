# OpenClaw Home Deployment Profile

Target: `openclaw-home` on the home LAN.

This profile runs the OpenClaw Shared Memory Postgres/pgvector pilot on
`openclaw-home` and binds it to LAN IP `192.168.68.125`.

## Boundary

- Local network only.
- Bind to `192.168.68.125`, never wildcard `0.0.0.0`.
- VPN may be enabled only as a private route into the home LAN.
- Real memory import is not approved.
- OpenClaw runtime/MCP wiring is not approved.
- Secrets stay outside git under `~/.local/share/openclaw-shared-memory/`.

## Runtime Paths

```text
~/.local/share/openclaw-shared-memory/
  .env
  data/
  backups/
  mirror/
  secrets/
```

## Start

From the project root:

```bash
docker compose --env-file ~/.local/share/openclaw-shared-memory/.env \
  -f deploy/home/docker-compose.home.yml up -d
```

## Stop

```bash
docker compose --env-file ~/.local/share/openclaw-shared-memory/.env \
  -f deploy/home/docker-compose.home.yml down
```

Do not delete `data/` without explicit approval.
