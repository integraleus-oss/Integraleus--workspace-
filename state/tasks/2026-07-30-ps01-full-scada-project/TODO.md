# PS01 full SCADA project package

## Goal
Build a runnable PS01 booster pump station SCADA package from the v2.0 spec:
server/simulator, web HMI control, alarms, trends/history, reports, docs, and
acceptance evidence.

## Scope
- 4 pumps H1..H4, cascade pressure control, up to 3 running + 1 reserve.
- Web HMI overview with manual/auto modes, confirmation, lockouts, alarms.
- Server-side simulator/tag API with command writeback and audit events.
- Time-series archive for key values and event/alarm journal.
- Trend view and report exports suitable for handoff/demo.
- Package must include run instructions, screenshot evidence, and ZIP.

## Checklist
- [x] Create task artifact/checklist.
- [x] Inspect existing Alpha BPR/webviewer project patterns.
- [x] Create runnable PS01 SCADA project files.
- [x] Implement server/simulator/history/commands.
- [x] Implement web HMI/trends/alarms/reports.
- [x] Run local smoke checks.
- [x] Capture real screenshot.
- [x] Build and test ZIP archive.
- [x] Send screenshot/archive to Telegram.

## Notes
- This will be a runnable demo/stand package unless a real licensed Alpha.Server
  environment is available in the workspace for native deployment.
- Use only current Alpha modules named in `docs/alpha_platform/PRODUCT_CHEATSHEET.md`.
- Smoke passed: `python3 tests/smoke.py` -> `PS01 full SCADA smoke: PASS`.
- Live HTTP checks passed for `/api/state`, `/api/history`, `/api/report/daily`,
  and confirmed mode commands.
- ZIP passed `unzip -t`: `outbound/ps01-full-scada-project-20260730.zip`.
- Latest geometry fix: pump inlet/outlet nozzles are visually tied to suction
  and discharge collectors.
- Archive SHA-256: `2b9611265578c1c4c31112884302a538a218d926aa2c55b41ad7681ffac1409e`.
- Local server is running in tmux session `ps01-scada` on `http://127.0.0.1:8051/`.
