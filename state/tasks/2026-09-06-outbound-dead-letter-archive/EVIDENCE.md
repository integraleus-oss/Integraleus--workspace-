# Evidence: outbound dead-letter archive

Status: SUCCEEDED

## Scope proof

- Live database: `/home/stanislav/.openclaw/state/openclaw.sqlite`.
- Table: `delivery_queue_entries`.
- Exact predicate: `status='failed'`, `recovery_state='completed_permanent'`, and `platform_send_started_at IS NULL`.
- Baseline: 115 matching rows; every row had `failed_at` populated.
- Age check: zero rows updated/enqueued in the last 24 hours; three within seven days; oldest approximately 93 days.
- Pending before archive: zero.

## Archive

- Protected directory: `/home/stanislav/.openclaw/backups/outbound-dead-letter-archive-2026-09-06` mode `0700`.
- Consistent SQLite backup: `openclaw.sqlite` mode `0600`.
- Redacted metadata export: `delivery-dead-letters.redacted.json` mode `0600`.
- Backup count: 115 terminal dead letters.
- Redacted export count: 115; forbidden raw keys for ids, targets, payloads, message text, and errors: none.
- Stable backup SHA-256: `ac8583fdbb3d0cc572676313211f0b02b2a33b3f8d813f120d16211f1b8de824`.
- Export SHA-256: `46e57501c3ab8c5f8a76ad29980bf65c66a2796107ed7d6290d26595eb866a55`.
- Note: the first independent SQLite read created WAL/SHM bookkeeping and normalized the backup header; the SHA-256 above was repeated afterward and remained stable.

## Mutation and verification

- Deleted exactly 115 snapshot-matched rows in one `BEGIN IMMEDIATE` transaction.
- Source integrity before: `ok`.
- Backup integrity: `ok`.
- Source integrity after: `ok`.
- Live failed count after: zero.
- Live pending count after: zero.
- Deep health after: `health.ok=true`; `deliveryQueues=null`.
- Replay/resubmission/delivery performed: **no**.
