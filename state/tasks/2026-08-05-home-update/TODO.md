# Home Update 2026-08-05

## Checklist

- [x] Preflight and package inventory
- [x] Apt upgrade
- [x] Tailscale upgrade
- [x] Autoremove obsolete packages
- [x] Global npm tools update
- [x] OpenClaw update
- [x] `openclaw doctor --fix`
- [x] Gateway restart
- [x] Final `openclaw status --deep`
- [x] Record reboot requirement

## Current State

- Apt upgrades completed at 09:11 MSK.
- Pending apt upgrades: 0.
- Reboot required by `amneziawg-dkms`.
- OpenClaw updated to `2026.7.1-2` and reports `npm · up to date · deps ok`.
- Discord OpenClaw plugin updated separately from `2026.6.10` to `2026.7.1`; the doctor hint for `@openclaw/discord@2026.7.1-2` pointed to a non-existent npm version.
- Global npm tools updated: `@openai/codex 0.146.0`, `@anthropic-ai/claude-code 2.1.222`, `corepack 0.35.0`, `npm 12.0.2`.
- Final checks: `dpkg --audit` clean, `systemctl --failed` clean, Telegram OK, gateway reachable/running.
- Secure Boot DBX firmware update intentionally left separate.

## Remaining Follow-Up

- Controlled reboot when convenient, because `/var/run/reboot-required.pkgs` lists `amneziawg-dkms`.
- Optional OpenClaw config hygiene from doctor: local agent fallback config, legacy Telegram state/orphan transcript archive, plaintext secrets migration, unpinned plugin specs.
