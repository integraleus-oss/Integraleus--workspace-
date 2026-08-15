# PS01 operator controls gap

- [x] Locate TZ/operator requirements for pump start, manual/auto mode, and setpoints.
- [x] Inspect current published WebViewer/control pages and runtime API.
- [x] Add or expose operator controls only if they can be verified end-to-end.
- [x] Verify browser/runtime behavior and report honest status.
- [x] Fix mobile WebViewer operator-control layout so pump controls do not overlap the mnemonic.
- [ ] Replace the external HTML helper with native Alpha Platform implementation before treating the result as TZ-compliant.

## Hard Acceptance Rule

Everything required by the TZ must be implemented with Alpha Platform software,
including both the server-side project and HMI: Alpha.Server,
Alpha.Domain/AccessPoint, Alpha.HMI/WebViewer, Alpha.HMI.Alarms,
alpha.hmi.charts, Alpha.Historian, Alpha.Reports, Alpha.Security,
Alpha.Imitator, and documented Alpha workflow where applicable.

External HTML/JS/API helper pages are allowed only as temporary diagnostics or
test harnesses. They do not count as the operator project, do not close TZ
requirements, and must not be presented as the delivered Alpha Platform project.

Current blocker: `commands.html` proves some writes/readbacks through the public
API, but it is an external helper. Pump commands, auto/manual mode, setpoint
entry, server configuration, alarms, trends, historian/archive, reports, roles,
audit, and simulator behavior must be surfaced and verified through native Alpha
Platform artifacts before this task can be closed.

## 2026-08-01 06:50 MSK

- Source requirement checked: `CTRL-001` pump start/stop with confirmation, `CTRL-002` auto/manual mode change, `CTRL-003` setpoint write with readback.
- Updated public operator helper page: `https://alpha-bpr.31.10.95.23.sslip.io/ps01-scada/commands.html`.
- Updated runtime proxy: `/api/ps01-state`, `/api/ps01-command`, `/api/ps01-setpoint`, `/api/ps01-mode`.
- Verified public API:
  - `PS01_PRESS_SP` wrote `8.1`, read back `8.100000381469727`, then restored to `8.0`.
  - `P4 start` wrote `PS01_P4_CMD_START`, read back `PS01_P4_RUN=true`, `PS01_PUMPS_RUNNING=3`.
  - `P4 stop` wrote `PS01_P4_CMD_STOP`, read back `PS01_P4_RUN=false`, `PS01_PUMPS_RUNNING=2`.
  - `/api/ps01-mode?mode=manual` returns the intentional blocker: simulator supports `PS01_MODE_AUTO/MANUAL`, but current Alpha.Server deployment has no such nodes.
- Browser evidence: `evidence/ps01-commands-1440x900.png`.

## 2026-08-03 14:40 MSK

- User screenshot showed the injected pump-control faceplate overlapping the
  MainForm mnemonic in mobile browser.
- Target runtime file: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731/webviewer/local-webviewer-run/ps01-public-proxy.mjs`.
- Required check after edit: public `/ps01-webviewer/?entity=MainForm` in a
  mobile viewport; pump controls must not cover the central process schematic.
- Fixed by docking the injected pump-control panel below the whole MainForm
  (`top: 1140px`) instead of floating it over the mnemonic/right-side panels.
- Verified public HTML includes the new CSS and `/api/ps01-state` still returns
  Alpha.Server data successfully.
- Browser evidence:
  `/home/stanislav/Pictures/ps01-check/mobile-like-mainform-final.png` and
  `/home/stanislav/Pictures/ps01-check/tall-mainform-panel-final.png`.

## 2026-08-03 15:05 MSK

- Replaced the always-visible injected pump-control block with an on-demand
  pump faceplate in the public WebViewer runtime:
  `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731/webviewer/local-webviewer-run/ps01-public-proxy.mjs`.
- Operator flow now matches the requested behavior:
  click a pump marker on `MainForm` -> open the control panel for that pump.
- Pump command buttons are enabled only when `PS01_STATION_MODE=1` (manual).
  In automatic mode (`PS01_STATION_MODE=2`) the pump menu stays visible but
  `Пуск`, `Стоп`, and `Ремонт/Разреш.` are disabled and do not send commands.
- Restarted public WebViewer proxy on port `18082`; corrected
  `ps01-webviewer.pid` to the live node process `1353389`.
- Verified with Chromium/CDP on the public URL:
  - `MainForm` DOM contains 4 clickable pump markers.
  - Click `Н1` opens `Управление Н1`.
  - Manual mode: `Пуск`, `Стоп`, `Ремонт` enabled.
  - Automatic mode: the same pump buttons disabled.
  - Restored station to manual mode after the test.
  - Mobile viewport `430x932`: faceplate fits inside the viewport
    (`left=102`, `right=414`, `width=312`).
- Browser evidence:
  `/home/stanislav/Pictures/ps01-check/context-faceplate-manual.png`,
  `/home/stanislav/Pictures/ps01-check/context-faceplate-auto-disabled.png`,
  `/home/stanislav/Pictures/ps01-check/context-faceplate-mobile.png`.

## 2026-08-03 17:45 MSK

- User mobile screenshot showed `MainForm` still rendered with a desktop fixed
  width and only the left part visible on Android.
- Updated the public WebViewer proxy injection in
  `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731/webviewer/local-webviewer-run/ps01-public-proxy.mjs`.
- Mobile viewport handling now switches the HTML viewport to the HMI design
  width (`1220px`) and lets the browser scale the whole station form down to
  the phone width.
- Restarted the public PS01 proxy on port `18082`; current live PID is recorded
  in `ps01-webviewer.pid`.
- Verified public HTTPS route returns the updated code and local CDP mobile
  emulation reports `innerWidth=1220`, `visualScale=0.322`, no extra horizontal
  overflow beyond the HMI design width, and the `ps01-mobile-fit` class applied.
- Verified mobile click behavior after scaling: clicking H1 opens
  `Управление Н1`; in manual mode `Пуск`, `Стоп`, `Запретить` are enabled and
  `Сброс аварии` is disabled when there is no fault.
- Browser evidence: `/home/stanislav/ps01-mobile-cdp.png`.
