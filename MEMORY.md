# MEMORY INDEX

## SYSTEM FILES
- Constitution → `CONSTITUTION.md`
- Current State → `STATE.md`
- Decisions → `DECISIONS.md`
- Daily log → `memory/YYYY-MM-DD.md`

## ACTIVE POINTERS
- User profile and timezone → `USER.md`
- Operating rules for the assistant → `AGENTS.md`

## KNOWLEDGE BASES
- **Alpha-Bot** → `docs/bots/ALPHA_BOT.md` — Telegram-бот + веб-виджет, консультант по Альфа платформе, гибридный RAG, калькулятор тегов
- **HumanLike Agent** → `docs/bots/HUMANLIKE_AGENT.md` — Telethon userbot, имитация живого инженера АСУ ТП, адаптивное обучение, миссии, опечатки
- **БАГЕТ-ПЛК1-01** → `docs/hardware/BAGET_PLK1_01.md` — одноплатный микрокомпьютер на Комдив-МК (К5500ВК018, НИИСИ РАН), режимы Debian/baremetal, среда разработки WSL+VS Code, прошивка через flashrom
- **Альфа платформа (полная)** → `docs/alpha_platform/INDEX.md` — единый индекс: конспекты 50 модулей, полный текст 6500+ стр., лицензирование, кейсы, роли для блога
- **Брендбук Атомик Софт** → `docs/alpha_platform/BRANDBOOK_AUTOMIQ.md` — цвета (#005497, #0997C8, #82C444), шрифты (Circe, Source Sans Pro), логотип, правила использования
- **Лицензирование Alpha** → `/root/.openclaw/workspace/data/licensing_automiq/` — тарифы, SKU, правила, шаблоны ТКП
- **Инструкции техподдержки Alpha** → `docs/alpha_platform/support_guides/INDEX.md` — практические инструкции по настройке, развёртыванию и сопровождению компонентов Alpha Platform
- **Блог specialtechnology.ru** → `website/spectech/BLOG_ROLE.md` (Автоматчик), `website/spectech/BLOG_ROLE_DEV.md` (Разработчик)
- **AVEVA PI System** → `docs/pi_system/` — полная база знаний (10 учебников, 45k строк, 7 конспектов ~100КБ):
  - `PI_SYSTEM_INDEX.md` — индекс всей базы
  - `PI_SYSTEM_OVERVIEW.md` — обзор модулей
  - `ALPHA_VS_PI_SYSTEM_v3.md` — детальное сравнение Альфы и PI System (19 разделов)
  - `pi_architecture_notes.md` — архитектура, HA, безопасность, порты
  - `pi_asset_framework_notes.md` — AF, шаблоны, аналитики, rollup
  - `pi_administration_notes.md` — sizing, backup, DR, мониторинг
  - `pi_events_notifications_notes.md` — Event Frames, Notifications
  - `pi_visualization_notes.md` — PI Vision, PI DataLink, функции Excel
  - `pi_analyzing_notes.md` — PI Analysis Service, OEE, BI
  - `pi_web_api_notes.md` — REST API, endpoints, примеры на 5 языках
  - `raw/` — исходные тексты 10 учебников
  - Доступ для ботов: `/opt/alpha-bot-data/docs/pi_system` (симлинк)
- **Веб-контент и UI/UX** → `docs/web_content/` — две книги-конспекта:
  - `LETTING_GO_WORDS.md` — принципы написания контента: bite/snack/meal, инвертированная пирамида, персоны, заголовки, ссылки, SEO
  - `ROOTS_UIUX_DESIGN.md` — UI/UX дизайн: сетка, типографика, цвета, кнопки, формы, компоненты, структуры страниц, мобильный дизайн

## MEMORY PROTOCOL
1. Стабильные знания и правила → `DECISIONS.md`
2. Текущий фокус и ограничения → `STATE.md`
3. История/черновые наблюдения → `memory/YYYY-MM-DD.md`

## BOOTSTRAP V2 (short)
- Mode: engineering assistant
- Priorities: accuracy > structure > brevity
- Truth order: Constitution > Decisions > State > Daily
- Assume continuity unless contradicted
- Current focus: keep memory compact and reliable
- Constraints: structured/manual memory first
- **Лицензирование Alpha (полное)** → `docs/alpha_platform/licensing_policy_2023_text.md` + `licensing_presentation_2023.md` — официальные документы Атомик Софт: политика, комплекты, правила подсчёта тегов, SKU, SLA
