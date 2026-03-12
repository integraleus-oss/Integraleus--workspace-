# specialtechnology.ru — Структура сайта

## Хостинг
- **Reg.ru**, IP: 31.31.196.244, user: u1899769
- **Домены**: specialtechnology.ru, special-tech.ru
- **Деплой**: `curl -s -X POST "https://specialtechnology.ru/deploy.php?key=spt2026deploy&file=<path>" --data-binary @file`
- Поддерживает подпапки (например `blog/article.html`)

## Страницы

| Файл | URL | Описание |
|------|-----|----------|
| `index.html` | / | Главная — о компании, продукты, технологии, партнёры, контакты |
| `calculator.html` | /calculator.html | Калькулятор лицензий Альфа платформы (два режима: быстрый + wizard) |
| `alpha-platform.html` | /alpha-platform.html | Страница продукта Альфа платформы — табы: Обзор, Характеристики, Лицензии, Протоколы, Поддержка, Внедрения |
| `wertsim.html` | /wertsim.html | Страница продукта CAE WeRTSim — табы: Обзор, Возможности, Процессы, Области применения, Интеграция |
| `blog.html` | /blog.html | База знаний / блог — карточки статей, поиск, фильтр по категориям |
| `blog/architecture.html` | /blog/architecture.html | Статья: Архитектура Альфа платформы |
| `blog/historian.html` | /blog/historian.html | Статья: Alpha.Historian 4.0 |
| `blog/hmi.html` | /blog/hmi.html | Статья: Визуализация в Alpha.HMI 2.0 |
| `blog/protocols.html` | /blog/protocols.html | Статья: Протоколы связи в АСУ ТП |
| `blog/crossplatform.html` | /blog/crossplatform.html | Статья: Кроссплатформенность (Linux/Windows) |
| `blog/alarms.html` | /blog/alarms.html | Статья: Alpha.Alarms 3.30 |
| `blog/reports.html` | /blog/reports.html | Статья: Alpha.Reports |
| `blog/scaling.html` | /blog/scaling.html | Статья: Масштабирование SCADA |
| `blog/devstudio.html` | /blog/devstudio.html | Статья: Alpha.DevStudio 4.1 (в процессе) |
| `deploy.php` | — | Эндпоинт деплоя (POST с ключом) |

## Навигация
- **Шапка**: Главная → О компании → Продукты (dropdown: Альфа платформа, CAE WeRTSim) → Калькулятор → Блог → Контакты
- **Футер**: Продукты (Альфа, WeRTSim, MES), Компания (О нас, Технологии, Партнёры, Блог, Контакты)
- **Карточки продуктов** на главной кликабельны → ведут на страницы продуктов

## Дизайн
- Тёмная тема: `--ink: #05080f`, `--volt: #00c8f0`
- Шрифты: Exo 2 (заголовки), JetBrains Mono (моно), Bitter (серифный)
- Базовый текст: 15-16px
- Контейнер: 1400px
- Альфа платформа — голубой акцент (`--volt`)
- CAE WeRTSim — оранжевый акцент (`--flame`)

## Источники контента
- **Альфа платформа**: automiq.ru + внутренняя документация (12 томов, `docs/alpha_platform/`)
- **CAE WeRTSim**: wertsim.ru
- **Правило**: никаких выдуманных фактов, только подтверждённые данные

## Роли
- **АО «Атомик Софт»** — разработчик Альфа платформы
- **АО «Юмосс»** — разработчик CAE WeRTSim
- **АО «СПЕЦТЕХ»** — официальный дистрибьютор

## История изменений
- **2026-03-11**: Первая версия сайта, калькулятор лицензий
- **2026-03-12**: UX-улучшения, parallax, анимации, страницы продуктов, блог с 8+ статьями
