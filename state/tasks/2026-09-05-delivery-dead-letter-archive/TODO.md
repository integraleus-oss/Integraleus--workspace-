# Delivery Dead-Letter Archive

- Owner: main
- Started: 2026-09-05
- Mechanism: current foreground Codex turn
- Expected output: consistent database backup plus redacted metadata export

## Checklist

- [x] Resolve source stores and schemas read-only.
- [x] Create consistent SQLite backup.
- [x] Export redacted outbound and inbound metadata.
- [x] Record hashes and verify counts.
- [x] Confirm source queues were not changed.
- [x] Record evidence.
