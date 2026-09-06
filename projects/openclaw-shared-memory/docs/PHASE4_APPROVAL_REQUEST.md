# Phase 4 Approval Request: Read-Only MCP/API Gateway

Status: draft, not approved
Date: 2026-07-23

## Requested Approval

Approve a future Phase 4 runtime change that wires a read-only OpenClaw
MCP/API gateway to the `openclaw-home` shared-memory DB pilot.

This request is not approval to perform Phase 4 yet.

## Proposed Runtime Scope

- Register read-only memory tools in OpenClaw Home:
  - `search_memory`
  - `get_with_audit`
  - `list_candidates`
- Use the reader-only DB role.
- Keep markdown memory as fallback and operational source.
- Use smoke records only until real-memory import is separately approved.
- Log access metadata without secrets or full private bodies.

## Explicitly Not Included

- write tools;
- candidate proposal tools;
- promotion/rejection/archive/supersede tools;
- import of existing memory files;
- replacing markdown memory as operational source;
- Synology package/runtime changes;
- WAN/public exposure;
- Gateway restart outside an approved maintenance action.

## Preconditions

- `openclaw-shared-memory-home-postgres` is healthy.
- DB remains bound to `192.168.68.125:55432`, not wildcard.
- `scripts/run_phase4_readonly_preflight.py` passes.
- Runtime config diff is reviewed before applying.
- Rollback path is documented.

## Rollback Requirement

If the runtime wiring causes errors, disable the new read-only tools and return
to markdown memory only. Do not delete DB data during rollback.

## Approval Phrase

Use a separate explicit command such as:

```text
approve Phase 4 runtime read-only MCP wiring
```

Without that command, this project remains at DB pilot plus prep documentation.
