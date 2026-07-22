# Home Server Audit - 2026-06-11

Audit time: 2026-06-11 10:08-10:12 MSK  
Host: `openclaw-home`, Ubuntu 24.04.4 LTS, kernel `6.17.0-35-generic`, GEEKOM A6  
Scope: read-only local audit, no configuration changes applied.

## Checklist
- [x] System identity and uptime
- [x] Disk, memory, load
- [x] Network exposure and firewall
- [x] SSH hardening
- [x] OpenClaw gateway and logs
- [x] System services and failures
- [x] Updates/security posture
- [x] Findings and recommendations

## Overall Verdict

Home is operational and not resource-constrained. OpenClaw gateway is running locally on loopback, Telegram is OK, SSH is key-only, fail2ban is active, disk and RAM have plenty of headroom.

Main issues found:
1. Synology NFS mounts are failed because `192.168.68.103` is unreachable from Home.
2. `alpha.security.service` logs an LDAP connection error every second.
3. OpenClaw security audit reports one critical configuration risk around small fallback models with web/browser tools and no sandbox.
4. OpenClaw state/config posture is permissive: `~/.openclaw` is group-writable, full exec is enabled, `tools.fs.workspaceOnly=false`, secrets are still present in plaintext config.
5. OS and OpenClaw updates are available.

## Evidence

System health:
- Uptime during check: ~4-6 minutes after recent boot.
- Load: `0.83, 0.50, 0.22`.
- Memory: 11 GiB total, 2.8 GiB used, 8.7 GiB available, swap unused.
- Root filesystem: 937 GiB total, 54 GiB used, 836 GiB free, 6% used.
- Docker is running but has no active containers.
- SMART check could not be performed because `smartctl` is not installed.
- Temperature check could not be performed because `sensors` is not installed.

Network/firewall:
- LAN IP: `192.168.68.125/24` on `eno1`.
- Tailscale service is active, but the node is not currently usable in the tailnet: `BackendState=NoState`, no Tailscale IPs, `Self.Online=false`.
- Tailscale health reports inability to synchronize with the coordination server; `tailscale status` exits with `unexpected state: NoState`.
- `tailscale netcheck` shows UDP and IPv4 connectivity are available and nearest DERP is Warsaw, so the local network path is basically functional; the node state/auth needs attention.
- Gateway `192.168.68.1` responds normally.
- Synology `192.168.68.103` does not respond to ping; TCP checks to `2049` and `2222` time out.
- Direct route to Synology is correct: `192.168.68.103 dev eno1 src 192.168.68.125`.
- Neighbor/ARP state for `192.168.68.103` is `FAILED`; Home receives no L2 response for that IP.
- LAN ping sweep found live hosts including `.1`, `.101`, `.102`, `.104`, `.107`, `.108`, `.112`, `.125`, `.247`, `.248`, `.249`; `.103` is not alive.
- Full-subnet TCP probe for typical Synology/NFS/SSH/SMB ports (`5000`, `5001`, `2049`, `111`, `2222`, `445`) found no Synology candidate. `.107:5000` is Apple AirTunes, not DSM.
- Recheck at ~10:22 MSK: Synology is back online at `192.168.68.103`; ARP resolves to `00:11:32:a2:35:68`, ping succeeds with ~0.16-0.64 ms latency.
- Recheck ports on `192.168.68.103`: `2222`, `111`, `445`, `2049`, `5000`, `5001` open; `22` refused as expected for the configured SSH-on-2222 setup.
- RPC/NFS service list is visible on Synology, including `mountd`, `nfs` on `2049`, and `nlockmgr`.
- DSM HTTP on `5000` responds with nginx/Synology headers.
- NFS mounts did not auto-recover after the NAS returned; all `mnt-synology-*.mount` units remain `failed` from the earlier boot-time timeout until manually retried/reset.
- UFW is active: deny incoming, allow outgoing, deny routed.
- Allowed inbound includes LAN ranges, Tailscale `100.64.0.0/10`, HTTP/HTTPS, CUPS `631/tcp`, and `2222/tcp` from private ranges.
- Listening ports include SSH `22`, CUPS `631`, Alpha services `4572/4600/4949/4976/4983/8080/11010/11020`, rpcbind `111`, OpenClaw loopback `18789`, Ollama loopback `11434`, and local uvicorn `8787`.

