# TASK PACKET: PS01 Alpha Native Rules Rebuild

## Язык

Все отчёты, чеклисты и пользовательские документы — **по-русски**.

## Контекст

Предыдущий проход доказал, что native Alpha.HMI пакет можно создать и скомпилировать, но визуальный формат получился не тем: агент выбрал собственную компоновку, местами с тесными подписями, placeholder values и слабой операторской графикой.

Теперь задача другая: **сделать новый проект**, используя правила, стандарты, примеры и guardrails, уже заложенные в текущем агенте. Не исправлять косметически старый экран.

## Цель

Создать новый Alpha-native кандидат проекта PS01 по ТЗ v2.0 для 4-насосной повысительной станции:

- 4 насоса `Н1..Н4`;
- каскадное поддержание давления;
- до 3 рабочих + 1 резерв;
- REGUL RX00;
- OPC UA основной источник;
- Modbus TCP резервный источник;
- Alpha Platform stack: Alpha.Server, Alpha.HMI, Alpha.HMI.WebViewer, Alpha.HMI.Alarms, alpha.hmi.charts, Alpha.Historian, Alpha.Reports, Alpha.Security, Alpha.Imitator.

Результат должен быть кандидатом проекта на Альфа платформе, а не web/Python/HTML имитацией.

## Обязательные источники

Перед разработкой прочитать:

1. `/home/stanislav/.openclaw/workspace/agents/main/docs/alpha_platform/PRODUCT_CHEATSHEET.md`
2. `/home/stanislav/.openclaw/workspace/agents/main/skills/asu-tp-hmi-checklist/SKILL.md`
3. `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-scada-engineer-prompt-alpha-review/scada-engineer-prompt-alpha-corrected.md`
4. `/home/stanislav/work/alpha-hmi-dev/docs/alpha_hmi_element_creation_rules_2026-07-30.md`
5. `/home/stanislav/work/alpha-hmi-dev/docs/alpha_hmi_omobj_model_creation_guide.md`
6. `/home/stanislav/work/alpha-hmi-dev/out/ps01_pump_station_cascade_native_20260729/README.md`
7. `/home/stanislav/work/alpha-hmi-dev/out/ps01_pump_station_cascade_native_20260729/EVIDENCE.md`
8. `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-full-alpha-builder/PARENT_REVIEW.md`
9. `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-full-alpha-builder/BUILDER_REPORT.md`

Use the ТЗ from inbound media if available:

`/home/stanislav/.openclaw/media/inbound/ТЗ_HMI_для_ИИ_агента_2---e88c5794-8d33-42d6-8783-d4ee2a4b5b97.md`

If the file path differs, locate it with `find /home/stanislav/.openclaw/media/inbound -name '*HMI*агента*2*.md'`.

## Visual Contract

The HMI must follow the current local rules, not invent a new presentation style:

- operator HMI, not decorative P&ID;
- sparse gray HPHMI layout;
- alarm colors only for abnormal/alarm states;
- normal running state must not dominate the screen with bright green;
- state must not rely on color alone;
- exactly four identical pump branches;
- no extra uncontrolled valves/fittings unless the ТЗ has a tag/operator reason;
- sensor hookups must land on measured objects/headers;
- no pipe through text, sensor, pump, tank, or unrelated object;
- labels and values must fit and align in 1920x1080 screenshots;
- Russian labels must have enough room;
- lower trend area must be honest: real alpha.hmi.charts if implemented, otherwise clearly labeled as not runtime-proven.

Use the earlier cleaner PS01/Alpha examples only as **style/reference material**, not as source to mutate in place.

Reference candidates:

- `/home/stanislav/work/alpha-hmi-dev/out/ps01_pump_station_cascade_native_20260729/`
- `/home/stanislav/work/alpha-hmi-dev/out/alpha_hmi_v2_baseline_library/`
- `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_project_20260731/` only for evidence of what to avoid and what to preserve technically.

## Work Boundary

Write only under:

- `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731/`
- `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-alpha-native-rules-rebuild/`

Do not modify:

- `/opt/Automiq` configs or services;
- existing PS01 output folders;
- production Alpha.Server/Historian/Reports/Security runtime;
- unrelated dirty files.

## Required Deliverables

Create at minimum:

- `README.md`
- `PROJECT_STATUS.md`
- `ACCEPTANCE_CHECKLIST.md`
- `MODULE_EVIDENCE.md`
- `VISUAL_REVIEW.md`
- `PS01_AlphaNativeRules.hmi`
- native `.omobj` files under `objects/`
- compile outputs under `build/` if compile succeeds
- `config/tag-map.csv`
- `config/opcua-node-map.csv`
- `config/modbus-map.csv`
- `config/alarm-matrix.csv`
- `config/historian-plan.json`
- `config/reports-plan.json`
- `config/security-roles.json`
- `config/cascade-parameters.json`
- Alpha module contracts under `server/`, `alarms/`, `historian/`, `reports/`, `security/`, `imitator/`, `webviewer/`
- screenshots:
  - normal state;
  - active alarm state;
  - if feasible, disabled/local/bad-quality state.
- final ZIP: `PS01_AlphaNativeRules_Project_20260731.zip`

## Required Checks

Run and record evidence:

- local Alpha module/tool discovery;
- `alpha.hmi.cli compile --export-binom` or exact feasible compile command;
- Alpha.HMI Viewer screenshot capture through Xvfb or equivalent;
- CSV/JSON/XML syntax validation;
- `unzip -t` for final ZIP;
- SHA-256 for final ZIP;
- scan for deprecated/current-forbidden Alpha names;
- screenshot visual review against the HPHMI checklist.

Open screenshots and inspect them before reporting success. A compile-only project with unreadable HMI is **NO-GO**.

## Alpha Module Honesty

Use only current modules from `PRODUCT_CHEATSHEET.md` as current Alpha components.

If exact import/runtime proof is unavailable for Alpha.Server, Alpha.HMI.Alarms, Alpha.Historian, Alpha.Reports, Alpha.Security, or Alpha.Imitator, create a contract/plan artifact and mark status honestly:

- `runtime_proven`
- `native_hmi_compile_proven`
- `contract_ready_import_blocked`
- `plan_only`
- `not_done`

Do not invent binary formats, import formats, live PLC addresses, license capabilities, or successful runtime deployment.

## Forbidden

- No standalone web/Python/HTML project as the main deliverable.
- No fake live REGUL/OPC UA/Modbus connection.
- No production deploy.
- No deprecated Alpha product names as current modules.
- No “looks fine” without screenshot inspection.
- No final package if HMI has obvious overlaps, cropped labels, floating sensors, wrong pump count, or unreadable value areas.

## Final Report

Write:

- `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-alpha-native-rules-rebuild/BUILDER_REPORT.md`
- `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-ps01-alpha-native-rules-rebuild/EVIDENCE.md`

Report must include:

- verdict: `GO`, `CONDITIONAL GO`, or `NO-GO`;
- package path and SHA-256;
- generated files;
- Alpha module-by-module status;
- checks run;
- screenshots and visual review;
- blockers;
- exact next action for real Alpha handoff.

Return to parent only a short Russian completion note.
