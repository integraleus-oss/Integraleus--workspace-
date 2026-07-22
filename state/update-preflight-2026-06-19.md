# Update Preflight - 2026-06-19

Started: 2026-06-19 15:40 MSK
Scope: read-only preflight before server updates.

## Checklist

- [x] System baseline captured
- [x] Reboot-required status checked
- [x] Apt pending upgrades reviewed without installing
- [x] Critical services checked
- [x] Agent/tooling versions and install paths checked
- [x] Risks and next-step recommendation written
- [x] User-visible report sent

## Constraints

- No package installation.
- No package upgrade.
- No service restart.
- No config changes.
- Do not read secrets or token contents.

## Findings

Captured: 2026-06-19 15:40-15:43 MSK

### System Baseline

- Host: `openclaw-home`
- OS: Ubuntu 24.04.4 LTS
- Kernel: `6.17.0-35-generic`
- Hardware: GEEKOM A6
- Uptime: about 1 day 4 hours
- Load at capture: `3.66, 2.80, 2.99`
- Root filesystem: 937G total, 61G used, 829G available, 7% used
- Memory: 11Gi total, 8.4Gi used, 3.1Gi available
- Swap: 4.0Gi total, 3.0Gi used
- Failed systemd units: none
- Reboot required: yes, package marker says `amneziawg-dkms`

### Apt / Dpkg

- `dpkg --audit`: no reported broken or half-configured packages.
- No unrelated `apt` or `dpkg` process was found; only the preflight commands themselves appeared during checks.
- `apt list --upgradable`: 17 packages listed.
- `apt-get -s upgrade`: would upgrade 16 packages, install 0 new packages, remove 0 packages, keep back 1 package.
- `apt-mark showhold`: `tailscale` is held.
- `apt-get -s install tailscale`: would upgrade held `tailscale` from `1.96.4` to `1.98.4` if explicitly requested.
- Autoremove candidates reported by simulation: `libfwupd2`, `libslirp0`, `slirp4netns`. Do not remove during the first update pass.

Pending apt upgrades:

- `amneziawg`: `1.0.20210914-0~202602231231+5d6179a~ubuntu24.04.1` -> `1.0.20210914-0~202606190632+61e7417~ubuntu24.04.1`
- `amneziawg-tools`: same old/new build line as `amneziawg`
- `docker-ce`, `docker-ce-cli`, `docker-ce-rootless-extras`: `5:29.5.3-1~ubuntu.24.04~noble` -> `5:29.6.0-1~ubuntu.24.04~noble`
- `docker-model-plugin`: `1.2.1-1~ubuntu.24.04~noble` -> `1.2.4-1~ubuntu.24.04~noble`
- `libheif*`, `heif-*`: `1.17.6-1ubuntu4.3` -> `1.17.6-1ubuntu4.4`
- `nodejs`: `22.22.3-1nodesource1` -> `22.23.0-1nodesource1`
- `tailscale`: `1.96.4` -> `1.98.4`, but held
- `vim-common`, `vim-tiny`, `xxd`: `2:9.1.0016-1ubuntu7.15` -> `2:9.1.0016-1ubuntu7.16`

### Critical Services

- OpenClaw gateway: reachable, user systemd service enabled and running since 2026-06-18 11:26 MSK.
- OpenClaw version: `2026.6.1`; update available: `2026.6.8`.
- OpenClaw dashboard bind: local loopback, Tailscale exposure off.
- OpenClaw deep status: gateway reachable, Telegram OK, tasks audit clean.
- OpenClaw security audit still reports pre-existing hardening warnings, including small-model sandbox/web-tool warning, `tools.fs.workspaceOnly=false`, full exec trust, group-writable state dir, and empty plugin allowlist. Treat as separate hardening work, not an apt-update blocker.
- Docker service: active.
- Docker containers: `n8n-app`, `n8n-caddy`, `n8n-postgres`, `alpha-bpr-postgres` running; postgres containers healthy.
- Tailscale: active at `100.114.189.16`.
- RustDesk: active and enabled.
- Ollama: active and enabled.

### Tooling

- `openclaw`: `2026.6.1`, `/usr/bin/openclaw -> /usr/lib/node_modules/openclaw/openclaw.mjs`
- `codex`: `codex-cli 0.140.0`, `/usr/bin/codex -> /usr/lib/node_modules/@openai/codex/bin/codex.js`
- `claude`: `2.1.179 (Claude Code)`, `/usr/bin/claude -> /usr/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`
- `node`: `v22.22.3`
- `npm`: `10.9.8`
- Global npm prefix: `/usr`
- Global npm packages checked: `openclaw@2026.6.1`, `@openai/codex@0.140.0`, `@anthropic-ai/claude-code@2.1.179`, `npm@10.9.8`
- `docker`: `29.5.3`
- `tailscale`: `1.96.4`

