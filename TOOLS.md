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

## openclaw-home (192.168.68.125 / Tailscale: openclaw-home)
- **OS:** Ubuntu 24.04 LTS, 937 GB NVMe (4% занято), 12 GB RAM
- **Доступ:** `ssh stanislav@openclaw-home` (Tailscale SSH)
- **OpenClaw:** 2026.4.2, gateway systemd enabled, heartbeat 1h
- **Ollama:** nomic-embed-text (memory search)
- **Docker:** 29.3.1, systemd enabled
- **Whisper:** 20250625, venv `~/.openclaw/workspace/.venv-whisper/`
- **VPN:** AmneziaWG split tunnel (MTU 1380), только Discord + YouTube через VPN
  - Конфиг: `/etc/amnezia/amneziawg/awg0.conf`
  - AllowedIPs: 162.159.0.0/16 (Discord), Google/YouTube подсети
- **Безопасность:** UFW active (SSH + LAN + Tailscale), fail2ban (sshd)
- **GitHub:** SSH-ключ добавлен, `integraleus-oss`
- **Утилиты:** ffmpeg, tmux, gh CLI, jq, rsync, imagemagick, poppler-utils, p7zip-full, yt-dlp
- **Locale:** en_US.UTF-8 + ru_RU.UTF-8
- **Бэкап:** ежедневно 3:00 → Synology `/mnt/synology/Documents/openclaw-backups`
- **Workspace:** полная синхронизация с VPS через git

## Synology NAS (192.168.68.103) — DS218play, DSM 7.3.2
- **Доступ:** SSH с ключом `ssh integraleus@192.168.68.103` (через openclaw-home)
- **API:** `http://192.168.68.103:5000` / `https://192.168.68.103:5001`
- **Пользователь:** Integraleus (uid 1026, группа administrators)
- **RAID:** RAID 1, два диска [UU]
- **NFS шары:** Documents, video, music, homes, Lost, surveillance, PlexMediaServer
- **Монтирование на openclaw-home:**
  - `/mnt/synology/Documents` → `/volume1/Documents`
  - `/mnt/synology/video` → `/volume1/video`
  - `/mnt/synology/music` → `/volume1/music`
  - `/mnt/synology/homes` → `/volume1/homes`
- **Автомонт:** fstab, `_netdev,noatime`
- **Squash:** Map all users to admin
- **Объём:** 7.3 TB (3.6 TB занято, 49%)
- **Plex:** работает (v1.41.5)
- **Принтер:** Pantum P1100ADW по USB (не виден, нужно включить)
- **Симлинки** `~/nas/`:
  - backups, books, downloads, flash-se, homes, journals, music, nata, onedrive, video, websites

### 🔒 ПРАВИЛО БЕЗОПАСНОСТИ SYNOLOGY (ОБЯЗАТЕЛЬНОЕ)
**Любые файлы и данные с Synology НЕ ДОЛЖНЫ покидать домашнюю сеть без явного разрешения Станислава.**
- ❌ Не отправлять содержимое файлов Synology в чаты, email, интернет
- ❌ Не копировать на VPS, Garden или другие внешние серверы
- ❌ Не включать содержимое в ответы на внешних поверхностях
- ❌ Не использовать как контекст для задач, результаты которых уходят наружу
- ✅ Можно читать, анализировать, обрабатывать ЛОКАЛЬНО на openclaw-home
- ✅ Можно показывать результаты анализа Станиславу в чате (без сырых данных)
- ✅ Если нужно передать наружу — СПРОСИТЬ разрешение

## API ключи

- **Anthropic:** настроен в OpenClaw (`auth.profiles.anthropic:default`)
- **OpenAI:** настроен в OpenClaw (`auth.profiles.openai:default`)
- **OpenRouter:** `sk-or-v1-c599...` в `.env` ботов (НЕ в OpenClaw)
- **Brave Search:** настроен в OpenClaw

## TTS
- Whisper (local, small model, русский) для транскрипции голосовых

## OpenClaw Gateway — управление

**Правильные команды:**
- `openclaw gateway restart` — штатный рестарт (предпочтительно)
- `openclaw gateway stop` / `openclaw gateway start` — стоп/старт
- `openclaw gateway install` — установка systemd-сервиса
- `systemctl --user restart openclaw-gateway.service` — через systemd (если установлен)
- **НЕ использовать:** `kill -TERM <pid>` + ручной запуск — грязно, ломает сессии
- **НЕ использовать:** `systemctl restart openclaw-gateway` (без --user) — нет такого сервиса

**После обновления OpenClaw (ОБЯЗАТЕЛЬНО):**
1. `openclaw doctor --fix` — починить runtime-модули
2. `openclaw logs --plain --limit 50` — проверить ошибки
3. `openclaw gateway restart` — чистый рестарт
4. `openclaw status --deep` — контрольная проверка
5. Убедиться: нет `ERR_MODULE_NOT_FOUND`, нет `409 Conflict` в Telegram

**Ollama — известные проблемы:**
- `nomic-embed-text` runner может зависнуть при массовых embedding-запросах
- Rate limiting добавлен в скрипты Alpha-Bot (sleep 0.1s)
- Если load average > 2 и ollama runner > 100% CPU — перезапустить: `systemctl restart ollama`
