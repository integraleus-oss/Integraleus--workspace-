# Evidence — Heartbeat Check Repair

Status: SUCCEEDED

## Scope

- Owner: `main`
- Execution: foreground Codex turn; no background job remains
- Changed files:
  - `scripts/execution-supervisor-recover-all.py`
  - `scripts/test_execution_supervisor_recovery.py`
  - `scripts/codex-account-limit-switch.mjs`

## Findings and repairs

1. Three 2026-09-01 fixtures use the historical `notification-outbox.jsonl`
   path. The current supervisor correctly rejects it as `unsafe outboxPath`,
   but all three records are terminal and already delivered. `recover-all`
   now reports `RECOVERY_SKIPPED_UNSAFE_TERMINAL` and continues only when the
   state is terminal, has a notification id, and delivery is acknowledged.
   Unsafe pending states still fail closed.
2. The account probe used minified export letters as fallbacks. In the current
   Codex plugin, `requestModule.t` is an Error class, causing the constructor
   failure. Export discovery now selects functions by their stable runtime
   names (`resolveCodexAppServerRuntimeOptions` and
   `requestCodexAppServerJson`).

## Verification

- Supervisor and recovery tests: `25/25 OK`.
- Real recovery scan: `SUPERVISOR_RECOVERY_OK`; three historical terminal
  fixtures explicitly skipped, zero active failures.
- Real Codex account probe: both profiles read successfully; primary 5h 92%,
  backup 5h 53% / week 92%; no switch needed.
- Full `scripts/heartbeat-token-limits.sh`: exit 0; session context below 80%,
  Claude authenticated, Claude usage 10%/1%, no new matching log events.
- `bash -n`, `node --check`, and scoped `git diff --check`: pass.
- Gateway: OpenClaw 2026.9.1, PID 211254, connectivity OK.
- Telegram: both accounts connected and transport probes work.
- Config validation: valid.

## Worktree boundary

The workspace was already dirty. No unrelated changes were reverted or
committed. No Gateway restart was required.