### Workspace Status

- Pre-existing modified files: `STATE.md`, `memory/heartbeat-state.json`
- New preflight artifact: `state/update-preflight-2026-06-19.md`
- Pre-existing untracked directories/files also exist under `output/`, `state/`, and `work_summary.md`; not touched for this task.

## Recommendation

Go/no-go for next stage: go, with caution.

Recommended next stage:

1. Do not run a blind full cleanup or autoremove.
2. Keep `tailscale` held for the first apt pass unless Stanislav explicitly wants the Tailscale upgrade included.
3. Run the normal apt upgrade for the 16 non-held packages first.
4. Expect Docker and Node.js package updates; verify Docker containers and OpenClaw immediately after.
5. Do not reboot before the package pass unless something breaks; a reboot is already required because of `amneziawg-dkms`, so prefer one controlled reboot after package updates and checks.
6. Treat OpenClaw `2026.6.1 -> 2026.6.8` as a separate stage after apt validation: `openclaw doctor --fix`, update, clean gateway restart, then `openclaw status --deep`.
7. Decide separately whether to unhold and upgrade `tailscale`.

## Apt Update Execution

Started: 2026-06-19 15:44 MSK

- [x] Confirm `tailscale` remains held
- [x] Refresh apt package lists
- [x] Upgrade non-held packages
- [x] Verify apt/dpkg health
- [x] Verify Docker service and containers
- [x] Verify OpenClaw gateway
- [x] Verify Tailscale
- [x] Verify RustDesk
- [x] Verify reboot-required marker
- [x] Send user-visible result

Constraints:

- Keep `tailscale` held.
- Do not run `autoremove`.
- Do not update OpenClaw in this stage.
- Do not reboot before post-checks.

Result:

- `apt-get update`: completed successfully.
- `apt-get upgrade -y`: completed successfully.
- Upgraded packages: `amneziawg`, `amneziawg-tools`, `containerd.io`, `docker-ce`, `docker-ce-cli`, `docker-ce-rootless-extras`, `docker-model-plugin`, `heif-gdk-pixbuf`, `heif-thumbnailer`, `libheif-plugin-aomdec`, `libheif-plugin-aomenc`, `libheif-plugin-libde265`, `libheif1`, `nodejs`, `vim-common`, `vim-tiny`, `xxd`.
- Kept back: `tailscale`, still held.
- Remaining upgradable package: `tailscale` `1.96.4 -> 1.98.4`.
- `dpkg --audit`: clean.
- Failed systemd units after update: none.
- Reboot-required marker after update: still yes, `amneziawg-dkms`.
- Versions after update: Node.js `v22.23.0`, Docker `29.6.0`, OpenClaw still `2026.6.1`, Codex `0.140.0`, Claude `2.1.179`.
- Docker restarted during package update. `n8n-caddy`, `n8n-app`, and `n8n-postgres` came back automatically.
- `alpha-bpr-postgres` had stopped cleanly with exit `0` because its restart policy is `no`; it was started manually to restore pre-update state and is now running healthy.
- OpenClaw gateway after update: reachable, Telegram OK, tasks audit clean.
- Tailscale after update: active at `100.114.189.16`, still version `1.96.4`.
- RustDesk after update: active.
- Ollama after update: active.

Next:

- [x] Controlled reboot completed; boot time 2026-06-19 15:49:01 MSK
- [x] Post-reboot verify failed units
- [x] Post-reboot verify OpenClaw gateway
- [x] Post-reboot verify Docker containers
- [x] Post-reboot verify Tailscale
- [x] Post-reboot verify RustDesk

Post-reboot result:

- Boot time: 2026-06-19 15:49:01 MSK.
- Failed systemd units: none.
- Reboot-required marker: absent.
- OpenClaw gateway: user systemd service active/enabled, gateway reachable, Telegram OK.
- Docker services: `docker`, `containerd` active.
- Docker containers: `n8n-caddy`, `n8n-app`, `n8n-postgres`, `alpha-bpr-postgres` running; postgres containers healthy.
- `alpha-bpr-postgres` again required manual `docker start` after reboot because restart policy is `no`; restored to pre-update running state.
- Tailscale service: active, systemd status says connected as `integraleus@gmail.com`, IP `100.114.189.16`.
- Tailscale functional check: `tailscale ping --c 1 100.81.237.50` succeeded direct to `note-pavlovsky` in 3 ms.
- Tailscale CLI note: `tailscale status --peers=false` still labels self as `offline`; because service status, IP, SSH logs, netcheck, and ping are good, treat as observation rather than outage.
- RustDesk: active.
- Ollama: active.
- Remaining apt upgradable package: held `tailscale` `1.96.4 -> 1.98.4`.
- OpenClaw remains `2026.6.1`; update to `2026.6.8` remains next separate stage.

