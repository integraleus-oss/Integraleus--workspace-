---
name: "safe-sqlite-archive"
description: "Archive SQLite queues safely with redacted metadata and proof"
---

# Safe SQLite Archive

## Procedure

1. Resolve the live SQLite path and inspect its schema read-only; finish when the source tables, terminal-state predicates, and baseline counts are recorded without exposing payloads or identifiers.
2. Create the task checklist and evidence file before copying data; state the owner, source, expected artifacts, and explicit no-delete/no-replay boundary, and finish when the archive scope is auditable.
3. Create a consistent backup with SQLite's backup API rather than copying a live database file; write it to a new protected directory and refuse to overwrite an existing backup, then finish when directory mode is `0700` and file mode is `0600`.
4. Export only operational metadata needed for audit: timestamps, statuses, attempt counts, recovery state, reason categories, presence flags, and record counts; replace raw IDs, lane keys, payload containers, and other sensitive values with SHA-256 digests, and finish when no message text, target, raw identifier, payload, or raw error is present.
5. Verify both databases with SQLite integrity checks and compare source-before, source-after, backup, and export counts; finish only when integrity is `ok`, all counts match, and pending-record counts are explicitly reported.
6. Hash the backup and redacted export, record paths, modes, hashes, counts, and unchanged-source evidence, then finish by stating that no deletion or replay occurred.
7. When archived terminal tombstones trigger queue-health warnings, preserve records that serve as deduplication or ownership fences and fix the health predicate to exclude completed recovery states; add a regression proving genuine failed or pending entries still warn, and finish when the warning reflects actionable queue work rather than retained history.

## Stop conditions

- Stop without writing if the source schema or terminal-state meaning is unclear.
- Stop if a destination artifact already exists; never overwrite an earlier evidence package.
- Stop if a redacted export would still reveal message text, targets, credentials, raw IDs, or payload content.
- Treat deletion, replay, resubmission, and retention-policy changes as separate actions requiring their own authorization and backup boundary.
