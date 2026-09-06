# TASK PACKET — openclaw-home smart-home baseline

- Owner: Stanislav
- Target: `openclaw-home` (`192.168.68.125`, `100.114.189.16`)
- Goal: audit A1–A10, then deploy Mosquitto + Home Assistant without affecting existing services.
- Risk: HIGH (remote host, Docker deployment, system timer, secret, NAS write).
- Approval basis: explicit technical specification received 2026-08-28.
- Source of truth: `/opt/smarthome/` on `openclaw-home`; evidence mirror in this task folder.

## Boundaries

- Do not stop/delete/reconfigure existing containers or services.
- Do not change host networking, netplan, firewall, existing ports, or Ollama configuration.
- No reboot, `apt full-upgrade`, package installation, InfluxDB/Grafana, or Zigbee2MQTT start.
- Resolve conflicts only by changing ports of the new stack.
- Never print or copy the MQTT password into logs/reports/chat.
- Synology access stays inside the home LAN; only the requested backup directory/test archive may be written.

## Checklist

- [x] Capture `docker ps` before state.
- [x] Complete and record A1–A10 read-only audit.
- [x] Choose conflict-free ports and document deviations.
- [x] Create `/opt/smarthome` structure and configs.
- [x] Generate MQTT secret directly on Home with mode 600.
- [x] Start only `sh-mosquitto` and `sh-homeassistant`.
- [x] Add disabled Zigbee2MQTT stub; do not start it.
- [x] Create and test NAS backup + 04:00 systemd timer.
- [x] Verify MQTT authenticated/anonymous behavior.
- [x] Verify HA over LAN and Tailscale.
- [x] Restart only the new compose project and re-check.
- [x] Compare existing containers before/after.
- [x] Finish `/opt/smarthome/REPORT.md` and evidence mirror.

## Acceptance / blocker behavior

- Stop before installation if SSH/sudo is unavailable, disk is insufficient, Docker Compose v2 is absent, or required host ports/network assumptions are unsafe.
- Do not install missing audit utilities; record them as unavailable.
- No commit requested; workspace evidence remains uncommitted unless separately requested.
