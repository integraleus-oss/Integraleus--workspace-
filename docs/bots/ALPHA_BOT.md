# Alpha-Bot (@Idol50_bot)

**Назначение:** Telegram-бот + веб-виджет — консультант по Альфа платформе (SCADA) для клиентов.  
**Дистрибьютор:** ООО «Специальные Технологии» (specialtechnology.ru)  
**Производитель платформы:** АО «Атомик Софт» (бренд Automiq, automiq.ru)

## Архитектура

```
projects/alpha-bot/          ← исходный код (единственный источник правды)
  ├── .env                   ← API-ключи (не коммитить)
  ├── venv/                  ← Python venv
  ├── bot.py                 ← главный модуль (Telegram + aiohttp web)
  ├── llm.py                 ← OpenRouter LLM-клиент с гибридным RAG
  ├── rag.py                 ← RAG v2: semantic (ChromaDB) + BM25 + реранкинг
  ├── knowledge_base.py      ← системный промпт с базой знаний Альфа
  ├── calculator.py          ← калькулятор тегов и подбор редакций
  ├── conversation_memory.py ← контекстная память: SQLite + профили + саммаризация
  ├── analytics.py           ← аналитика: темы, конверсия, качество
  └── build_index_batch.py   ← построение индекса (эмбеддинги)
/opt/alpha-bot               ← симлинк → projects/alpha-bot/
/opt/alpha-bot-data/         ← данные
  ├── chunks.json            ← чанки документации
  ├── embeddings.npy         ← numpy-эмбеддинги (legacy)
  ├── chroma_db/             ← ChromaDB (гибридный RAG)
  ├── conversations.db       ← SQLite: история, профили, аналитика
  ├── docs/                  ← исходные документы
  └── логи
```

## Стек

| Компонент | Технология |
|-----------|-----------|
| LLM | OpenRouter → Google Gemini 2.0 Flash (основная), Gemma 3 12B / Nemotron 120B (free fallback) |
| Embeddings | Ollama → nomic-embed-text (локально) |
| RAG | Гибридный: ChromaDB (semantic) + BM25Okapi + реранкинг |
| Telegram | python-telegram-bot |
| Web-виджет | aiohttp |
| Память | SQLite (conversations.db) |
| Деплой | `/opt/alpha-bot` → симлинк |

## Модули

### bot.py — Главный модуль
- Telegram-хэндлеры: `/start`, `/reset`, `/stats`
- aiohttp web-сервер для виджета (API `/api/chat`)
- Контекстная память: до 10 сообщений + саммаризация при >20
- Фаза 2: контекстная память

### llm.py — LLM-клиент
- OpenRouter API с fallback на free-модели
- Гибридный RAG: автоматический поиск контекста в документации
- Детекция модуля по запросу → фильтрация RAG-результатов
- Интеграция с калькулятором тегов

### rag.py — Гибридный поиск RAG v2
- **Semantic**: ChromaDB с Ollama-эмбеддингами (nomic-embed-text)
- **BM25**: BM25Okapi по чанкам
- **Реранкинг**: RRF (Reciprocal Rank Fusion) — объединение результатов
- Фильтрация по модулям (21 модуль с keyword-паттернами)
- Fallback на legacy numpy-индекс

### knowledge_base.py — Системный промпт
- Полное описание Альфа платформы: 3 семейства, все модули
- Правила консультации: НЕ выдумывать, НЕ упоминать устаревшие компоненты
- Запрет markdown в ответах (Telegram plain text)
- Устаревшие модули (ЗАПРЕЩЕНЫ): Alpha.Alarms 3.30, Alpha.Trends 3.33 standalone

### calculator.py — Калькулятор тегов
- Расчёт внешних тегов из сигналов (DI/DO/AI/AO × коэффициенты мощности)
- Тарифные ступени: 32...2 000 000 тегов
- Подбор редакций: One+ / SCADA / Platform
- Коэффициенты мощности: simple / medium / complex

### conversation_memory.py — Контекстная память
- SQLite: messages, user_profiles
- Профили: display_name, company, role, interests, topics
- Саммаризация диалогов
- Детекция follow-up вопросов
- Извлечение информации о пользователе из текста

### analytics.py — Аналитика
- Трекинг событий: вопросы, темы, ответы
- Метрики: общее количество, по модулям, конверсия
- Формат отчёта для Telegram

## Конфигурация (.env)

```env
OPENROUTER_API_KEY=sk-or-v1-...
TELEGRAM_TOKEN=...
OLLAMA_URL=http://127.0.0.1:11434
EMBED_MODEL=nomic-embed-text
```

## Запуск

```bash
cd /opt/alpha-bot && venv/bin/python bot.py
```

## Ключевые правила бота

1. Отвечает ТОЛЬКО на русском
2. НЕ выдумывает продукты/модули
3. НЕ использует markdown (plain text для Telegram)
4. НЕ упоминает устаревшие компоненты
5. Предлагает Alpha.One+ первым если подходит (до 50k тегов, без резерва, 1 клиент)
6. Всегда минимум 2 варианта для сравнения
7. Не называет цены — предлагает оставить контакт
