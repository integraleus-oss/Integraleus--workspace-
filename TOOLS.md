# TOOLS.md - Local Notes

## Серверы

### Main (155.212.227.115) — этот VPS
- OpenClaw gateway, Telegram/Discord боты, Ollama
- UFW active, fail2ban, SSH key-only

### Garden (31.128.32.68) — через SSH
- root@31.128.32.68

### VPN (157.22.180.83) — через SSH
- root@157.22.180.83, Amnezia AWG2 (Docker)

## Боты (помимо OpenClaw)

### Alpha-Bot (@Idol50_bot)
- **Назначение:** Консультант по Альфа Платформе (SCADA) для сайта и Telegram
- **Код:** `projects/alpha-bot/` → симлинк `/opt/alpha-bot`
- **Данные:** `/opt/alpha-bot-data/` (chunks.json, embeddings.npy, docs/, логи)
- **Venv:** `projects/alpha-bot/venv/`
- **Модель:** `google/gemini-2.0-flash-001` через OpenRouter
- **RAG:** Ollama nomic-embed-text → cosine similarity
- **Запуск:** `cd /opt/alpha-bot && venv/bin/python bot.py`
- **.env:** Единственный экземпляр в `projects/alpha-bot/.env`

### HumanLike Agent
- **Назначение:** Telegram userbot (Telethon), имитирует живого человека
- **Код:** `projects/humanlike-agent/` → симлинк `/opt/humanlike-agent`
- **Данные:** `projects/humanlike-agent/memory.db`, `*.session`
- **Venv:** `projects/humanlike-agent/venv/`
- **Модель:** `google/gemini-2.0-flash-001` через OpenRouter
- **Телефон:** +79933490618
- **Миссии:** Пока не настроены (0)
- **Запуск:** `cd /opt/humanlike-agent && venv/bin/python agent.py`
- **.env:** Единственный экземпляр в `projects/humanlike-agent/.env`

### Структура деплоя (A+ схема)
```
projects/alpha-bot/          ← код (единственный источник правды)
  ├── .env                   ← конфиг (НЕ коммитить)
  ├── venv/                  ← Python окружение (НЕ коммитить)
  └── *.py                   ← исходники
/opt/alpha-bot               ← симлинк → projects/alpha-bot/
/opt/alpha-bot-data/         ← данные (chunks, embeddings, docs, логи)

projects/humanlike-agent/    ← код
  ├── .env                   ← конфиг
  ├── venv/                  ← Python окружение
  ├── memory.db              ← база памяти
  ├── *.session              ← Telethon сессия
  └── *.py                   ← исходники
/opt/humanlike-agent         ← симлинк → projects/humanlike-agent/
```

**Правило:** Код правим ТОЛЬКО в `projects/`. `/opt/` — симлинки, не трогать.
**Правило:** `.env` читаем из `projects/*/. env`, НЕ из `/opt/`.

## API ключи

- **Anthropic:** настроен в OpenClaw (`auth.profiles.anthropic:default`)
- **OpenAI:** настроен в OpenClaw (`auth.profiles.openai:default`)
- **OpenRouter:** `sk-or-v1-c599...` в `.env` ботов (НЕ в OpenClaw)
- **Brave Search:** настроен в OpenClaw

## TTS
- Whisper (local, small model, русский) для транскрипции голосовых
