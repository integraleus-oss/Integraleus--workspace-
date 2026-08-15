# TASK PACKET: PS01 Full Alpha Platform Project Candidate

## Язык и стиль

Отвечай и оформляй все отчёты **по-русски**.

Работай как Alpha/SCADA engineer controlled builder. Используй принятый системный промпт роли:

`/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-scada-engineer-prompt-alpha-review/scada-engineer-prompt-alpha-corrected.md`

Это не read-only review. Это controlled builder pass, но без production deploy и без изменения живых сервисов.

## Цель

Создать полноценный локально проверенный **кандидат проекта PS01 на Альфа платформе** по ТЗ v2.0:

`/home/stanislav/.openclaw/media/inbound/ТЗ_HMI_для_ИИ_агента_2---e88c5794-8d33-42d6-8783-d4ee2a4b5b97.md`

Проект: повысительная насосная станция PS01, 4 насосных агрегата Н1..Н4, каскадное поддержание давления, до 3 рабочих + 1 резерв, REGUL RX00, OPC UA основной протокол, Modbus TCP резервный, Alpha.Server + Alpha.HMI + Alpha.Reports как заявленный стек.

## Обязательные источники перед разработкой

Перед любыми выводами по продуктам и модулям Альфы прочитай:

- `/home/stanislav/.openclaw/workspace/agents/main/docs/alpha_platform/PRODUCT_CHEATSHEET.md`

Перед HMI-дизайном и ревью прочитай:

- `/home/stanislav/.openclaw/workspace/agents/main/skills/asu-tp-hmi-checklist/SKILL.md`

Перед повторным использованием существующих Alpha.HMI подходов изучи:

- `/home/stanislav/work/alpha-hmi-dev/TODO.md`
- `/home/stanislav/work/alpha-hmi-dev/docs/alpha_hmi_element_creation_rules_2026-07-30.md`
- `/home/stanislav/work/alpha-hmi-dev/docs/alpha_hmi_omobj_model_creation_guide.md`
- `/home/stanislav/work/alpha-hmi-dev/out/ps01_pump_station_cascade_native_20260729/README.md`
- `/home/stanislav/work/alpha-hmi-dev/out/ps01_pump_station_cascade_native_20260729/EVIDENCE.md`

Изучи предыдущий trial review, чтобы не повторить уже найденную ошибку:

- `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-alpha-scada-agent-ps01-trial/AGENT_REPORT_RU.md`
- `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-alpha-scada-agent-ps01-trial/PARENT_REVIEW.md`

Проверь доступные Alpha-инструменты локально:

- `/opt/Automiq/Alpha.HMI/alpha.hmi.cli`
- `/opt/Automiq/Alpha.HMI/alpha.hmi.viewer`
- `/opt/Automiq/Alpha.DevStudio/bin/devstudio.cli`
- наличие relevant modules under `/opt/Automiq`

## Рабочая зона

Создай и используй новую рабочую зону:

`/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/`

Не меняй существующие файлы вне этой папки, кроме записи отчёта/сводки сюда:

`/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-full-alpha-builder/`

Если нужен генератор, положи его внутрь новой рабочей зоны или в task folder. Не правь старые генераторы без отдельной причины.

## Что нужно сделать

### 1. Проектная структура

Создай пакет с понятной структурой, например:

- `README.md`
- `PROJECT_STATUS.md`
- `ACCEPTANCE_CHECKLIST.md`
- `MODULE_EVIDENCE.md`
- `config/tag-map.csv`
- `config/opcua-node-map.csv`
- `config/modbus-map.csv`
- `config/alarm-matrix.csv`
- `config/historian-plan.json`
- `config/reports-plan.json`
- `config/security-roles.json`
- `config/cascade-parameters.json`
- `docs/operator-guide.md`
- `docs/alarm-philosophy.md`
- `docs/cascade-algorithm.md`
- `docs/alpha-platform-handoff.md`
- `objects/` with native Alpha.HMI `.omobj` objects where feasible
- `PS01_FullAlpha.hmi`
- `build/` compile outputs if compile succeeds
- `logs/`
- `screenshots/`
- final ZIP package

### 2. HMI

