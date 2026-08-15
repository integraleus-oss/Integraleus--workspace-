# PS01 Alpha-native compliance pass

Started: 2026-08-01 07:25 MSK

## Goal

Bring the PS01 pump-station project into compliance with the approved rule
`D-2026-08-01-01`: everything required by the TZ must be implemented with Alpha
Platform software, including the server-side project and HMI.

External HTML/JS/API pages are diagnostic only and must not be used as delivered
operator UI or acceptance evidence.

## Scope

- PS01 server-side project: Alpha.Server / Alpha.Domain or AccessPoint where needed.
- PS01 HMI: Alpha.HMI project served through Alpha.HMI.WebViewer.
- Native operator actions: pump start/stop, enable/disable, auto/manual, setpoint selection/write.
- Native monitoring: alarms, trends via alpha.hmi.charts, historian/archive via Alpha.Historian.
- Acceptance evidence: project files, module map, compile/deploy/runtime checks, screenshots, and an honest gap list.

## Checklist

- [x] Create task checkpoint before further implementation.
- [x] Inventory current PS01 Alpha-native artifacts and live deployment.
- [x] Map TZ requirements to Alpha Platform modules and tags.
- [x] Remove or quarantine external helper pages from the delivered operator path.
- [x] Implement/repair Alpha.Server tags for missing command/mode/setpoint nodes.
- [x] Implement/repair Alpha.HMI controls and faceplates for native operation.
- [ ] Implement/repair Alpha.HMI.Alarms, alpha.hmi.charts, Alpha.Historian/archive, Reports/Security/Imitator artifacts where required.
- [x] Deploy or stage through documented Alpha workflow.
- [x] Verify native HMI/WebViewer behavior with readback and screenshots for
  core controls.
- [x] Add repeatable acceptance probe for services, public HMI entities,
  Historian, Reports, Security service state, and static project hashes.
- [ ] Produce final evidence and explicit remaining blocker list.

## Current Facts

- Current public `commands.html` is a diagnostic helper only.
- Current project is not accepted as a TZ-compliant Alpha Platform project until
  the same functionality exists in Alpha Platform artifacts and runtime.
- Worktree was already dirty before this pass; unrelated changes must not be reverted.
- Alpha.Server live package was rebuilt through Alpha.DevStudio CLI from staged
  `ps01-mix01-mode-devstudio`, preserving the previous MIX01 server object and
  adding `PS01_MODE_AUTO` / `PS01_MODE_MANUAL`.
- Live Alpha.Server package hashes after deploy:
  - `alpha.server.cfg`: `d3b40d4f260cb503121a8ee07974f7338cb9c3a72a711a8aca722363fe54f906`
  - `Alpha.Server.json`: `d2146ec4db50ba7784e7ecb10815edb6e11bec5827c25fe511e287a26a872e92`
  - `history.json`: `99191f53f912c860723a36450231f89656aad31cde8b9eff15447c01de4be79b`
  - `history.xml`: `b77bf95373ddc1a78517c145f81a75813e2bb9d98b06ee3b6c7c8ed69078b6d3`
- Live backup before deploy:
  `backups/alpha-server-live-backup-before-ps01-native-mode-20260801T074328+0300.tar`.
- Native Alpha.Server readback after deploy:
  `PS01_MODE_AUTO=false`, `PS01_MODE_MANUAL=false`, `PS01_STATION_MODE=2`,
  `PS01_PRESS_SP=8.0`, `PS01_PUMPS_RUNNING=2`, `PS01_P1_RUN=true`.
- Manual/auto smoke through Alpha.Server:
  `PS01_MODE_MANUAL=true` was accepted as a pulse and changed
  `PS01_STATION_MODE` to `1`; `PS01_MODE_AUTO=true` changed it back to `2`.
- `alpha-bpr-ps01-bridge.service` now starts with `tag_count=95` and writes
  `snapshot_writes=95`, so the two mode tags are in the live bridge path.
- Alpha.HMI project compiles successfully with the native SetpointsForm controls
  added for manual/auto, pressure setpoint presets, and H1-H4 start/stop/
  enable/disable.
- Public Alpha.HMI.WebViewer websocket blocker was fixed by creating and
  enabling `ps01-webviewer-root.service` on port `18080`; nginx already proxies
  the public websocket path to that process.
- `ps01-webviewer-root.service`, `alpha.server.service`,
  `alpha-bpr-ps01-bridge.service`, and `alpha-bpr-mix01-bridge.service` are
  active.
