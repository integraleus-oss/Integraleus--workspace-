# Supervisor stale-admission repair

- Owner: main
- Started: 2026-09-05T09:16:20+03:00
- Mechanism: current foreground Codex session
- Expected output: tested plugin fix for terminal admission cleanup and invalid managed working-directory handling

## Checklist

- [x] Reproduce stale `DISPATCHED` admission after terminal state
- [x] Clear/revalidate terminal admissions before tool blocking
- [x] Tolerate a workspace directory disappearing during trusted-context traversal
- [x] Add regression tests
- [x] Run focused tests and `git diff --check`
- [x] Install protected runtime and restart Gateway
- [x] Verify live Gateway/plugin state
- [x] Record final evidence and commit boundary
