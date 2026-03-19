# Альфа платформа — Полный индекс базы знаний

> **Как пользоваться:** читай этот файл, чтобы найти нужный раздел документации.
> Путь к этому файлу: `docs/alpha_platform/INDEX.md`

## 1. Конспекты модулей (краткие, структурированные)

Для быстрого ответа на вопросы — сначала смотри сюда:

| Модуль | Файл | Размер | Что внутри |
|--------|-------|--------|------------|
| Alpha.Server (35 подмодулей) | `alpha_server_notes.md` | 25K | Ядро платформы: сигналы, OPC UA/DA, Modbus, SNMP, IEC 60870-5-104/101, IEC 61850, БД, журналирование, кластер, резервирование |
| Alpha.HMI 2.0 | `alpha_hmi_notes.md` | 5.5K | Мнемосхемы, виджеты, анимации, навигация, справочник элементов |
| Alpha.HMI.WebViewer 2.0 | `alpha_hmi_webviewer_notes.md` | 3K | Веб-доступ к мнемосхемам, AdminConsole, HMI.Alarms |
| Alpha.DevStudio 4.1 | `alpha_devstudio_notes.md` | 6.4K | IDE: проекты, компиляция, отладка, деплой, CLI |
| Alpha.Domain | `alpha_domain_notes.md` | 1.8K | Информационная модель, типы объектов |
| Alpha.Historian 4.0 | `alpha_historian_notes.md` | 2.8K | Архивирование, сжатие, запросы истории, агрегация |
| Alpha.Alarms 3.30 | `alpha_alarms_notes.md` | 7.2K | Тревоги, квитирование, подавление, аналитика, фильтрация |
| Alpha.Diagnostics 2.2 | `alpha_diagnostics_notes.md` | 2.2K | Диагностика компонентов платформы |
| Alpha.Reports, Om, Security, AccessPoint, Imitator, RMap, Tools, Trends | `alpha_other_modules_notes.md` | 16K | 8 модулей: отчёты, скрипты, безопасность, АРМ оператора, имитация, интерактивная карта, утилиты, тренды |

**Итого конспектов:** 50 модулей покрыты, ~70K текста

## 2. Полный текст документации (сырой, по диапазонам страниц)

Для глубоких ответов, цитат и деталей:

| Файл | Страницы | Строк | Примерное содержание |
|------|----------|-------|----------------------|
| `AlphaPlatform_7-32_text.md` | 7–32 | 630 | Введение, общее описание платформы |
| `AlphaPlatform_32-61_text.md` | 32–61 | 700 | Основные концепции, архитектура |
| `AlphaPlatform_62_1018_text.md` | 62–1018 | 33.8K | Alpha.Server, коммуникации, сигналы |
| `AlphaPlatform_1018-2000_text.md` | 1018–2000 | 30.6K | Alpha.HMI, мнемосхемы, виджеты |
| `AlphaPlatform_2000_3000_text.md` | 2000–3000 | 31.9K | Alpha.HMI продолжение, Alpha.Alarms |
| `AlphaPlatform_3000_4000_text.md` | 3000–4000 | 32.3K | Alpha.DevStudio, Alpha.Domain |
| `AlphaPlatform_4000_4500_text.md` | 4000–4500 | 12.7K | Alpha.Historian |
| `AlphaPlatform_4500_5000_text.md` | 4500–5000 | 17.4K | Alpha.Reports, Alpha.Security |
| `AlphaPlatform_5000_5500_text.md` | 5000–5500 | 18.6K | Alpha.AccessPoint, Alpha.Diagnostics |
| `AlphaPlatform_5500_6000_text.md` | 5500–6000 | 14.9K | Alpha.Imitator, Alpha.RMap, Alpha.Tools |
| `AlphaPlatform_6000_end_text.md` | 6000–конец | 20.4K | Alpha.Om, Alpha.Trends, глоссарий |
| `AlphaPlatform_главы_text.md` | — | 326 | Оглавление всех глав/модулей |

**Итого:** ~219K строк, ~12 МБ текста

## 3. Дополнительные документы

| Файл | Описание |
|------|----------|
| `Alpha_Basic_Course_text.md` | Базовый учебный курс (395K) |
| `Alpha_New_2024_2025_text.md` | Новинки версий 2024-2025 (15K) |
| `Alpha_vs_Competitors.md` | Сравнение с MasterSCADA 4D, SCADA Лацерта и др. (12K) |
| `TZ_Requirements_Alpha.md` | ТЗ на требования к платформе (10K) |

## 4. Лицензирование и ТКП

Путь: `/root/.openclaw/workspace/data/licensing_automiq/`

| Файл | Описание |
|------|----------|
| `tariff_quick_index_2026.md` | Краткий тарифный индекс |
| `tariff_sku_full_index_2026.csv` | Полный SKU-индекс (CSV) |
| `rules_hard_checks.md` | Жёсткие правила расчёта лицензий |
| `rules.md` | Общие правила лицензирования |
| `quote_template.md` | Шаблон КП |

⚠️ **Перед расчётом ТКП** обязательно прочитай: `playbooks/PRESELL_FASTLANE.md`, `playbooks/EDGE_CASES.md`, `rules_hard_checks.md`

## 5. Кейсы расчётов

Путь: `memory/alpha_platform/cases/` (вне sandbox — доступ через exec)

- `case-2026-03-01-scada5700-hist1710.md` — SCADA 5700 + Historian 1710
- `case-2026-03-04-family-preselection.md` — преселекция семейства

## 6. Шаблоны и роли для контента

| Файл | Описание |
|------|----------|
| `website/spectech/BLOG_ROLE.md` | Роль «Автоматчик» — статьи для инженеров АСУ ТП |
| `website/spectech/BLOG_ROLE_DEV.md` | Роль «Разработчик» — статьи для разработчиков ПО |

## 7. Опросник для клиентов

Путь: `memory/alpha_platform/templates/` (вне sandbox — доступ через exec)

- `Опросник_ТКП_Alpha.docx`
- `Опросник_ТКП_Alpha.xlsx`

---

## 7. Релизы и обновления

| Период | Файл | Что внутри |
|--------|-------|------------|
| Q1 2026 (янв–март) | `releases_2026_Q1.md` | Краткий анализ Q1 2026: топ-9 изменений для руководства. |
| **Полный архив янв 2025 – март 2026** | `releases_full_2025_2026.md` | 223 письма, 14 месяцев. Топ-15 изменений, 7 breaking changes, 9 новых модулей. Хронология по 8 компонентам. Таблица рекомендаций с приоритетами. |

---

## Как искать информацию

1. **Быстрый ответ** → конспекты (раздел 1)
2. **Детали/цитаты** → полный текст по нужному диапазону (раздел 2), используй `read` с `offset`/`limit`
3. **Лицензирование** → раздел 4, обязательно preflight
4. **Статьи для блога** → раздел 6 + раздел 1 как источник фактов
5. **Оглавление** → `AlphaPlatform_главы_text.md` для навигации по страницам

*Последнее обновление: 2026-03-19*
