# PS01 Alpha Native Rules Rebuild — TODO

## Scope

Сделать новый кандидат проекта PS01 на Альфа платформе, не патчить старый визуальный формат.

## Checklist

- [x] Создать task packet с правилами и границами.
- [x] Запустить controlled builder agent.
- [x] Получить новый Alpha-native пакет в отдельной рабочей зоне.
- [x] Проверить структуру, module status и evidence.
- [x] Открыть реальные viewer screenshots и провести HMI review.
- [x] Проверить ZIP, SHA-256, deprecated Alpha names scan.
- [x] Вернуть parent agent проверенный результат с честным `CONDITIONAL GO`.

## Result

- Verdict: `CONDITIONAL GO`
- ZIP: `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/PS01_AlphaNativeRules_Project_20260731.zip`
- SHA-256: `f2cf50b5d7cf08273688385567c79982962d3a290783eb2e8e7e91b000d9955b`
- Reports: `BUILDER_REPORT.md`, `EVIDENCE.md`

## Working Dirs

- Task: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-alpha-native-rules-rebuild/`
- Output: `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/`

## Follow-up Fix

- [x] 2026-07-31 10:33 MSK: исправлено наложение входного датчика `PT` на блок параметров `Н1`.
- [x] `PTIN` отнесён левее к всасывающему коллектору, длинная подпись заменена на короткую `P всас 3.1 бар`.
- [x] Проект пересобран, Viewer screenshots обновлены, ZIP перепакован и проверен через `unzip -t`.
- [x] 2026-07-31 10:46 MSK: исправлено центрирование надписей `LT/PT/FT` внутри окружностей и значений под датчиками.
- [x] Генератор проекта обновлён, выполнен полный rebuild: compile/export, normal/alarm/disabled Viewer screenshots, ZIP, `unzip -t`.
