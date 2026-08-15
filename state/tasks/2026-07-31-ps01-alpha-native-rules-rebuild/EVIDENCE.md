# EVIDENCE — PS01 Alpha Native Rules Rebuild

## Источники

Перед разработкой прочитаны обязательные источники из `TASK_PACKET.md`: product cheatsheet, live `asu-tp-hmi-checklist`, исправленный Alpha/SCADA prompt, правила создания Alpha.HMI элементов, `.omobj` guide, предыдущие PS01 README/EVIDENCE и отчёты parent/builder review, а также ТЗ v2.0 из inbound media.

## Команды и результаты

### Генерация

```bash
python3 state/tasks/2026-07-31-ps01-alpha-native-rules-rebuild/build_ps01_alpha_native_rules.py
```

Результат: проект создан в разрешённой рабочей зоне `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/`.

### Alpha tools discovery

Лог: `logs/alpha_tool_discovery.txt`.

Найдены `alpha.hmi.cli`, `alpha.hmi.viewer` и локальные директории Alpha-модулей, включая Alpha.Server, Alpha.HMI, Alpha.HMI.Alarms, Alpha.HMI.WebViewer, Alpha.Historian, Alpha.Reports, Alpha.Security, Alpha.Imitator.

### Compile/export

Логи:

- `logs/compile_normal.jsonl`: exit code `0`;
- `logs/compile_alarm.jsonl`: exit code `0`;
- `logs/compile_disabled.jsonl`: exit code `0`;
- `logs/compile_final_normal.jsonl`: exit code `0`.

Команда:

```bash
/opt/Automiq/Alpha.HMI/alpha.hmi.cli compile --solution-path /home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/PS01_AlphaNativeRules.hmi --output-folder /home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/build --output-format json --export-binom
```

### Viewer screenshots

Все screenshots были открыты визуально через image viewer перед финальным вердиктом.

- `screenshots/ps01_normal_viewer.png`: `1920 1080 2599 58875.3`.
- `screenshots/ps01_alarm_viewer.png`: `1920 1080 3674 58787.7`.
- `screenshots/ps01_disabled_viewer.png`: `1920 1080 2846 58777`.

Визуальный вывод: не пустые, читаемые, 4 насоса присутствуют. После замечания Станислава входной `PT` перенесён левее от блока `Н1`, длинная подпись `PS01_HDR_PRESS_IN 3.1 бар` заменена на короткую операторскую `P всас 3.1 бар`; повторный просмотр нормального, alarm и disabled/bad-quality screenshots не показывает наложения датчика на параметры насоса. После следующего замечания по центрированию надписей выровнены все приборы `LT/PT/FT`: текст внутри окружности переведён на центрированное поле шириной окружности, значения под датчиками центрированы относительно оси прибора и укорочены до `L`, `P всас`, `P нагн`, `Q`. Повторный просмотр normal/alarm/disabled screenshots подтверждает, что приборные надписи не уезжают влево. Оставлен `CONDITIONAL GO`, потому что live runtime модулей не доказан.

### Syntax validation

XML parse OK:

- `PS01_AlphaNativeRules.hmi`;
- `objects/MainForm.omobj`;
- `objects/PS01_PumpFaceplate.omobj`;
- `objects/PS01_PumpUnit.omobj`.

CSV row counts:

- `alarm-matrix.csv`: 15;
- `modbus-map.csv`: 93;
- `opcua-node-map.csv`: 93;
- `tag-map.csv`: 93.

JSON parse OK:

- `config/cascade-parameters.json`;
- `config/historian-plan.json`;
- `config/reports-plan.json`;
- `config/security-roles.json`;
- `server/alpha-server-contract.json`.

### ZIP

```bash
sha256sum /home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/PS01_AlphaNativeRules_Project_20260731.zip
unzip -t /home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/PS01_AlphaNativeRules_Project_20260731.zip
```

Результат:

- SHA-256: `f2cf50b5d7cf08273688385567c79982962d3a290783eb2e8e7e91b000d9955b`;
- `unzip -t`: errors нет.

После первичного builder pass parent review поправил тесную подпись у расходомера FT и пересобрал пакет через тот же генератор. После замечания Станислава дополнительно исправлен входной `PT`, пересобраны Viewer screenshots и ZIP. После замечания по центровке обновлён генератор `build_ps01_alpha_native_rules.py`, пересобраны native `.omobj`, binom, screenshots и ZIP.

### Forbidden names scan

Scan по output на устаревшие/current-forbidden названия: hits `0`.

Примечание: в `TASK_PACKET.md` есть запрещающие формулировки как часть требований; они не относятся к generated output.

## Boundary check

- `/opt/Automiq` configs/services не менялись.
- Existing PS01 output folders не изменялись.
- Production runtime не трогался.
- Писал только в output boundary и task artifact boundary.
