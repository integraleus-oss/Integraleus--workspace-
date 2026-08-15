# MIX01 Working Project Video - 2026-07-29

## Checklist

- [x] Confirm Alpha product names from cheatsheet.
- [x] Find existing MIX01/Alpha.HMI runtime video or frame evidence.
- [x] Produce a short MP4 artifact for Telegram.
- [x] Visually inspect the output.
- [x] Send the video to Telegram topic 14.
- [x] User rejected static screenshot montage: needs visible changing numbers/functions.
- [x] Check live MIX01 WebViewer status.
- [x] Try non-root MIX01 WebViewer startup.
- [x] Start MIX01 WebViewer with explicit root permission from Stanislav.
- [x] Record real live WebViewer video with changing values and function navigation.
- [x] Visually inspect live video frame sheet.
- [x] Send corrected live video to Telegram topic 14.

## Output

- `mix01-alpha-hmi-working-project-20260729.mp4` - 14.5 s MP4 built from
  real MIX01 Alpha.HMI runtime screenshots.
- `checkframes/contact-sheet.png` - visual check frame sheet.
- Rejected for current request: this is static screenshot montage, not a
  live recording with changing values/functions.

## Live Recording Attempt

- `http://127.0.0.1/mix01/build/index.html` returns HTTP 200.
- `xwv-conf.js` points to WebSocket `127.0.0.1:8081`.
- Current listener check: `8081` is not listening; generic WebViewer process is
  running without visible `MIX01` argument.
- Non-root launch of `/opt/Automiq/Alpha.HMI.WebViewer/alpha.hmi.webviewer MIX01`
  compiles the project but fails to deploy to `/var/www/html/mix01/...` with
  `Permission denied`.
- Tried a user-writable `WwwRoot` copy under this task directory; the binary
  still used the system `/opt/.../alpha.hmi.webviewer.MIX01.xml` target and
  failed on `/var/www/html/mix01/...`.
- With explicit Telegram approval, started:
  `sudo -n setsid -f /opt/Automiq/Alpha.HMI.WebViewer/alpha.hmi.webviewer MIX01`
- `8081` became available and WebViewer logged: `Приложение запущено.`
- `mix01-alpha-hmi-live-functions-20260729.mp4` - 45 s live browser recording
  with changing `PLC HB` and navigation across recipe/setpoint, archive chart,
  and OPC/PLC diagnostics.
- `checkframes-live/functions-contact-sheet.jpg` - visual check frame sheet.
- Sent to Telegram topic 14 as message `2347`.
