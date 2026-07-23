# Evidence: Phase 4 Runtime Read-Only MCP/API Wiring

Status: ready, pending fresh-turn tool availability check
Date: 2026-07-23
Approval: Telegram topic `HOME:1751`, message at 2026-07-23 17:36 MSK

## Approved Scope

- Wire a read-only OpenClaw runtime/MCP/API path to the `openclaw-home`
  shared-memory DB pilot.
- Expose only:
  - `search_memory`
  - `get_with_audit`
  - `list_candidates`
- Use the reader-only DB role.
- Keep existing markdown memory as operational fallback.
- Use smoke records only.

## Explicitly Not Approved

- write tools;
- candidate proposal through runtime;
- promotion/rejection/archive/supersede through runtime;
- real memory import;
- replacing markdown memory as operational source;
- Synology runtime/package changes;
- WAN/public exposure;
- destructive DB changes.

## Checklist

- [x] Inspect OpenClaw runtime/tool registration source of truth
- [x] Add read-only adapter without exposing write methods
- [x] Configure runtime secrets outside git
- [x] Validate DB health and reader-only preflight
- [x] Validate runtime/tool smoke
- [x] Validate fallback/no-hard-dependency behavior
- [x] Confirm no real memory import
- [x] Confirm no write tools exposed
- [x] Record rollback path
- [x] Commit project/runtime evidence

## Commands And Evidence

### Baseline

```bash
openclaw status --deep
openclaw mcp list --json
```

Result:

- Gateway reachable on loopback.
- `mcp.servers` was empty before registration.
- DB pilot container stayed healthy on `192.168.68.125:55432`.

### Manual MCP Server Smoke

```bash
set -a
source ~/.local/share/openclaw-shared-memory/.env
source ~/.local/share/openclaw-shared-memory/secrets/roles.env
set +a
cd projects/openclaw-shared-memory
.venv/bin/python scripts/mcp_readonly_server.py
```

Result:

- `initialize` returned server `openclaw-shared-memory-readonly`.
- `tools/list` returned only:
  - `search_memory`
  - `get_with_audit`
  - `list_candidates`
- `tools/call search_memory` returned one disposable smoke record.

### OpenClaw Runtime Registration

```bash
openclaw mcp add openclaw-shared-memory-readonly \
  --command bash \
  --arg -lc \
  --arg 'set -a; source ~/.local/share/openclaw-shared-memory/.env; source ~/.local/share/openclaw-shared-memory/secrets/roles.env; set +a; exec .venv/bin/python scripts/mcp_readonly_server.py' \
  --cwd /home/stanislav/.openclaw/workspace/agents/main/projects/openclaw-shared-memory \
  --include search_memory,get_with_audit,list_candidates \
  --timeout 10 \
  --connect-timeout 10
openclaw mcp reload
openclaw mcp probe openclaw-shared-memory-readonly --json
openclaw config validate
```

Result:

- Saved MCP server `openclaw-shared-memory-readonly` to
  `/home/stanislav/.openclaw/openclaw.json`.
- Runtime command sources local secrets from
  `~/.local/share/openclaw-shared-memory/`; passwords are not stored in
  project files.
- Probe showed only three effective provider-safe tools:
  - `openclaw-shared-memory-readonl__get_with_audit`
  - `openclaw-shared-memory-readonl__list_candidates`
  - `openclaw-shared-memory-readonl__search_memory`
- `openclaw config validate` passed.
- No Gateway restart was performed; `openclaw mcp reload` disposed cached MCP
  runtimes for the next runtime build.

### Configured Server Smoke

The saved `openclaw.json` server command was launched and called through the
same JSON-RPC stdio protocol.

Result:

```text
PHASE4_CONFIGURED_MCP_SMOKE_OK tools=search_memory,get_with_audit,list_candidates count=1
```

### Fallback Behavior

The MCP server returns a tool error instructing the caller to use the existing
markdown memory fallback if DB reads fail. Current markdown memory tooling was
not removed or replaced.

## Rollback

Disable or remove the MCP server:

```bash
openclaw mcp unset openclaw-shared-memory-readonly
openclaw mcp reload
```

Do not delete DB data during rollback.

## Remaining Checks

- Confirm from a fresh agent turn that the new provider-safe MCP tools appear
  as callable runtime tools.
- Real memory import remains blocked.

## Commit

- `feat: wire shared memory read-only mcp runtime`