## Tailscale Held Package Update

Started: 2026-06-19 15:56 MSK

- [x] Confirm current hold/version
- [x] Unhold `tailscale`
- [x] Upgrade `tailscale`
- [x] Re-apply hold to keep controlled updates
- [x] Verify `tailscaled` service
- [x] Verify Tailscale IP/status/ping
- [x] Verify apt/dpkg state
- [x] Send user-visible result

Result:

- `tailscale` hold before update: confirmed.
- `tailscale` before update: `1.96.4`.
- `apt-mark unhold tailscale`: completed.
- `apt-get install -y tailscale`: completed.
- `tailscale` after update: `1.98.4`.
- `apt-mark hold tailscale`: completed; package is held again.
- `tailscaled`: active and connected.
- Tailscale IP: `100.114.189.16`.
- `tailscale status --peers=false`: self no longer marked `offline`.
- Tailnet ping: `note-pavlovsky` `100.81.237.50` direct via LAN, 2 ms.
- `tailscale netcheck`: UDP true, IPv4 yes, nearest DERP Helsinki.
- `apt list --upgradable`: no remaining upgradable packages listed.
- `dpkg --audit`: clean.
- Reboot-required marker: absent.
- OpenClaw after Tailscale update: gateway reachable, Telegram OK, tasks audit clean.
- Docker containers after Tailscale update: `n8n-*` and `alpha-bpr-postgres` running; postgres containers healthy.

## OpenClaw Update

Started: 2026-06-19 16:02 MSK

- [x] Capture pre-update OpenClaw/Codex/Claude versions and paths
- [x] Run OpenClaw update
- [x] Run `openclaw doctor --fix`
- [x] Check `openclaw logs --plain --limit 50`
- [x] Restart gateway cleanly
- [x] Run `openclaw status --deep`
- [x] Verify Telegram channel health
- [x] Verify Codex CLI version/path unchanged
- [x] Verify Claude Code CLI version/path unchanged
- [x] Verify Docker/Tailscale/RustDesk remain active
- [ ] Send user-visible result

Attempt note:

- Direct `openclaw update` from this Codex turn refused safely because the command is running inside the gateway process tree. Next attempt must run outside gateway, e.g. detached `systemd --user` job with log capture.

Verification result, 2026-06-19 16:42-16:48 MSK:

- OpenClaw is updated: `OpenClaw 2026.6.8 (844f405)`.
- Global npm package state: `openclaw@2026.6.8`, `@openai/codex@0.140.0`, `@anthropic-ai/claude-code@2.1.179`.
- Paths remain separate: `/usr/bin/openclaw`, `/usr/bin/codex`, `/usr/bin/claude`.
- Codex CLI remains `codex-cli 0.140.0`.
- Claude Code CLI remains `2.1.179 (Claude Code)`.
- Gateway user service is active/enabled and reachable; `openclaw status --deep` reports gateway app `2026.6.8`, Telegram OK, tasks audit clean.
- Logs show the gateway restarted cleanly at 16:17 MSK after update; later logs show normal Telegram inbound/outbound.
- `openclaw doctor --fix` completed. Remaining doctor findings: OpenRouter catalog entry missing `api`, old non-effective `openai:integraleus@gmail.com` OAuth profile expired, legacy state/orphan transcript cleanup candidates, plaintext secret config warning, and official `discord` plugin drift `2026.5.12 -> expected 2026.6.8`.
- Model status: default model remains `openai/gpt-5.5`; effective OpenAI profiles are `openai:stasiintegraleus@gmail.com` then `openai:integraleus55@gmail.com`.
- Model fallback list is now `ollama/qwen2.5:3b`; this differs from the previously documented expected fallback `ollama/phi3:instruct` and should be handled as a separate config cleanup.
- Services remain active: `docker`, `containerd`, `tailscaled`, `rustdesk`, `ollama`.
- Docker containers remain running: `n8n-caddy`, `n8n-app`, `n8n-postgres` healthy, `alpha-bpr-postgres` healthy.
- Tailscale remains `1.98.4`; `tailscale status --peers=false` shows `openclaw-home` at `100.114.189.16`.

## OpenClaw Config Cleanup

Started: 2026-06-19 16:46 MSK

- [x] Restore expected model fallback to `ollama/phi3:instruct`
- [x] Remove stale `ollama/qwen2.5:3b` allowed-model entry from OpenClaw config
- [x] Update heartbeat Codex limit switch script for current `openai:*` OAuth profile ids
- [x] Filter benign `openclaw models fallbacks list`/auto-enable log lines from heartbeat WARN detection
- [x] Check drifted official plugin state with `openclaw doctor --fix`
- [x] Investigate OpenRouter catalog warning without exposing API keys
- [ ] Clean safe legacy/orphan state if OpenClaw provides a non-destructive path
- [x] Re-run `openclaw doctor --fix`
- [x] Restart gateway cleanly if plugin/config changes require it
- [x] Re-run `openclaw status --deep`
- [x] Verify `codex` and `claude` CLI versions remain unchanged
- [x] Send user-visible result