- Public native HMI URL for this check:
  `https://alpha-bpr.31.10.95.23.sslip.io/ps01-scada/build/index.html?entity=SetpointsForm`.
- Public WebViewer smoke now shows
  `Соединение с Alpha.HMI.WebViewer установлено` with no browser console errors.
- Public HMI layout screenshot after Alpha-HMI-DEV geometry fix:
  `/home/stanislav/tmp/ps01-alpha-native-check/setpoints-layout-fixed.png`.
- Public HMI readback smoke for native manual/auto/setpoint controls:
  `Ручной` changed `PS01_STATION_MODE` to `1`; `Авто` changed it to `2`;
  `8.0 бар` restored `PS01_PRESS_SP` to `8`.
- Public HMI readback smoke for native H4 controls:
  `Пуск` changed `PS01_P4_RUN=false -> true` and
  `PS01_PUMPS_RUNNING=2 -> 3`; `Стоп` changed
  `PS01_P4_RUN=true -> false` and `PS01_PUMPS_RUNNING=3 -> 2`;
  `Запретить` changed `PS01_P4_READY=true -> false`; `Разрешить` restored
  `PS01_P4_READY=false -> true`.
- Public HMI command screenshot:
  `/home/stanislav/tmp/ps01-alpha-native-check/setpoints-p4-command-smoke.png`.
- External `commands.html` helper was quarantined from both the generated
  WebViewer `wwwroot` and public `/var/www/html/ps01-scada`; backups are in
  `backups/quarantined-external-helpers/`.
- Public diagnostic helper check:
  `https://alpha-bpr.31.10.95.23.sslip.io/ps01-scada/commands.html` now
  returns `404`, while native WebViewer `MainForm` and `SetpointsForm` return
  `200`.
- Clean public WebViewer smoke for native module windows:
  `PS01TrendsWindow`, `PS01ArchiveWindow`, and `PS01AlarmsWindow` render with
  `Соединение с Alpha.HMI.WebViewer установлено`, no browser errors, and no
  failed HTTP responses after adding an empty resource-root `index.html`.
- Clean module screenshots:
  `/home/stanislav/tmp/ps01-alpha-native-check/entity-PS01TrendsWindow-clean.png`,
  `/home/stanislav/tmp/ps01-alpha-native-check/entity-PS01ArchiveWindow-clean.png`,
  `/home/stanislav/tmp/ps01-alpha-native-check/entity-PS01AlarmsWindow-clean.png`.
- Repeatable acceptance probe:
  `state/tasks/2026-08-01-ps01-alpha-native-compliance/ps01_alpha_acceptance_probe.sh`.
- Latest probe output:
  `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731/logs/acceptance_probe_20260801_120303/SUMMARY.md`.
- Probe-confirmed service state at 2026-08-01 12:03 MSK:
  `alpha.server.service`, `alpha-bpr-ps01-simulator.service`,
  `alpha-bpr-ps01-bridge.service`, `alpha.historian.server.service`,
  `alpha.reports.service`, `alpha.security.service`,
  `alpha.security.useractivity.service`, and `ps01-webviewer-root.service`
  are active.
- Probe-confirmed public WebViewer endpoints return `200` for `MainForm`,
  `SetpointsForm`, `PS01TrendsWindow`, `PS01ArchiveWindow`,
  `PS01AlarmsWindow`, and `ReportsForm`.
- Probe-confirmed Alpha.Historian `stat` succeeds: version
  `4.1.1+b1.r143917`, `Config.Status=true`, license found `122/122`,
  default database state `4`, stored records `4459919`, insert failures `0`.
- Probe-confirmed Alpha.Reports service is active and HTTP `/` returns `200`;
  recent journal shows temporary license polling misses followed by
  `License received` and `license ok` states.
- Public `ReportsForm` WebViewer render screenshot:
  `/home/stanislav/tmp/ps01-alpha-native-check/entity-ReportsForm-20260801-probe.png`.

## Remaining Blockers

- Full acceptance still needs Alpha.HMI.Alarms acknowledgement/export and
  event-generation proof.
- alpha.hmi.charts windows render and Alpha.Historian `stat` proves a live
  server with stored records, but PS01-specific historical curve freshness is
  still not proven.
- Alpha.Reports is live and connected enough to serve the login/configurator
  page; actual PS01 report template import/generation/export remains open.
- Alpha.Security and UserActivity services are active and role contract exists;
  actual role enforcement against the PS01 HMI commands remains open.
- Final delivery package/sign-off remains open.
