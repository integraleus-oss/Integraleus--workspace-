# MCP Tool Contract

This project currently provides a CLI-compatible server skeleton. The same commands should become MCP tools when wired into OpenClaw.

## Tools

## Phase 4 Read-Only Gateway Subset

Phase 4 runtime wiring is not approved yet. When it is approved, the gateway
must expose only this read-only subset:

- `search_memory`
- `get_with_audit`
- `list_candidates`

The gateway must use a reader-only DB role, require caller identity, filter by
privacy allowlist, log access metadata without secrets or full private bodies,
and fall back to the current markdown memory workflow if DB reads fail.

The following commands remain CLI/project-internal only until a later explicit
write-phase approval:

- `propose_memory`
- `promote_to_shared`
- `reject_candidate`
- `archive_record`
- `supersede`

Direct SQL, backup, restore, and memory import operations must not be exposed as
MCP tools.

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
- `privacy_class`
- `scope`
- `source`
- `confidence`

Promotion must repeat and confirm the candidate privacy class, scope, source, and confidence. This is an intentional guard against accidental or silent promotion.

### reject_candidate

Rejects one candidate without deleting it.

Required:

- `record_id`
- `actor`
- `reason`

### archive_record

Archives one shared record without deleting it.

Required:

- `record_id`
- `actor`
- `reason`

### list_candidates

Lists candidate records visible under the caller privacy policy.

Optional:

- `scope`
- `limit`

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

Creates a shared replacement and marks the old record superseded. Supersede is allowed only for current `shared` records that have not already been superseded.

Required:

- `old_record_id`
- replacement `record_type`
- replacement `title`
- replacement `body`
- replacement `privacy_class`
- replacement `source`
- replacement `created_by`
- `actor`
- `reason`

Optional:

- replacement `scope`
- replacement `source_ref`
- replacement `owner`
- replacement `confidence`
- replacement `tags`
