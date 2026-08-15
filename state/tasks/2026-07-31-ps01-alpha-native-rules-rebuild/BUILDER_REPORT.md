# BUILDER_REPORT — PS01 Alpha Native Rules Rebuild

## Вердикт

**CONDITIONAL GO**.

Создан новый Alpha-native кандидат проекта PS01, не патч старого ZIP. Native Alpha.HMI часть скомпилирована через `alpha.hmi.cli`, получены и визуально открыты Viewer/Xvfb screenshots для нормального, аварийного и bad-quality/disabled состояний.

Статус не повышаю до `GO`, потому что Alpha.Server, Alpha.HMI.Alarms, Alpha.Historian, Alpha.Reports, Alpha.Security и Alpha.Imitator оформлены как контракты/планы: runtime import, live REGUL OPC UA/Modbus, write/readback, alarm ack, Historian write и Reports generation не доказаны без отдельного dev-стенда.

## Итоговый пакет

- Рабочая зона: `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/`
- ZIP: `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/PS01_AlphaNativeRules_Project_20260731.zip`
- SHA-256: `c5383b301d290d1c0d56e37c5844bbd4ace00563cb240a5a7070db50e745c810`
- HMI: `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/PS01_AlphaNativeRules.hmi`

## Созданные файлы

- Документы: `README.md`, `PROJECT_STATUS.md`, `ACCEPTANCE_CHECKLIST.md`, `MODULE_EVIDENCE.md`, `VISUAL_REVIEW.md`.
- Native Alpha.HMI: `PS01_AlphaNativeRules.hmi`, `objects/MainForm.omobj`, `objects/PS01_PumpUnit.omobj`, `objects/PS01_PumpFaceplate.omobj`.
- Build outputs: `build/PS01_AlphaNativeRules.binom`, `build/PS01_AlphaNativeRules.ni.binom`, `output/PS01_AlphaNativeRules.ni.binom`.
- Configs: `config/tag-map.csv`, `config/opcua-node-map.csv`, `config/modbus-map.csv`, `config/alarm-matrix.csv`, `config/historian-plan.json`, `config/reports-plan.json`, `config/security-roles.json`, `config/cascade-parameters.json`.
- Контракты модулей: `server/`, `alarms/`, `historian/`, `reports/`, `security/`, `imitator/`, `webviewer/`.
- Screenshots: `screenshots/ps01_normal_viewer.png`, `screenshots/ps01_alarm_viewer.png`, `screenshots/ps01_disabled_viewer.png`.

## Статус по модулям

| Модуль | Статус | Артефакт | Комментарий |
|---|---|---|---|
| Alpha.HMI | `native_hmi_compile_proven` | `.hmi`, `.omobj`, `build/` | compile/export успешен |
| Alpha.HMI.WebViewer | `contract_ready_import_blocked` | `webviewer/README.md` | production config не менялся |
| Alpha.Server | `contract_ready_import_blocked` | `server/alpha-server-contract.json` | live import/writeback не выполнялись |
| Alpha.HMI.Alarms | `contract_ready_import_blocked` | `config/alarm-matrix.csv` | ack/journal runtime не доказан |
| alpha.hmi.charts / Alpha.Historian | `contract_ready_import_blocked` | `config/historian-plan.json` | нижняя зона честно помечена как contract |
| Alpha.Reports | `contract_ready_import_blocked` | `config/reports-plan.json` | шаблоны требуют dev-стенд |
| Alpha.Security | `contract_ready_import_blocked` | `config/security-roles.json` | enforcement/audit не проверялись |
| Alpha.Imitator | `plan_only` | `imitator/alpha-imitator-scenarios.md` | сценарии есть, import format не подтверждён |

## Проверки

- Local Alpha module/tool discovery: выполнено, лог `logs/alpha_tool_discovery.txt`.
- Alpha.HMI compile/export:
  - normal: exit code `0`;
  - alarm: exit code `0`;
  - disabled/bad-quality: exit code `0`;
  - final normal source: exit code `0`.
- Viewer/Xvfb screenshots:
  - normal: `1920 1080 2608 58860.1`;
  - alarm: `1920 1080 3688 58772.5`;
  - disabled: `1920 1080 2856 58761.8`.
- CSV/JSON/XML syntax validation: успешно.
- ZIP integrity: `unzip -t` exit code `0`, compressed data errors нет.
- SHA-256 пересчитан после parent-поправок FT/коллекторной подписи и входного PT: `c5383b301d290d1c0d56e37c5844bbd4ace00563cb240a5a7070db50e745c810`.
- Deprecated/forbidden Alpha names scan по output: hits `0`.

## Визуальное ревью

Screenshots открыты визуально. Экран не пустой, не чёрный, содержит ровно 4 насосные ветки `Н1..Н4`, каскадную панель, таблицу очередности, приборы давления/расхода/уровня, alarm ticker и bad-quality блокировку.

Плюсы:

- насосы одинаковые, 4 экземпляра видны на мнемосхеме;
- нормальный режим спокойный серый, без ярко-зелёного доминирования;
- аварийный цвет зарезервирован для `Н4` и alarm zone;
- датчики PT/FT/LT привязаны к резервуару и коллекторам, не висят отдельно;
- подписи и значения помещаются в 1920x1080.
- parent review поправил тесную подпись у FT: подпись направления коллектора вынесена ниже линии, расход оформлен как `м³/ч`;

Оговорки:

- нижняя trend area не выдана за доказанный live `alpha.hmi.charts` widget, прямо помечена как contract;
- Viewer показывает системные полосы прокрутки вокруг окна, но содержимое HMI читаемо;
- live data quality, command blocking, alarm acknowledgement and transitions не доказаны.

## Блокеры

- Нет подключения к реальному REGUL RX00 и финальному OPC UA/Modbus export.
- Modbus registers не выдумывались: в `config/modbus-map.csv` стоит `TBD_REGUL_EXPORT_*`.
- Runtime import/config format для Alpha.Server/Alarms/Historian/Reports/Security/Imitator не подтверждён в этом проходе.
- Production `/opt/Automiq` configs/services не менялись по boundary.

## Следующее действие

Поднять непроизводственный Alpha dev-стенд, импортировать HMI, подключить подтверждённый REGUL RX00 GVL/OPC UA NodeId + Modbus map, затем пройти раздел 10 ТЗ: write/readback команд, alarm ack, Historian write, Reports generation, role enforcement, rotation/AVR/capacity-low сценарии через Alpha.Imitator или стенд ПЛК.
