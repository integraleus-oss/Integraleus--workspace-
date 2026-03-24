# Alpha Platform Consultant Bot

Чат-бот консультант по Альфа платформе (SCADA) для сайта и Telegram.

## Установка

```bash
cd projects/alpha-bot
pip install -r requirements.txt
```

## Запуск

```bash
python bot.py
```

## Конфигурация (.env)

- `OPENROUTER_API_KEY` — ключ OpenRouter
- `TELEGRAM_BOT_TOKEN` — токен Telegram-бота
- `MODEL` — модель LLM (по умолчанию `google/gemma-2-9b-it:free`)
- `PORT` — порт веб-сервера (по умолчанию 8090)

## Компоненты

- **Telegram-бот** — polling, команды /start, /reset
- **Веб-виджет** — встраиваемый чат для сайта
- **API** — POST /api/chat для веб-клиента

## Встраивание на сайт

Добавить перед `</body>`:

```html
<script src="https://YOUR_VPS_IP:8090/widget.js"></script>
```

## Эндпоинты

- `GET /widget` — HTML виджета
- `GET /widget.js` — JS для встраивания
- `POST /api/chat` — API чата (`{"message": "...", "session_id": "..."}`)
- `GET /health` — healthcheck
