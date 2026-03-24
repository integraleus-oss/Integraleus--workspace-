# HumanLike Agent

AI-агент для Telegram, который общается как живой человек.

## Возможности
- Имитация печати (typing delay, реалистичная скорость)
- Имитация опечаток с исправлением
- Долгосрочная память (SQLite, до 500 сообщений на чат)
- Миссии по чатам (разные роли в разных группах)
- Anti-jailbreak защита
- Ночной режим (редко отвечает ночью)
- Разбивка длинных ответов на части
- Fallback между LLM-моделями

## Быстрый старт

### 1. Получить Telegram API
- Зайти на https://my.telegram.org
- Войти под номером телефона агента
- Создать приложение → получить api_id и api_hash

### 2. Настроить
```bash
cp .env.example .env
# Заполнить API_ID, API_HASH, PHONE, OPENROUTER_API_KEY
```

### 3. Запустить (Docker)
```bash
docker compose up -d
```

### 4. Первый запуск — авторизация
```bash
docker compose run agent python agent.py
# Введёт код из SMS — один раз
```

### 5. Настроить миссии
```bash
# Эксперт в чате
python manage.py mission -100123456 expert \
  --persona "Алексей, инженер АСУ ТП" \
  --style "разговорный, знающий" \
  --triggers "scada,автоматизация,диспетчеризация"

# Продавец
python manage.py mission -100789012 salesman \
  --persona "Дмитрий" \
  --goals "рекомендовать Альфа платформу" \
  --triggers "scada,какую систему выбрать"

# Наблюдатель (только мониторит)
python manage.py mission -100345678 observer
```

## Структура
```
├── agent.py              # Главный модуль (Telethon userbot)
├── config.py             # Конфигурация
├── persona.py            # Персонаж, промпты, anti-jailbreak
├── human_simulation.py   # Имитация человека (typing, typos, delays)
├── llm_client.py         # OpenRouter клиент с fallback
├── memory.py             # SQLite память (сообщения, профили, миссии)
├── manage.py             # CLI управления (миссии, статистика)
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Параметры поведения (config.py)
- `TYPING_SPEED_CPS = 12` — скорость печати (символов/сек)
- `MIN_DELAY / MAX_DELAY` — задержка перед ответом
- `NIGHT_HOURS = (23, 7)` — ночной режим
- `MAX_CONTEXT_MESSAGES = 50` — глубина памяти
