# EVIDENCE

Status: complete.

## Artifacts

- `TASK_PACKET.md`
- `SECURITY_PRECHECK.md`
- `ROLLBACK.md`
- `EVIDENCE.md`

## Verification log

- A1–A10 captured on `openclaw-home`; full synthesis is `/opt/smarthome/REPORT.md`.
- New containers: `sh-mosquitto`, `sh-homeassistant`; both running with `unless-stopped` after compose restart.
- MQTT authenticated publish/sub: passed; anonymous subscription: rejected (`RC=5`, not authorised).
- HA HTTP: 302 onboarding redirect on LAN and Tailscale endpoints.
- Backup tar validation: passed; systemd timer enabled/active for 04:00 MSK; oneshot result success.
- Accepted backup target: `/mnt/synology/Documents/backups/smarthome/`.
- Ollama short generation: `qwen2.5:3b`, 100% CPU.
- Swap remains an open read-only observation item; no swap clearing or tuning was authorized.
- Existing 11 container IDs checked unchanged and still running after deployment.
- Secret content was not recorded; `/opt/smarthome/.secrets` mode 600.
