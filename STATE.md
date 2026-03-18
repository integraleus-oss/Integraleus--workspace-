# CURRENT STATE

## FOCUS
- Развиваем устойчивую memory-архитектуру без лишней сложности.

## WEEK FOCUS
- Держим стабильную continuity между сессиями через краткий `STATE.md` и фиксируем ключевые решения в `DECISIONS.md`.

## ACTIVE GOALS
- Держать контекст компактным и предсказуемым.
- Уменьшить повторные объяснения.
- Убрать silent failures при сбоях основной модели.

## MODEL OPERATING MODE
- Default main session: Sonnet
- Deep analysis / pricing / commercial reasoning / long-form documents: Opus
- Coding / infra / server / config / debugging: Codex

## CONSTRAINTS
- Используем structured/manual memory как основной режим.
- Для routine-задач предпочитаем Sonnet; Opus не держим дефолтом для повседневной рутины.
- Для cron и heartbeat предпочитаем Sonnet, при timeout переключаем на Codex как запасной вариант.

## NEXT CHECKPOINT
- Еженедельная консолидация памяти (5 минут).
