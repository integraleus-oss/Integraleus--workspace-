# RustDesk Install - 2026-06-19

Target: install RustDesk on Ubuntu host so Windows can view/control the current Ubuntu desktop session.

Checklist:
- [x] Inspect OS/session/package state
- [x] Download official RustDesk client package
- [x] Install package and dependencies
- [x] Enable/start RustDesk service
- [x] Verify service status and capture Ubuntu RustDesk ID if available
- [x] Report Windows-side next steps

Notes:
- Host: Ubuntu 24.04.4 LTS, amd64
- RustDesk release selected: 1.4.7 from `rustdesk/rustdesk` GitHub releases
- Package: `/tmp/rustdesk-1.4.7-x86_64.deb`
- SHA256: `12f61bb5ceb10a708089903357bd1f98dcb618bd0ea56ec568aaf1713a38070a`
- Service: `rustdesk.service` enabled and active
- RustDesk ID: `232083379`
- Current desktop session: GNOME on Wayland, active local seat `tty2`
- Tailscale: active, host IP `100.114.189.16`
- UFW: active; LAN/Tailscale private ranges allowed
- Unattended password: configured, not stored in this file
- Reported to Stanislav in Telegram message `1194`
- Follow-up: first connection showed black screen because GNOME session was locked. Unlocked session, disabled GNOME autolock (`lock-enabled=false`, `idle-delay=0`), restarted RustDesk/desktop portal. Stanislav confirmed connection works in Telegram message `1203`.
- Persisted in `STATE.md` under GEEKOM A6/openclaw-home in response to Telegram message `1204`.
