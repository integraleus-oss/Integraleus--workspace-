# Heartbeat log-filter fix

- Owner: main
- Started: 2026-09-06 Europe/Moscow
- Execution: current foreground turn
- Expected output: `agent-turn-timing` informational lines no longer produce model/context warnings
- Boundary: no queue mutation, replay, auth-order change, or Gateway restart

## Checklist

- [x] Inspect current classifier and state format
- [x] Add exact exclusion/regression coverage
- [x] Run focused tests
- [x] Run full heartbeat and record evidence
