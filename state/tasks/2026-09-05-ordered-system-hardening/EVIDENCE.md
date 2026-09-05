# Ordered system hardening — evidence

Status: RUNNING

- Task packet: `TASK_PACKET.md`
- Managed mechanism: foreground Codex turn
- Last verified: 2026-09-05T22:18:00+03:00

## Heartbeat diagnosis

- `heartbeat-main` had three consecutive 600-second watchdog timeouts.
- Each mandatory shell check was run independently with an external timeout.
  The slowest was the Claude usage probe inside `heartbeat-token-limits.sh`;
  the complete token check finished in 31.44 seconds. The other mandatory
  checks completed in 1.51 seconds combined.
- Root cause: the heartbeat instructions told every heartbeat to inspect all
  cron failures and immediately re-run any timed-out job, without excluding
  the currently executing `heartbeat-main` declaration. A heartbeat timeout
  therefore recursively scheduled its own replay.
- Repair: declaration/current heartbeat jobs are excluded from auto-failover
  and self-rerun. `scripts/heartbeat-main-bounded.sh` gives each mandatory
  check an explicit timeout and reports the exact failing step.

## Activation evidence correction

- The attempt-scoped auth evidence now records the completed activation of
  `ba667378` instead of the stale pending line.

## Inbound timeout retirement

- Twenty Telegram `handler-timeout` rows were retired after a fresh SQLite
  backup at `~/.openclaw/backups/inbound-timeout-retirement-2026-09-05/`.
- Source-after and backup integrity checks are `ok`; backup count is 20 and
  live matching count is zero.
- No replay occurred and outbound delivery rows were not changed.

## SecretRef migration

- The team write-only store was populated from existing local values through
  stdin; credential values were not placed in arguments or evidence.
- Gateway auth, both Telegram bot tokens, and the configured Ollama key now use
  store SecretRefs. Sixteen main/home-monitor auth-profile refs passed preflight
  and were applied. Runtime reload reported zero warnings.
- Remaining plaintext is classified: Discord's current schema rejects its
  advertised SecretRef target; the legacy shared auth store may still serve
  other agents; the home-monitor `models.json` Arcee key is a legacy surface.

## Hardening classification

- Delivery queue health is clean.
- Codex and Moonshot npm install records are pinned to exact versions. Explicit
  external npm specs were required because the bundled Codex copy lacks
  `smol-toml` in this custom installation.
- Security audit after pinning: 0 critical, 5 warnings, 2 info.
- Remaining warnings are policy decisions: loopback proxy trust, workspace-only
  filesystem scope, full exec, host-MCP isolation, and the group-channel
  multi-user heuristic.
- Last verified: 2026-09-05T22:34:00+03:00
