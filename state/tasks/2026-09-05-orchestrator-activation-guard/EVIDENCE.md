# Evidence

Status: BLOCKED_ON_FRESH_OWNER_RETRY
Last evidence: 2026-09-05T08:45:00+03:00
Heartbeat window: 10 minutes
Timeout: 2 hours
Notification target: Telegram `-1004417478336`, topic `2922`
Disable path: cancel the managed TaskFlow job; if activation has begun, follow `ROLLBACK.md`.

## Initial facts

- Main branch: `92ee5436`.
- Candidate commit: `f70913ea` in worktree `/home/stanislav/agent-runs/managed-program-r20-isolated`.
- Gateway at preflight: reachable; Telegram accounts 2/2 OK.
- Managed tasks at preflight: 0 active.
- Sandbox container at preflight: running, but mounted to the isolated worktree.
- No activation or live drill has been claimed.

## Evidence log

- 2026-09-05T08:19:00+03:00: artifact gate completed. Managed job ID and live-process proof still pending; status remains `PLANNED`.
- 2026-09-05T08:22:00+03:00: pre-activation gate started in live exec session `90986` from candidate worktree at commit `f70913ea`. Command runs runner, supervisor, TaskFlow, syntax and diff checks. Live session proof exists; status is `RUNNING` only for the current foreground-controlled turn.
- 2026-09-05T08:22:13+03:00: candidate integrated into `main` as scoped commit `6c03db78`; live plugin and five script files match candidate content.
- 2026-09-05T08:22:06+03:00: protected runtime installed under `~/.openclaw/runtime/execution-supervisor/`; directory modes are `0700`, executable runtime files `0500`, and the shared contract `0400`.
- 2026-09-05T08:22:13+03:00: managed-worker workspace remapped from the isolated worktree to the main workspace. Sandbox remains Docker, network `none`, read-only root, user `1000:1000`, all capabilities dropped. The old sandbox was removed and will be recreated on first managed use.
- 2026-09-05T08:22:42+03:00: `openclaw gateway restart` cleanly interrupted the active Codex turn. Main-session restart recovery marked one interrupted source session and resumed it at 08:22:53 without a new owner message (`recovered=1 failed=0 skipped=0`). This is direct reply-boundary recovery evidence.
- 2026-09-05T08:23-08:25+03:00: Gateway is active as PID `411552`, listening only on loopback `127.0.0.1/[::1]:18789`; `openclaw status --deep` reports Gateway reachable, event loop OK, Telegram 2/2 OK. No module-load or Telegram 409 errors observed.
- 2026-09-05T08:24-08:25+03:00: runner test PASS; supervisor 22/22 PASS; TaskFlow integration PASS; Node/Python syntax PASS; `git diff --check` PASS; plugin doctor PASS. An attempted `npm test` was only a wrong command (the package has no npm test script); the documented `node --test index.test.mjs` command passed.
- 2026-09-05T08:26+03:00: the live dispatch tool rejected this recovered system continuation with `trusted owner required`. This is the intended fail-closed owner boundary: the restart-recovery continuation does not carry a fresh authenticated Telegram sender context. No managed job was created and no work is claimed as running.

## Remaining live gate

A fresh authenticated owner message in Telegram topic `2922` must trigger `execution_supervisor_dispatch`. Acceptance requires durable admission/task paths, TaskFlow ID, supervisor PID, current heartbeat, validated terminal result, and one acknowledged notification back to the same topic. Until then the activation is installed and healthy, but the end-to-end owner-dispatch drill is truthfully blocked rather than `RUNNING`.

- 2026-09-05T08:40:41+03:00: fresh owner message `Запусти контрольный drill` reached Telegram ingress, but no admission was created. `execution_supervisor_dispatch` failed closed with `no managed admission for this turn`; no job was claimed as running. Root cause: the exact operator drill phrase was absent from `DEFAULT_MANAGED_PATTERNS`.
- 2026-09-05T08:42:18+03:00: commit `fe8c515f` added the exact drill phrase to `DEFAULT_MANAGED_PATTERNS` and its regression test. The Gateway then restarted to load the plugin change; restart recovery resumed the source session (`recovered=1 failed=0 skipped=0`).
- 2026-09-05T08:45+03:00: post-restart dispatch was attempted and failed closed with `trusted owner required`. The original authenticated owner turn had already passed its admission hook before the phrase patch, while the recovered continuation is deliberately not treated as a fresh owner turn. Therefore no admission path, TaskFlow ID, detached supervisor PID, or heartbeat exists, and the drill is not `RUNNING`.
