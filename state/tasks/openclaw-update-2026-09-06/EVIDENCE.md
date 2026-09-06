# Transactional updater evidence

Status: SOURCE_VERIFIED_NOT_EXECUTED
Verified: 2026-09-06 11:56 MSK

## Scope

- Durable updater: `scripts/openclaw-transactional-update.sh`.
- Regression test: `scripts/test_openclaw_transactional_update.sh`.
- No real update, doctor repair, Gateway restart, queue operation, or message
  delivery was performed in this verification.

## Verification

- Bash syntax for updater and test: PASS.
- Mock success case: PASS; exactly one safe Gateway restart.
- Mock failure case: PASS; failed update does not enter normal restart and
  invokes recovery start when the previously-running service is inactive.
- Mock dry-run case: PASS; no Gateway restart/start.
- Live `--dry-run --timeout 120`: PASS on OpenClaw `2026.9.2`.
- Live preflight config validation: PASS.
- Live backup dry-run: PASS; workspace excluded, no archive written.
- Live update dry-run: target/current both `2026.9.2`, restart false, status
  `skipped` with reason `dry-run`.

## Safety boundary

- The updater is designed for an external managed job, not the Gateway process
  tree it protects.
- Installation uses `update --no-restart`; config and backup gates precede it.
- A real run creates and verifies a protected backup before installation and
  performs at most one final safe restart when the Gateway was active at entry.
- Message queues, notification records, SQLite delivery data, and message
  replay/resend are outside scope.
