# Task Packet: PS01 Full Alpha Platform Runtime Package

## Задача

Сделать новый полноценный пакет проекта PS01 по ТЗ v2.0 средствами Alpha Platform,
а не web/Python-имитацией и не одним Alpha.HMI-экраном.

## Источники правил

- `docs/alpha_platform/PRODUCT_CHEATSHEET.md`
- `skills/asu-tp-hmi-checklist/SKILL.md`
- локальные Alpha-документы и примеры из `/home/stanislav/work/alpha-hmi-dev`
- предыдущий кандидат `/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731`

## Область записи

- Task state: `state/tasks/2026-07-31-ps01-full-alpha-platform-runtime/`
- Output: `/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731/`
- Outbound mirror: `outbound/2026-07-31-ps01-full-alpha-platform-runtime/`

## Обязательные артефакты

- Alpha.HMI `.hmi/.omobj` проект с формами/вкладками: Обзор, Тренды, Архив, Аварии, Отчёты, Уставки.
- `.binom/.ni.binom` после `alpha.hmi.cli compile --export-binom`.
- Alpha.Server карта тегов, OPC UA NodeId, Modbus map, расчётные теги, команды.
- Alpha.HMI.Alarms матрица тревог, задержек, приоритетов, квитирования.
- Alpha.Historian план архивирования и source list для alpha.hmi.charts.
- Alpha.Reports определения пяти отчётов из ТЗ.
- Alpha.Security роли и матрица прав.
- Alpha.Imitator сценарии проверки каскада/АВР/аварий.
- Evidence: tool discovery, compile logs, viewer screenshots, XML/CSV/JSON checks, ZIP integrity, SHA-256.

## Честная граница

Не заявлять `GO` для модуля, если есть только config/contract и нет подтверждённого
runtime/import/write-readback на локальном стенде.
