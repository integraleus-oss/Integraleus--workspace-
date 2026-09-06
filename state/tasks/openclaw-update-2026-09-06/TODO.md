# OpenClaw update 2026-09-06

- Owner: main
- Started: 2026-09-06 08:47 Europe/Moscow
- Execution: current foreground Codex turn on openclaw-home
- Expected output: OpenClaw 2026.9.2, repaired runtime modules, restarted and healthy Gateway, verified Telegram and heartbeat behavior
- Failure mode: stop on update/repair failure; do not force-kill services or roll back destructively
- Notification target: Stanislav via current Telegram direct chat
- Status: SUCCEEDED_WITH_POSTCHECK_WARNING
- Latest evidence: 2026-09-06 10:07 Europe/Moscow
- Earlier failure: managed updater reported `EACCES` while creating `/usr/lib/node_modules/.openclaw-update-stage-*`, but later probes show the installed package and running Gateway are both 2026.9.2.
- Current state: CLI `OpenClaw 2026.9.2 (3928bad)`; package `/usr/lib/node_modules/openclaw/package.json` version `2026.9.2`; Gateway runtimeVersion `2026.9.2`; service reachable and active. Stale update failure/owner_required status remains in the update helper path.

## Checklist

- [x] Record pre-update version and workspace boundary
- [x] Run `openclaw update` / managed update path (eventual installed/running version is 2026.9.2)
- [ ] Run `openclaw doctor --fix` manually outside OpenClaw if needed; OpenClaw expert declined to run repair mode from inside the active inference route
- [x] Inspect recent logs for module errors
- [x] Gateway recovered through managed update handoff
- [x] Verify version, Gateway, Telegram, model/auth, and heartbeat state
- [x] Record final evidence and result

## Remaining warning

- Read-only doctor reports only node-onboarding warnings: device-pair disabled and loopback-only binding. Package-update restart is not currently needed because the running Gateway already uses 2026.9.2.
