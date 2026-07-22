# MCP Tool Contract

This project currently provides a CLI-compatible server skeleton. The same commands should become MCP tools when wired into OpenClaw.

## Tools

### propose_memory

Creates a candidate record.

Required:

- `record_type`
- `title`
- `body`
- `privacy_class`
- `source`
- `created_by`
- `reason`

Optional:

- `scope`
- `source_ref`
- `owner`
- `confidence`
- `tags`
- `metadata`

### promote_to_shared

Promotes one candidate to shared canon.

Required:

- `record_id`
- `actor`
- `reason`

### search_memory

Searches records by text filters first. Vector search is reserved for the next implementation step after embedding generation is wired.

Required:

- `query`

Optional:

- `scope`
- `status`
- `limit`

### get_with_audit

Fetches one record and the full audit trail.

Required:

- `record_id`

### supersede

Creates a shared replacement and marks the old record superseded. The Python repository already has this operation; the CLI parser should expose it before runtime wiring.