SSH:
- `ssh.service` is active and enabled.
- Effective config: `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin without-password`, public key auth enabled.
- `fail2ban` is active with `sshd` jail; currently 0 failed and 0 banned.
- SSH listens on port `22` on all IPv4/IPv6 interfaces; UFW allows LAN/private ranges and Tailscale CGNAT range, but not arbitrary public IPv4 to port 22.
- UFW has `2222/tcp` allow rules from private ranges, but sshd currently listens on `22`, not `2222`.

OpenClaw:
- Gateway: systemd user service, enabled/running, current version `2026.6.1`.
- Bind: loopback only `127.0.0.1:18789`; probe OK.
- Dashboard: `http://127.0.0.1:18789/`.
- Telegram channel: OK.
- Event loop health: OK.
- Update available: `2026.6.5`.
- Plugin drift: `discord` active at `2026.5.12`, expected `2026.6.1`.
- `openclaw doctor` reports auth profile cooldown for one OpenAI profile and expired auth for `integraleus55@gmail.com`, though the current session is working through Codex runtime.

System services:
- Failed units:
  - `mnt-synology-Documents.mount`
  - `mnt-synology-homes.mount`
  - `mnt-synology-music.mount`
  - `mnt-synology-video.mount`
- The Documents mount failed by timeout mounting `192.168.68.103:/volume1/Documents`.
- Alpha services are active, but `alpha.security.service` logs every second: LDAP connection error, wrong user configured for LDAP connection.
- Journal size: 2.5 GiB, likely inflated by repeated Alpha.Security errors.

Updates:
- `apt list --upgradable` shows many pending package updates, including Docker, Node.js, NetworkManager, nftables, snapd, fwupd, GNOME packages, and Ubuntu Pro client.
- `unattended-upgrades.service` is active.
- System timers for apt daily and apt daily upgrade are enabled.

Security findings from `openclaw security audit --deep`:
- Critical: small fallback model `ollama/qwen2.5:3b` is configured with web/browser tools and sandbox off.
- Warn: `tools.fs.workspaceOnly=false`.
- Warn: full exec trust for `main` and `home-monitor`.
- Warn: `/home/stanislav/.openclaw` mode is `775`; recommended `700`.
- Warn: plugin install specs for codex/discord are unpinned.
- Warn: plaintext secret-bearing config fields in `openclaw.json`.

## Recommended Next Steps

High priority:
1. Check Synology power/network/IP (`192.168.68.103`) and only then retry NFS mounts. Current evidence points to the NAS being absent from the LAN segment: no ARP response, no ping, no NFS/DSM/SSH/SMB ports anywhere in `192.168.68.0/24`.
2. Fix or disable the Alpha.Security LDAP integration if LDAP is not intended; the current one-error-per-second loop should be stopped.
3. Harden OpenClaw small-model fallback: either remove `ollama/qwen2.5:3b` from fallback for untrusted chats, or deny web/browser tools for that model and enable sandboxing.

Medium priority:
1. Run OpenClaw update to `2026.6.5`, update the drifted `discord` plugin, then restart gateway cleanly.
2. Move OpenClaw secrets from plaintext config into SecretRefs.
3. Change `/home/stanislav/.openclaw` permissions to `700`.
4. Review whether `tools.fs.workspaceOnly=false` and full exec should remain enabled for normal operation.
5. Apply OS package updates during a maintenance window.

Nice to have:
1. Install `smartmontools` and `lm-sensors` for disk and thermal checks.
2. Add journal retention limits if logs keep growing.
3. Consider disabling public CUPS/HTTP/HTTPS if they are not intentionally exposed.
