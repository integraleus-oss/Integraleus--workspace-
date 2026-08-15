# Evidence — PS01 Full Alpha Builder

Дата выполнения: 2026-07-31 09:56 MSK / 06:56 UTC.

## Артефакты

- Рабочая зона: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/`
- HMI проект: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/PS01_FullAlpha.hmi`
- ZIP: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/PS01_FullAlpha_Project_20260731.zip`
- ZIP SHA-256: `91e840bae37b9f4f5ec74f0d09c907b14a2c439629165ea5a2333877bf33c426`
- run report: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/run_report.json`

## Команды и результаты

### Alpha.HMI compile/export — alarm state

```bash
/opt/Automiq/Alpha.HMI/alpha.hmi.cli compile --solution-path /home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/PS01_FullAlpha.hmi --output-folder /home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/build --output-format json --export-binom
```

Результат: exit code `0`. Лог: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/logs/compile_alarm.jsonl`.

Ключевые строки лога:
- `< Компиляция завершилась успешно >`
- `< Экспорт проекта в binom завершился успешно >`
- warning: `PS01_PumpFaceplate` не используется в проекте; это ожидаемый faceplate placeholder.

### Alpha.HMI compile/export — normal state

```bash
/opt/Automiq/Alpha.HMI/alpha.hmi.cli compile --solution-path /home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/PS01_FullAlpha.hmi --output-folder /home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/build --output-format json --export-binom
```

Результат: exit code `0`. Лог: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/logs/compile_normal.jsonl`.

Ключевые строки лога:
- `< Компиляция завершилась успешно >`
- `< Экспорт проекта в binom завершился успешно >`
- warning: `PS01_PumpFaceplate` не используется в проекте; это ожидаемый faceplate placeholder.

### Viewer screenshots

- Alarm state: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/screenshots/ps01_alarm_viewer.png` — `1600 900 3583 59620.1`.
- Normal state: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/screenshots/ps01_normal_viewer.png` — `1600 900 3508 59688.5`.

### ZIP integrity

```bash
unzip -t /home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/PS01_FullAlpha_Project_20260731.zip
```

Результат: exit code `0`, `No errors detected in compressed data`.

### Static checks

- CSV parsed: `{'alarm-matrix.csv': 25, 'modbus-map.csv': 94, 'opcua-node-map.csv': 102, 'tag-map.csv': 107}`.
- JSON parsed: `5` files.
- XML parsed: `9` files.
- Forbidden deprecated/current-name hits: `[]`.

### Tool/module discovery

- `/opt/Automiq/Alpha.HMI/alpha.hmi.cli --help`: available, commands `compile`, `extract`.
- `/opt/Automiq/Alpha.HMI/alpha.hmi.viewer`: available and used for screenshots via Xvfb.
- `/opt/Automiq/Alpha.DevStudio/bin/devstudio.cli --help`: installed, but headless call failed with `XOpenDisplay failed`; recorded in `logs/tool_check_devstudio_cli.txt`.
- `/opt/Automiq` contains relevant modules: Alpha.Server, Alpha.HMI, Alpha.HMI.WebViewer, Alpha.HMI.Alarms, Alpha.Historian, Alpha.Reports, Alpha.Security, Alpha.Imitator.

## Файлы пакета

- `ACCEPTANCE_CHECKLIST.md`
- `MODULE_EVIDENCE.md`
- `PROJECT_MANIFEST.json`
- `PROJECT_STATUS.md`
- `PS01_FullAlpha.hmi`
- `PS01_FullAlpha_Project_20260731.zip`
- `README.md`
- `TODO.md`
- `alarms/alpha-hmi-alarms-contract.md`
- `build/PS01_FullAlpha.binom`
- `build/PS01_FullAlpha.ni.binom`
- `config/alarm-matrix.csv`
- `config/cascade-parameters.json`
- `config/historian-plan.json`
- `config/modbus-map.csv`
- `config/opcua-node-map.csv`
- `config/reports-plan.json`
- `config/security-roles.json`
- `config/tag-map.csv`
- `docs/alarm-philosophy.md`
- `docs/alpha-platform-handoff.md`
- `docs/cascade-algorithm.md`
- `docs/operator-guide.md`
- `evidence/MainForm_alarm_state.omobj`
- `historian/alpha-historian-contract.md`
- `imitator/alpha-imitator-test-scenarios.md`
- `logs/compile_alarm.jsonl`
- `logs/compile_normal.jsonl`
- `logs/ps01_alarm_viewer_viewer.log`
- `logs/ps01_alarm_viewer_xvfb.log`
- `logs/ps01_normal_viewer_viewer.log`
- `logs/ps01_normal_viewer_xvfb.log`
- `logs/tool_check_devstudio_cli.txt`
- `logs/unzip_test.txt`
- `objects/MainForm.omobj`
- `objects/PS01_CentrifugalPump.omobj`
- `objects/PS01_DischargeLine.omobj`
- `objects/PS01_FlowTransmitter.omobj`
- `objects/PS01_InletGateValve.omobj`
- `objects/PS01_LevelTransmitter.omobj`
- `objects/PS01_PumpFaceplate.omobj`
- `objects/PS01_Tank.omobj`
- `output/PS01_FullAlpha.ni.binom`
- `reports/alpha-reports-definitions.md`
- `run_report.json`
- `screenshots/ps01_alarm_viewer.png`
- `screenshots/ps01_normal_viewer.png`
- `security/alpha-security-contract.md`
- `server/alpha-server-contract.json`
- `webviewer/README.md`
