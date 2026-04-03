# STATE.md — Текущее состояние проектов и серверов

_Обновляется из любой сессии после значимых действий. Main session читает при старте._

## Серверы

### Main VPS (155.212.227.115)
- **OS:** Ubuntu 24.04.4 LTS, kernel 6.8.0-107-generic
- **CPU:** AMD EPYC 7763, **RAM:** 11 ГБ, **Disk:** 145 ГБ (21% занято)
- **OpenClaw:** 2026.4.2
- **Ollama:** 0.17.6, модель nomic-embed-text (embedding для Alpha-Bot RAG)
- **Alpha-Bot:** работает (bot.py), RAG через ollama + ChromaDB
- **HumanLike Agent:** установлен, миссии не настроены
- **SSH:** key-only, UFW active (22/80/443)
- **Каналы:** Telegram OK, Discord OK
- **Последнее обновление:** 2026-04-03

### Garden (31.128.32.68)
- **OS:** Ubuntu, **Disk:** 48 ГБ (38% занято)
- **OpenClaw:** установлен (gateway active)
- **SSH:** key-only (permitroot=without-password, password=no)
- **Пользователи:** root, ops
- **Последнее обновление:** 2026-04-03

### VPN (157.22.180.83)
- **OS:** Ubuntu 24.04, kernel 6.8.0-107-generic
- **Amnezia AWG2:** работает (Docker)
- **SSH:** key-only, UFW active
- **Disk:** 11%
- **Последнее обновление:** 2026-04-03 (обновлён + ребут)
- **⚠️ UFW может не стартовать после ребута** — проверять!

### GEEKOM A6 (openclaw-home)
- **OS:** Ubuntu 24.04 LTS
- **CPU:** AMD Ryzen, **RAM:** 16 ГБ DDR5, **SSD:** ~1 ТБ NVMe
- **Tailscale IP:** 100.114.189.16, **LAN:** 192.168.68.125
- **OpenClaw:** 2026.3.28 (устарел)
- **Статус:** НЕ ЗАВЕРШЁН — перенос .openclaw не сделан
- **Последний контакт:** 2026-03-29 (недоступен по Tailscale 2026-04-03)

## Проекты

### specialtechnology.ru
- **Хостинг:** Reg.ru (u1899769@server182)
- **Деплой:** `curl -X POST "https://specialtechnology.ru/deploy.php?key=spt2026deploy&file=FILENAME" --data-binary @file`
- **Статус:** активен, 36+ страниц, 20 статей блога
- **SEO:** GSC + Яндекс.Вебмастер подключены, sitemap 39 URL
- **Последний деплой:** 2026-04-03 (перелинковка 79 ссылок)
- **TODO:** alt-тексты, PageSpeed, Product-микроразметка, Яндекс.Бизнес

### Alpha-Bot (@Idol50_bot)
- **Статус:** работает на Main VPS
- **RAG:** ollama nomic-embed-text + ChromaDB
- **⚠️ Rate limiting добавлен** в скрипты индексации (2026-04-03)

### Переезд VPS → GEEKOM
- **Статус:** ПРИОСТАНОВЛЕН
- **Сделано:** Ubuntu установлена, SSH/Tailscale/Node/OpenClaw настроены
- **Не сделано:** перенос .openclaw, обновление OpenClaw, каналы, Alpha-Bot, ollama, DNS/порты
- **Бэкап:** `/root/openclaw_full_backup_20260305T061301Z.tar.gz` (230 МБ) на VPS

## Активные крон-задачи
- Morning Task Digest — 09:30 MSK ежедневно
- BBQ Daily Digest — 10:00 MSK ежедневно
- Daily Server Monitoring — 10:00 MSK ежедневно
- system-monitor:daily — 10:30/18:30 MSK ежедневно
- fielddev-monitor — 10:00 MSK ежедневно
- healthcheck:security-audit — понедельник 09:00
- healthcheck:update-status — понедельник 09:30
- Garden Server Weekly Check — понедельник 10:00
- SEO audit specialtechnology.ru — понедельник 10:00

## Известные проблемы
- Discord groupPolicy="open" — 4 CRITICAL security warnings (не закрыто)
- Ollama может зависать при массовой индексации без rate limiting (починено в коде, но старые процессы могут работать без фикса)
- Gateway systemd service: disabled (не установлен как auto-start)
