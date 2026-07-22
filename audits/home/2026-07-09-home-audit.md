# Home Server Audit - 2026-07-09

## Checklist
- [x] Baseline/context captured
- [x] OS, uptime, resources checked
- [x] OpenClaw status checked
- [x] Services and failed units checked
- [x] Network/listening ports checked
- [x] Firewall/SSH checked
- [x] Storage/mounts checked
- [x] Security/update signals checked
- [x] Findings and new changes summarized

## Notes

Audit time: 2026-07-09 09:59-10:04 MSK. Scope: read-only checks on
openclaw-home; no service restarts, package upgrades, firewall changes, config
edits, or Synology root-level changes.

## Current Posture

Home is healthy as a local trusted workstation/server: Ubuntu 24.04.4 on
GEEKOM A6, booted 2026-07-08 18:37 MSK, uptime ~15h 22m, load around
2.09/1.73/1.83, 58 GiB RAM with 47 GiB available, swap unused, root disk
102G/937G used (12%). OpenClaw gateway is reachable, loopback-only on
127.0.0.1:18789, Telegram accounts are connected, and Alpha BPR API/HMI BFF
are reachable locally.

## What Appeared New / Changed

- OpenClaw update is available: installed/gateway version 2026.6.10, npm update
  2026.6.11 available.
- `openclaw models fallbacks list` now returns `Fallbacks (0): none`. This
  conflicts with recorded STATE/DECISIONS expectation that main should fall
  back to `ollama/phi3:instruct` after Codex OAuth profile failover.
- User failed units appeared: `claude-token-refresh.service` and
  `snap.firmware-updater.firmware-notifier.service`.
- Claude token refresh failures are HTTP 403 code 1010 at 00:45, 02:46, and
  08:49 MSK; 04:47 and 06:48 runs skipped successfully because token was still
  valid. This is not currently blocking OpenClaw, but the failed unit remains.
- Tailscale is up (`openclaw-home` 100.114.189.16) but `tailscale status`
  reports: "Tailscale can't reach the configured DNS servers."
- Ollama now has `qwen3.5:9b` and `gemma4:e4b` installed in addition to
  `phi3:instruct`, `qwen2.5:3b`, `nomic-embed-text`, and `kimi-k2.7-code:cloud`.
  `nomic-embed-text` is the only currently loaded model.
- Alpha BPR stand is reachable, but HMI/BFF `readyz` still reports UI file
  `operator-reviewer-prototype.html`; recent work discussed an integrated HMI
  shell, so route/UI alignment should be checked before demos.
- `STATE.md` is stale in a few Home details: it still says 16 GB RAM / 6% disk
  and SSH `PasswordAuthentication yes` / `22 Anywhere`, while current checks
  show 58 GiB RAM, 12% disk, `passwordauthentication no`, and UFW does not open
  port 22 to the public internet.

## OpenClaw

- Gateway service: systemd user service installed/enabled/running, pid 4909.
- Bind/exposure: loopback only, 127.0.0.1:18789 and ::1:18789.
- CLI/gateway version: 2026.6.10.
- Channels: Telegram default and home-monitor enabled, running, connected.
- Sessions: 27 active in `openclaw status`; `home-monitor` is around 81%
  context. Main current direct session is fresh after thread rotation.
- Tasks: `openclaw tasks audit` returned 0 findings.
- Security audit: 0 critical, 5 warn, 2 info.

## Security Findings

- Medium: model fallback chain is empty. If both Codex OAuth profiles fail,
  current model routing may not degrade to `ollama/phi3:instruct` as intended.
- Medium: OpenClaw state dir `/home/stanislav/.openclaw` is group-writable
  (`775`). `openclaw doctor` recommends `chmod 700`.
- Medium: `openclaw doctor` reports plaintext secret-bearing fields in
  `openclaw.json` and recommends SecretRefs. I did not print secret values.
- Medium: OpenClaw security audit warns `tools.fs.workspaceOnly=false` and
  `exec.security=full` for main/home-monitor/local. This is consistent with a
  trusted personal assistant setup, but high impact if any group/user boundary
  becomes untrusted.
- Low: reverse proxy trusted proxies are not configured. Since gateway is
  loopback-only, this matters only if the Control UI is later exposed through a
  proxy.
