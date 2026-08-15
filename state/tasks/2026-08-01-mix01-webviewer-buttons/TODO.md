# MIX01 WebViewer Buttons Runtime Fix - 2026-08-01

## Goal

Fix or accurately diagnose why MIX01 public WebViewer buttons such as `Пуск` do not work at:

`https://alpha-bpr.31.10.95.23.sslip.io/mix01/build/index.html`

## Checklist

- [x] Capture current runtime state: services, ports, logs.
- [x] Inspect MIX01 HMI/source artifacts for button bindings and command tags.
- [x] Test public WebViewer click behavior with Chromium.
- [x] Verify command path blocker: live Alpha.Server has no `MIX01.*` nodes, so bridge fails before commands can round-trip.
- [x] Stage the smallest correct Alpha.Server fix without touching live `/opt`.
- [x] Apply the approved live fix.
- [x] Re-run smoke checks and record evidence.

## Boundaries

- Do not replace the native Alpha.HMI/WebViewer screen with a standalone web mock.
- Do not claim full Alpha Platform runtime unless button commands are proven end-to-end.
- Keep public URL stable unless a separate diagnostic URL is needed.

## Evidence

- `alpha-bpr-mix01-bridge.service` is repeatedly failing with `BadNodeIdUnknown`.
- Read-only browse of `opc.tcp://127.0.0.1:62544` shows `PS01` under `Application`, but no `MIX01`.
- MIX01 HMI source is `unit.Source.MIX01`; buttons write `Scada_Command_ID`,
  `Scada_Command_Code`, and `Scada_Command_Trigger`.
- Staged fix: `staging/ps01-mix01-devstudio/PS01_Server.omx` now contains both `PS01`
  (93 params) and `MIX01` (74 params), built successfully by DevStudio.
- Initial staged runtime output:
  `staging/ps01-mix01-devstudio/bin/local/PS01_Domain/ps01-server/Server/alpha.server.cfg`
  SHA-256 `52e8b7134fe3b4ca602e0d621c93a5fa5cd638807bd69e83821a5e99b872abb7`.
- Live `alpha.server.cfg` before deploy:
  SHA-256 `f6203c54a3d2c3fa5442fcc1b9223dc1c74f72733ac96c61d6a9580d8826be8e`.
- Staged `Alpha.Server.json` matches live:
  SHA-256 `d2146ec4db50ba7784e7ecb10815edb6e11bec5827c25fe511e287a26a872e92`,
  Instance Id `5e14f75a-2f3b-4e4f-84c8-a95baca1ed3e`.
- Live deployment backups:
  - `alpha-server-live-backup-20260801T064725+0300.tar`
  - `alpha-server-live-backup-before-ap-write-20260801T065156+0300.tar`
  - `alpha-server-live-backup-before-history-restore-20260801T070129+0300.tar`
  - `alpha-server-live-backup-before-known-good-cfg-20260801T070409+0300.tar`
  - `alpha-server-live-backup-before-merged-default-history-20260801T070549+0300.tar`
- Final live runtime package:
  - `alpha.server.cfg` SHA-256 `3a587d60ffa5f22afbe72508dd204cc7adf83c0e8c9fb9383d93e7fedcc3adcb`
  - `Alpha.Server.json` SHA-256 `d2146ec4db50ba7784e7ecb10815edb6e11bec5827c25fe511e287a26a872e92`
  - `history.json` SHA-256 `99191f53f912c860723a36450231f89656aad31cde8b9eff15447c01de4be79b`
  - `history.xml` SHA-256 `b77bf95373ddc1a78517c145f81a75813e2bb9d98b06ee3b6c7c8ed69078b6d3`
  - `alarms.json` SHA-256 `87c748a1065f9a601e0a2300ca1658a01f45deee9280a466ec4e65252da672ec`
  - `alarms.xml` SHA-256 `ca57bcb49a7bda986e6b062244bd4fa24f69b2d751f60802ff7faed565737561`
- Final staged `PS01_Server.omx` keeps WebViewer AP/TCP writes enabled on port 4388 and binds
  `HistoryModule` to `history.Historian.default`, matching the live Alpha.Historian database.
- Public Chromium WebViewer smoke passed:
  - `Пуск`: WebViewer sent command 2, `ID 66101 ACK 66101`, `Batch_Status 4`, `Batch_Step 4`.
  - `Стоп`: WebViewer sent command 5, `ID 66102 ACK 66102`, `Batch_Status 12`.
  - `Сброс`: WebViewer sent command 7, `ID 66103 ACK 66103`, `Batch_Status 0`, `Batch_Step 0`.
  - Screenshots: `public-webviewer-pusk-final-2.png`, `public-webviewer-stop-final-2.png`,
    `public-webviewer-reset-final-2.png`.
- Final health/service smoke:
  - `alpha.server.service`, `alpha-bpr-mix01-bridge.service`, `alpha-bpr-ps01-bridge.service`,
    `alpha-bpr-mix01-simulator.service`, `mix01-webviewer-root.service`, and
    `alpha.historian.server.service` are active.
  - `GET http://127.0.0.1:5088/health/ready` returns `200 Healthy`; historian check reported
    `195 readiness samples returned`.
  - PS01 readback through Alpha.Server: `PS01_P1_RUN=true`, `PS01_P1_READY=true`,
    `PS01_PUMPS_RUNNING=2`, `PS01_HEARTBEAT=56189`.
  - MIX01 final readback: `Scada_Command_ID=66103`, `Scada_Command_Code=7`,
    `Plc_Command_ID_Ack=66103`, `Plc_Command_Status=3`, `Plc_Command_ErrorCode=0`,
    `Batch_Status=0`, `Batch_Step=0`.
