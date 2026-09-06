# Outbound dead-letter archive

- Owner: main
- Started: 2026-09-06 Europe/Moscow
- Execution: current foreground turn
- Expected output: protected SQLite backup, redacted audit export, terminal-only archive/removal, integrity and zero-count proof
- Authorization: archive and remove the 115 old terminal dead-letter entries
- Hard boundary: no replay, resubmission, delivery, payload export, or overwrite of prior backups

## Checklist

- [x] Resolve live database, schema, terminal predicate, and baseline counts read-only
- [x] Create protected SQLite backup using the backup API
- [x] Export redacted operational metadata only
- [x] Verify backup/source integrity and matching pre-change counts
- [x] Remove only the proven terminal archive scope in one transaction
- [x] Verify source integrity, pending counts, and dead-letter count zero
- [x] Hash artifacts and record final evidence
