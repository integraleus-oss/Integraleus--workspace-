# TECHNICAL-RULES.md

Reference-правила для технической, инфраструктурной и операционной работы.
Live entrypoint: `AGENTS.md`; этот файл читать перед задачами с кодом,
OpenClaw operations, ботами, Synology, Alpha BPR, UI или hardening.

## Область применения

Использовать для:

- кода;
- серверных проверок;
- OpenClaw operations;
- ботов;
- Alpha technical work;
- Synology и домашней сети;
- координации агентов;
- диагностики и hardening.

## Общая инженерная работа

Перед изменениями:

1. изучить проект;
2. определить source of truth;
3. проверить `git status`;
4. не трогать чужие изменения;
5. сделать минимальное полезное изменение;
6. выполнить релевантные проверки.

Следовать существующим паттернам. Не добавлять абстракции ради абстракций.

## Правки файлов

- Для поиска использовать `rg`/`rg --files`.
- Для ручных правок использовать `apply_patch`.
- Не перезаписывать файлы shell-redirection.
- Не редактировать `.env` без необходимости.
- Не коммитить секреты, session-файлы, базы, virtualenv и generated noise.
- В dirty worktree не откатывать изменения, которые агент не делал.

## Проверки

Выбирать проверки по риску:

- syntax-check для маленьких скриптов;
- unit tests для изменения поведения;
- integration tests для API/data contracts;
- smoke tests для сервисов;
- browser/mobile screenshots для UI;
- `git diff --check` для чистоты патча.

Если проверка невозможна, сказать почему.

## OpenClaw operations

Правильные команды gateway:

- `openclaw gateway restart`
- `openclaw gateway stop`
- `openclaw gateway start`
- `openclaw gateway install`

Не использовать:

- случайный `kill -TERM` плюс ручной запуск;
- `systemctl restart openclaw-gateway` без `--user`.

После обновления OpenClaw:

1. `openclaw doctor --fix`
2. `openclaw logs --plain --limit 50`
3. `openclaw gateway restart`
4. `openclaw status --deep`
5. проверить module errors и Telegram conflicts.

На home host не запускать широкие repair tools вслепую, если state говорит о
security/legacy caveats.

## Model/Auth routing

Каноническая основная модель:

- `openai/gpt-5.5` с Codex runtime.

Порядок профилей:

1. `openai-codex:stasiintegraleus@gmail.com`
2. `openai-codex:integraleus55@gmail.com`
3. локальный fallback только после Codex profile failover.

Не добавлять legacy names:

- `codex/gpt-5.5`
- `openai-codex/gpt-5.5`

Heartbeat обязан запускать `scripts/heartbeat-token-limits.sh`. При WARN
следовать `HEARTBEAT.md`.

## Local Codex и Claude

Для локального Codex использовать:

- `/home/stanislav/.local/bin/codex-local`
- `scripts/codex-local-run.sh`

Причина: OpenClaw задаёт свой `CODEX_HOME`, и plain `codex` может смотреть не
тот auth state.

Для Claude non-interactive review использовать:

- `/home/stanislav/agent-runs/_bin/claude-review`
- `/home/stanislav/agent-runs/_bin/claude-review-diff`

Не использовать сырой `claude -p "$(cat prompt.md)" | tee output.log` для
review.

## Серверы

Известные хосты:

- Main VPS: внешний host для OpenClaw/bots/Ollama.
- Garden: `root@31.128.32.68`.
- VPN: `root@157.22.180.83`.
- openclaw-home: домашний GEEKOM.
- Synology: `192.168.68.103`.

Read-only диагностику можно делать свободно. Перед root-level изменениями
пользователей, firewall, пакетов, сервисов, дисков, шар, sudoers, cron или
system state — спросить.

Для admin tools в non-login shell использовать абсолютные пути:

- `/usr/sbin/ufw`
- `/sbin/ufw`
- `sshd -T`

## Synology

Данные Synology не должны покидать домашнюю сеть без явного разрешения
Станислава.

Можно без отдельного разрешения:

- локальные read-only проверки;
- локальный анализ;
- краткие выводы Станиславу без сырых приватных данных.

Нельзя без явного разрешения:

- копировать Synology data на VPS/Garden/external services;
- отправлять сырое содержимое файлов в чаты или email;
- менять root-level state;
- менять users, shares, firewall, packages, cron или permissions.

Если есть сомнение, считать действие root-level или external и спросить.

## Боты

Код ботов править только в `projects/`.

Не считать `/opt/*` source of truth, если это symlink.

Основные source roots:

- `projects/alpha-bot/`
- `projects/humanlike-agent/`

`.env` читать только при необходимости, не вставлять секреты в чат и не
коммитить.

## Alpha technical rules

Перед любым ответом о продуктах/модулях Alpha читать:

- `docs/alpha_platform/PRODUCT_CHEATSHEET.md`

Если модуля нет в cheatsheet, не придумывать.

Актуальные компоненты:

- `Alpha.Server`
- `Alpha.Domain`
- `Alpha.AccessPoint`
- `Alpha.HMI`
- `Alpha.HMI.WebViewer`
- `Alpha.HMI.Alarms`
- `alpha.hmi.charts`
- `Alpha.Historian`
- `Alpha.Reports`
- `Alpha.RMap`
- `Alpha.DevStudio`
- `Alpha.Om`
- `Alpha.Tools`
- `Alpha.Imitator`
- `Alpha.Security`
- `Alpha.Diagnostics`

Устаревшие названия не использовать.

## Alpha BPR

Project root:

- `/home/stanislav/projects/alpha-bpr`

Перед изменением behavior/API/DB/algorithms/templates/acceptance:

- обновить baseline/docs/tests в том же изменении;
- запустить focused tests;
- запустить `git diff --check`;
- просканировать deprecated Alpha names;
- сохранить owner-approved boundaries.

Не утверждать без явного одобрения и evidence:

- production sign-off;
- Part 11/QMS validation;
- SLA approval;
- off-machine backup approval;
- live restore approval;
- plant integration approval;
- customer deployment approval.

## Web/UI

При frontend-задачах:

- строить полезный экран, а не marketing shell, если landing page не просили;
- следовать существующему дизайну;
- задавать responsive constraints;
- не допускать overlap текста;
- проверять screenshots при возможности;
- для сайтов и игр использовать визуальные assets;
- не утверждать готовность UI без visual smoke.

Для operational tools предпочитать плотные, спокойные, сканируемые интерфейсы.

## Incident logging

Security incidents логировать без секретов.

Указывать:

- timestamp;
- что произошло;
- затронутую поверхность;
- evidence path или summary команды;
- действие;
- остаточный риск.

Не включать raw tokens, passwords, session files, private message content или
сырые Synology file contents.