Progress, 2026-06-19 17:03 MSK:

- `openclaw models status --json`: default/resolved model is `openai/gpt-5.5`; allowed models no longer include `ollama/qwen2.5:3b`.
- `openclaw models fallbacks list`: only `ollama/phi3:instruct`.
- Effective OpenAI profiles: `openai:stasiintegraleus@gmail.com` then `openai:integraleus55@gmail.com`.
- Legacy compatibility: `openclaw doctor --fix` set `plugins.bundledDiscovery="compat"` and refreshed plugin registry.
- Remaining doctor findings are not auto-fixed: expired non-effective `openai:integraleus@gmail.com` OAuth profile for main/home-monitor, legacy Telegram state files, 7 orphan transcript files, plaintext secret fields in `openclaw.json`.
- Discord channel currently logs `401 Unauthorized`; left enabled pending explicit user decision to replace token or disable Discord.
- `scripts/heartbeat-token-limits.sh` now exits cleanly: Codex per-account check OK, no session >80%, Claude auth/usage OK, no new matching limit/auth/fallback/context events.
- `codex --version`: `codex-cli 0.140.0`; `claude --version`: `2.1.179 (Claude Code)`.

Final post-restart check, 2026-06-19 17:09 MSK:

- `openclaw gateway restart`: completed through normal restart recovery.
- `openclaw status --deep`: gateway reachable, app `2026.6.8`, Telegram OK, main session `gpt-5.5` / OpenAI Codex, `71k/272k` (`26%`).
- `openclaw models status --json`: allowed models are `openai/gpt-5.4`, `openrouter/qwen/qwen3-coder:free`, `openai/gpt-5.5`, `openrouter/google/gemma-4-26b-a4b-it:free`, `moonshot/kimi-k2.6`, `ollama/phi3:instruct`; `ollama/qwen2.5:3b` is absent.
- `openclaw config get auth.order --json`: `openai:stasiintegraleus@gmail.com` -> `openai:integraleus55@gmail.com`.
- `openclaw models auth order get --provider openai-codex`: legacy compatibility view reports `openai-codex:stasiintegraleus@gmail.com` -> `openai-codex:integraleus55@gmail.com`.
- `openclaw models fallbacks list`: only `ollama/phi3:instruct`.
- Repeated `scripts/heartbeat-token-limits.sh`: exit code `0`; no new matching limit/auth/fallback/context events.
- Known remaining issue: Discord token still causes repeated `401 Unauthorized` provider restarts in logs. Telegram is OK. Discord was left enabled until Stanislav chooses token replacement or disabling.

Follow-up check, 2026-06-19 17:18 MSK:

- `openclaw status --deep`: gateway reachable, app `2026.6.8`, Telegram OK, Discord OK, main session `gpt-5.5` / OpenAI Codex.
- `openclaw models status --json`: default/resolved model `openai/gpt-5.5`; fallback list only `ollama/phi3:instruct`; `ollama/qwen2.5:3b` absent from allowed models.
- `openclaw models auth order get --provider openai-codex`: `openai-codex:stasiintegraleus@gmail.com` -> `openai-codex:integraleus55@gmail.com`.
- `scripts/heartbeat-token-limits.sh` initially emitted a false `WARN` because multiline Telegram message text contained words like `fallback` and `claude`; adjusted the log filter to ignore markdown/list content from messages.
- Repeated `scripts/heartbeat-token-limits.sh`: exit code `0`; Codex accounts healthy, no session >80%, Claude auth/usage OK, no new matching limit/auth/fallback/context events.
- `codex --version`: `codex-cli 0.140.0`; `claude --version`: `2.1.179 (Claude Code)`.

## Discord Channel Disable

Started: 2026-06-19 17:51 MSK

- [x] Set `channels.discord.enabled=false` without deleting the token/settings
- [x] Validate OpenClaw config
- [x] Restart gateway cleanly
- [x] Verify Telegram remains OK
- [x] Verify Discord provider no longer restarts with `401 Unauthorized`
- [x] Send user-visible result

Result, 2026-06-19 17:54 MSK:

- `openclaw config get channels.discord.enabled`: `false`.
- `openclaw config validate`: config valid.
- Gateway restarted through normal restart recovery and resumed the interrupted main session.
- `openclaw status --deep`: gateway reachable, app `2026.6.8`, Telegram OK; active channels list no longer includes Discord.
- Log tail after the restart shows no new Discord `401 Unauthorized`; the remaining `401` lines are from before Discord was disabled.
