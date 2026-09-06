# Ordered system hardening — evidence

Status: SUCCEEDED

- Task packet: `TASK_PACKET.md`
- Managed mechanism: foreground Codex turn
- Completed: 2026-09-06T11:30:24+03:00
- Original execution stopped because the foreground turn ended after activation
  and scoped commits, before this evidence file and checklist were finalized.
  The activation helper also invoked `scripts/heartbeat-main-bounded.sh` from
  the wrong working directory, producing a non-fatal `No such file or
  directory` line even though the script was committed at `8c18a573`.

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

## Completion verification

- Scoped implementation commit: `8c18a573` (`fix: bound heartbeat and archive stale ingress`).
- Activation-verifier commit: `da2b68d6` (`chore: add hardening activation verifier`).
- Post-restart status recorded Gateway health `true`, Telegram accounts 2/2
  connected, and security audit 0 critical / 5 warnings / 2 info.
- Secret audit recorded zero unresolved SecretRefs; remaining findings were
  classified plaintext/legacy residues rather than failed activation.
- Final execution-truth, manual heartbeat, deep status, and fresh-log checks
  were repeated at 2026-09-06T11:30+03:00.
- `python3 scripts/execution-truth-watch.py --root state/tasks` returned
  `EXECUTION_TRUTH_OK`; the stale `RUNNING` finding is cleared.
- Manual managed `heartbeat-main` was enqueued but skipped because the main
  agent lane was active. The bounded foreground heartbeat then ran every check:
  Codex process watch `OK`, execution truth `OK`, supervisor recovery `OK`,
  Gateway status `OK`, and token/account probes completed for both OAuth
  profiles. Overall result was `HEARTBEAT_MAIN_WARN` only because the existing
  log classifier mislabeled an informational `agent-turn-timing` line as a new
  `model_fallback` event.
- Current `openclaw status --deep`: Gateway reachable on 2026.9.2, Telegram
  `OK` with accounts 2/2, event loop healthy, security audit 0 critical / 5
  warnings / 2 info, and no delivery-queue warning.
- Fresh logs contain repeated non-terminal Codex settled-turn-finalization
  context warnings. Status still exposes the separate stale update marker
  `owner_required`; neither warning changes this task's terminal state.
- Manual heartbeat output: `terminalization-heartbeat.log`.