Создай Alpha.HMI native candidate, не standalone web app.

Минимум:

- ровно 4 насоса Н1..Н4;
- одинаковая геометрия веток;
- давление нагнетания как главный operator value with SP, limits, deviation, quality/stale status;
- давление всаса, расход, уровень ёмкости в понятных точках измерения;
- панель каскада: N из 4, ведущий, next start, next stop, скорость ведущего, PRESS PV/SP/DEV, CAPACITY_LOW;
- таблица насосов: наработка, пуски, статус, разрешён/запрещён;
- состояния: run/ready/fault/local/vfd_fault/vfd_ready/enabled;
- faceplate placeholder или отдельный объект/форма для насоса, если feasible;
- нижний trend area для pressure + SP + running pump count, preferably via Alpha.HMI/alpha.hmi.charts if feasible; if not feasible, mark as placeholder honestly;
- alarm banner/ticker with active and unacknowledged state;
- normal screenshot and active alarm screenshot.

HPHMI constraints:

- спокойная серая HMI-палитра;
- не использовать насыщенный зелёный как главный нормальный режим;
- alarm colors only for alarm/abnormal states;
- state not by color alone;
- no decorative P&ID pseudo-realism;
- no labels/lines/sensors overlap;
- all sensor hookups must visibly connect to measured object/header.

### 3. Alpha module artifacts

Создай честные Alpha Platform artifacts/contracts for:

- **Alpha.Server**: tag groups, OPC UA source placeholder for REGUL RX00, Modbus fallback map, calculated tags, command writeback and reverse-readback contract.
- **Alpha.HMI**: native `.hmi` + `.omobj` files, compile/build evidence if possible.
- **Alpha.HMI.WebViewer**: config/notes for serving the native HMI through WebViewer if runtime proof is not feasible.
- **Alpha.HMI.Alarms**: alarm matrix with priority, delay, hysteresis, cause, consequence, operator action, acknowledgement behavior, event-vs-alarm split.
- **alpha.hmi.charts / Alpha.Historian**: historian plan and trend plan; mark exact implementation status honestly.
- **Alpha.Reports**: definitions for all 5 reports from TZ.
- **Alpha.Security**: role matrix and command/setpoint audit requirements.
- **Alpha.Imitator**: if feasible, create simulation plan or a local test-scenario contract. Do not call external PLC endpoints.

If exact import format for a module is not confirmed by local docs/examples, create a clearly labeled contract/plan and list the blocker. Do not invent opaque binary/config formats.

### 4. Acceptance and evidence

Create acceptance checklist covering all TZ section 10 items.

Run feasible checks:

- generate files;
- validate CSV/JSON syntax;
- ZIP integrity test;
- Alpha.HMI compile/export if feasible with local CLI;
- screenshot capture if viewer can run locally;
- static checks for outdated Alpha names and forbidden substitutions.

If a check cannot run, record:

- command attempted;
- error or missing precondition;
- impact;
- next step.

### 5. Final package

Create final package:

`/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/PS01_FullAlpha_Project_20260731.zip`

Include all generated docs/configs/HMI/build/evidence.

## Forbidden

- Do not deploy to production.
- Do not modify `/opt/Automiq` configs or services.
- Do not connect to real REGUL/PLC/OPC UA/Modbus endpoints.
- Do not present Python/browser/HTML/SQLite as the Alpha project.
- Do not invent current Alpha product/module names.
- Do not use deprecated names as current: standalone Alpha.Trends, Alpha.Alarms 3.30, Alpha.Developer.
- Do not send anything to Stanislav or external channels.
- Do not touch unrelated dirty files.

## Required output

Write final report in Russian:

`/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-full-alpha-builder/BUILDER_REPORT.md`

Report must include:

- final verdict: GO / CONDITIONAL GO / NO-GO;
- package path and ZIP SHA-256;
- module-by-module status;
- generated files;
- commands/checks run;
- screenshots/evidence produced;
- blockers and uncertainties;
- exact next step needed for a real Alpha handoff.

Also update:

`/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-full-alpha-builder/EVIDENCE.md`

with command outputs and artifact paths.

When done, return only a short completion note to the parent.
