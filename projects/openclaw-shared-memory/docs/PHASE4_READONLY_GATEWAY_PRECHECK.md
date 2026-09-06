# Phase 4 Read-Only Gateway Precheck

Status: prepared
Date: 2026-07-23

## Runtime Boundary

This is a planning and verification artifact only. It does not approve or
perform OpenClaw runtime wiring.

The future gateway must read through a dedicated reader role and must not make
OpenClaw depend on the shared-memory DB. Existing markdown memory remains the
operational source unless and until a separate migration is approved.

## Tool Allowlist

Phase 4 gateway may expose only:

- `search_memory`
- `get_with_audit`
- `list_candidates`

All write/canon-changing tools remain blocked:

- `propose_memory`
- `promote_to_shared`
- `reject_candidate`
- `archive_record`
- `supersede`

## Identity And Privacy

Every gateway request must carry:

- caller identity
- source surface or agent id
- request reason or task id when available

Every response must be filtered by:

- allowed privacy classes
- record status
- scope, when supplied

Default Phase 4 readable privacy classes:

- `project`
- `shared_safe`

## Audit Requirements

- `get_with_audit` must include record audit trail for allowed records.
- Gateway logs may include tool name, caller, scope, result count, and status.
- Gateway logs must not include passwords, DB URLs, full record bodies, tokens,
  backup file paths with secrets, or raw private memory dumps.

## Failure And Fallback

If the DB, network, container, or gateway adapter fails:

- return a clear read-unavailable error to the caller;
- continue using the current markdown memory workflow;
- do not retry writes;
- do not attempt migration/import;
- do not restart OpenClaw Gateway automatically.

## Pre-Runtime Smoke Checks

Run from project root after sourcing local pilot secrets:

```bash
set -a
source ~/.local/share/openclaw-shared-memory/.env
source ~/.local/share/openclaw-shared-memory/secrets/roles.env
set +a

.venv/bin/python scripts/run_phase4_readonly_preflight.py
```

Expected result:

```text
PHASE4_READONLY_PREFLIGHT_OK
```

The script checks reader health, role attributes, privacy filtering, candidate
listing, audit retrieval for allowed smoke data, and direct write denial. It
does not import real memory and does not change OpenClaw runtime config.
