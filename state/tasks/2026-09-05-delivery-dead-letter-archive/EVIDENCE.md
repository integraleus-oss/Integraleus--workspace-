# Evidence — Delivery Dead-Letter Archive

Status: SUCCEEDED

No deletion or replay was performed. The source queues remain unchanged.

## Artifacts

- Consistent SQLite backup:
  `/home/stanislav/.openclaw/backups/delivery-dead-letter-2026-09-05/openclaw.sqlite`
- Redacted metadata export: `dead-letter-metadata.redacted.json`
- Reproducible export script: `export-dead-letter-metadata.mjs`

## Verification

- Backup directory mode: `0700`; backup and export modes: `0600`.
- Backup SQLite integrity: `ok`.
- Source SQLite integrity: `ok`.
- Source counts before/after: outbound failed `115`, inbound failed `20`.
- Backup counts: outbound failed `115`, inbound failed `20`.
- Export counts: outbound `115`, inbound `20`.
- Pending outbound: `0`; pending inbound: `0`.
- Export excludes payloads, message text, targets, raw IDs, lane keys, and raw
  errors. Sensitive identifiers and payload containers are represented only by
  SHA-256 digests.

## SHA-256

- SQLite backup:
  `d8614a285d72e281dba407ac188e5b76e67f2d45edec046df941842660dfbe2b`
- Redacted metadata export:
  `ac9fbf21816ff13871259a440793743e75986cf4286c47a38d9bccee3075911b`
