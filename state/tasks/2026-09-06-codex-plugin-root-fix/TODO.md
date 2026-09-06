# Codex plugin root fix

- Owner: main
- Started: 2026-09-06 Europe/Moscow
- Execution: current foreground turn
- Expected output: registry-based Codex plugin discovery and successful two-profile limit probe
- Safety: no outbound queue changes or message replay

## Checklist

- [x] Preserve pre-change script snapshot
- [x] Resolve the installed Codex plugin through `openclaw plugins list --json`
- [x] Patch plugin discovery with a legacy fallback
- [x] Run syntax and focused probe checks
- [x] Run full heartbeat token-limit check
- [x] Record evidence and final status
