# Phase 4 Prep Task Packet: Read-Only MCP/API Gateway

Status: prepared, not approved for runtime wiring
Date: 2026-07-23

## Goal

Prepare the Phase 4 read-only MCP/API gateway package after the
`openclaw-home` DB pilot, without changing OpenClaw runtime config and without
importing real memory.

Phase 4 is allowed to become a runtime change only after a separate explicit
approval.

## Current Starting Point

- DB pilot host: `openclaw-home`
- DB LAN bind: `192.168.68.125:55432`
- Container: `openclaw-shared-memory-home-postgres`
- Current data: disposable smoke records only
- Current operational memory source: existing markdown memory files
- Synology role: storage/backup candidate only

## Allowed Work In This Prep Step

- Document the read-only gateway surface.
- Document caller identity, privacy, audit, and fallback requirements.
- Add local verification scripts that read smoke data only.
- Update TODO/evidence files.
- Run read-only DB checks against the current pilot.

## Forbidden Work In This Prep Step

- Do not edit OpenClaw runtime config.
- Do not register MCP tools in the live Gateway.
- Do not restart OpenClaw Gateway.
- Do not import `MEMORY.md`, `STATE.md`, `DECISIONS.md`, or `memory/*.md` into DB.
- Do not promote real memory records.
- Do not enable write tools through the gateway.
- Do not expose the DB outside the local network/VPN-private LAN boundary.

## Read-Only Gateway Surface

Approved-for-design tools:

- `search_memory`
- `get_with_audit`
- `list_candidates`

Excluded from Phase 4 runtime exposure:

- `propose_memory`
- `promote_to_shared`
- `reject_candidate`
- `archive_record`
- `supersede`
- direct SQL execution
- backup/restore operations

## Required Gateway Behavior

- Use a reader-only DB role.
- Require caller identity on every request.
- Apply privacy allowlist before returning records.
- Include audit context for direct record fetches.
- Log access metadata without DB URLs, passwords, record bodies, or secrets.
- On DB/gateway failure, fall back to the current markdown memory workflow.
- A failed read must not block normal OpenClaw operation.

## Acceptance Criteria

- DB pilot is healthy and reachable on the LAN bind.
- Reader role can run read-only searches.
- Privacy-denied smoke content is not returned.
- Reader role cannot write directly.
- Candidate listing is privacy-filtered.
- Fallback behavior is specified before runtime wiring.
- Approval request clearly states the exact runtime files/tools to change later.