- Low: 11 orphan transcript jsonl files exist under sessions; doctor can
  archive them with `openclaw doctor --fix`, but no cleanup was run.

## Network / Firewall / SSH

- Interfaces: LAN 192.168.68.125, Tailscale 100.114.189.16, AWG 10.8.1.19,
  Docker bridges 172.18.0.1 and 172.19.0.1.
- UFW: active, default deny incoming, allow outgoing, deny routed.
- UFW allows LAN/private/Tailscale ranges, public 80/443, and public CUPS 631.
  It does not explicitly allow public 22.
- SSH: active on 0.0.0.0:22 and [::]:22, but effective config shows
  `passwordauthentication no`, `kbdinteractiveauthentication no`,
  `permitrootlogin without-password`.
- SSH journal since midnight has no entries; fail2ban `sshd` jail active with
  0 failed and 0 banned.
- Public listeners include nginx 80/443, LDAP 389, CUPS 631, several Alpha
  services, Docker-published Postgres 54329, and RustDesk/remote desktop related
  ports. Firewall rules constrain most non-public surfaces to LAN/private
  ranges.

## Services / Logs

- System failed units: none.
- User failed units: `claude-token-refresh.service`,
  `snap.firmware-updater.firmware-notifier.service`.
- Running services include Alpha Platform stack, Alpha BPR home API/HMI/sim
  bridges, Docker, nginx, Ollama, OpenLDAP, RustDesk, Tailscale, fail2ban,
  CUPS, and OpenClaw gateway.
- Journal warning pattern: `alpha.security.agent` reports 23 Alpha Platform
  security violations every 5 minutes; likely expected stand noise but should be
  classified before any production/demo claim.
- Repeating non-critical desktop noise: `gcr-prompter` / gnome-keyring cannot
  open display; RustDesk periodically logs `cannot open display`.

## Storage / Mounts

- Root filesystem: ext4, 937G total, 102G used, 788G available, 12%.
- EFI: 1.1G total, 1% used.
- Synology NFS mounts present and mounted: Documents, video, music, homes,
  surveillance, PlexMediaServer, Lost. NAS volume is 7.3T total, 3.6T used, 49%.
- `/mnt/synology/Documents` mountpoint check returned success.

## Updates

- Apt upgradable packages: 26, including Docker compose plugin, Tailscale,
  tzdata, iproute2, mutter/libinput, and SSSD packages.
- Snap latest change: Firefox auto-refresh completed after the 2026-07-08
  reboot.
- System timers active for apt daily, apt daily upgrade, fwupd, logrotate,
  fstrim, etc.

## Alpha BPR / Local AI Quick Checks

- `curl http://127.0.0.1:5088/health` returned ok for `alpha-bpr` 0.1.0.
- `curl http://127.0.0.1:5095/readyz` returned ready; BPR base reachable.
- `curl -k https://127.0.0.1/alpha-bpr-hmi/readyz` returned ready.
- Docker: `alpha-bpr-postgres` and `n8n-postgres` healthy; `n8n-app` and
  `n8n-caddy` up.
- Ollama installed models: `gemma4:e4b`, `qwen3.5:9b`, `phi3:instruct`,
  `kimi-k2.7-code:cloud`, `qwen2.5:3b`, `nomic-embed-text`.

## Recommended Next Actions

1. Restore or intentionally revise the model fallback chain. Current runtime
   says no fallbacks, while memory expects `ollama/phi3:instruct`.
2. Decide whether to run `openclaw doctor --fix` for safe maintenance items
   only after reviewing its actions: state dir permissions, legacy state, orphan
   transcripts. Do not blindly apply if it might touch config/secrets.
3. Investigate Claude token refresh 403/1010. It may be Cloudflare/proxy/account
   related; current Claude login may still work, but the timer is noisy.
4. Check Tailscale DNS configuration, because Tailscale itself reports DNS
   reachability trouble.
5. Update `STATE.md` Home facts after approval: RAM/disk, SSH password auth,
   UFW exposure, OpenClaw version, Alpha services status, and current fallback
   state.
6. Before any Alpha BPR demo, align the HMI/BFF readyz UI path with the current
   integrated HMI shell or document why `operator-reviewer-prototype.html`
   remains the served route.
