# Phase 5 Prep Task Packet: Controlled Memory Candidate Import

Status: prepared, not approved for real import or write-tool exposure
Date: 2026-07-24

## Goal

Prepare the Phase 5 controlled write/import pilot without importing real memory,
without enabling write MCP tools, and without changing the current markdown
memory source of truth.

This prep package defines how existing markdown may later be converted into
reviewable `candidate` records only after a separate owner approval.

## Current Starting Point

- DB pilot host: `openclaw-home`
- DB LAN bind: `192.168.68.125:55432`
- Container: `openclaw-shared-memory-home-postgres`
- Runtime MCP state: read-only tools only
- Current exposed tools: `search_memory`, `get_with_audit`, `list_candidates`
- Current data: disposable smoke records only
- Current operational memory source: existing markdown memory files

## Allowed Work In This Prep Step

- Document the markdown-to-candidate pipeline.
- Document source eligibility, privacy classification, redaction, audit, and
  rollback rules.
- Add a dry-run planner that reads synthetic fixtures by default.
- Add synthetic fixture records for validation.
- Update TODO/evidence files.
- Run syntax, model-validation, and dry-run checks.

## Forbidden Work In This Prep Step

- Do not expose `propose_memory` through OpenClaw MCP/runtime.
- Do not enable `promote_to_shared`, `reject_candidate`, `archive_record`, or
  `supersede` through MCP/runtime.
- Do not import `MEMORY.md`, `STATE.md`, `DECISIONS.md`, or `memory/*.md`.
- Do not read Synology file contents for import candidates.
- Do not write candidates to the DB.
- Do not promote real records.
- Do not replace markdown memory as operational source.
- Do not restart OpenClaw Gateway for Phase 5 prep.

## Candidate Pipeline

```text
approved source list
  -> local dry-run planner
  -> deterministic candidate JSONL preview
  -> owner review of titles/sources/privacy classes
  -> separate approval for tiny real candidate import
  -> candidate queue only
  -> separate human promotion decision
```

The planner output is not canon. It is a review artifact. A record becomes DB
state only through a later explicit candidate-write approval. A record becomes
shared canon only through a later explicit promotion decision.

## Source Eligibility

Default allowed sources for prep:

- synthetic fixtures in this repository;
- manually drafted sample Memory Candidate text;
- redacted evidence notes created specifically for review.

Blocked by default:

- `MEMORY.md`;
- `STATE.md`;
- `DECISIONS.md`;
- `memory/YYYY-MM-DD.md`;
- imported chat/session transcript dumps;
- Synology files;
- `.env`, backups, dumps, session files, and archives.

Future real import approval must name exact files and maximum candidate count.

## Classification Rules

Default privacy class for imported candidates is `personal_stanislav`, because
markdown memory is private unless deliberately narrowed.

Only use `shared_safe` when the candidate is:

- already approved for cross-agent sharing;
- free of personal/private chat contents;
- free of secrets, tokens, credentials, and raw Synology data;
- useful outside a single private agent notebook.

Use `project` for project-local operational facts that should not enter the
plaintext public-style mirror unless policy changes.

Never put `external_forbidden` or `personal_stanislav` into plaintext mirror
output.

## Redaction Rules

Candidates must not include:

- API keys, tokens, passwords, DSNs, cookies, private keys, or session strings;
- raw private chat logs;
- Synology file contents;
- unneeded personal addresses, phone numbers, emails, or account IDs;
- full command output containing local secrets.

The dry-run planner must fail closed on obvious secret-like strings. Manual
review remains mandatory because pattern checks are not a privacy proof.

## Audit Requirements

Every future candidate write must carry:

- `record_type`;
- `title`;
- `body`;
- `privacy_class`;
- `source`;
- `source_ref`;
- `created_by`;
- `scope`;
- `confidence`;
- `reason`;
- source checksum or equivalent provenance marker.

Audit logs must record proposal writes without exposing record bodies in
operational logs.

## Rollback

For prep-only work, rollback is deleting generated preview artifacts and
leaving DB/runtime untouched.

For a later candidate-write pilot, rollback is:

- stop exposing the write tool;
- keep audit logs;
- reject imported candidates through the human-approved promoter path;
- do not delete DB rows unless Stanislav separately approves data purging.

## Acceptance Criteria

- Phase 5 docs clearly separate prep, candidate write, and promotion gates.
- Dry-run planner validates synthetic records and emits candidate previews.
- Dry-run planner refuses real memory paths by default.
- Secret-like synthetic input is rejected.
- No DB writes occur.
- OpenClaw runtime remains read-only.
- Markdown remains operational source.
