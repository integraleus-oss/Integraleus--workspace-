# Heartbeat Check Repair

- Owner: main
- Started: 2026-09-05
- Mechanism: current foreground Codex turn
- Expected output: repaired recovery-all and Codex account-limit checks with regression tests

## Checklist

- [x] Reproduce both heartbeat failures.
- [x] Make historical unsafe recovery fixtures non-fatal without weakening path validation.
- [x] Remove fragile private Codex dist constructor dependency.
- [x] Add focused regression tests.
- [x] Run heartbeat smoke and Gateway/Telegram health checks.
- [x] Record evidence and final worktree boundary.
