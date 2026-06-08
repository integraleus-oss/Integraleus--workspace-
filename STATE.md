# STATE.md — Текущее состояние проектов и серверов

_Обновляется из любой сессии после значимых действий. Main session читает при старте._

## Текущий рабочий режим

- **Подтверждение:** явный запрос Станислава считается подтверждением только на указанную область; расширение объёма, внешние действия, конфиги, зависимости, БД, API/auth/security, бизнес-логика, destructive/root-level изменения требуют отдельного подтверждения.
- **Критические изменения:** маленькие атомарные патчи, предварительное описание действия/риска, `git diff`, релевантные тесты/линтеры/type checks при наличии, фактический статус по файлам/проверкам/git/commit.
- **Deliverable:** сначала артефакт/checklist на диске, затем рассуждения; готовность подтверждать реальной проверкой. Для PPTX/визуальных файлов не считать достаточными только `unzip`/XML-проверки.

## Серверы

### Main VPS (155.212.227.115)
- **OS:** Ubuntu 24.04.4 LTS, kernel 6.8.0-107-generic
- **CPU:** AMD EPYC 7763, **RAM:** 11 ГБ, **Disk:** 145 ГБ (21% занято)
- **OpenClaw:** 2026.5.12
- **Ollama:** 0.17.6, модель nomic-embed-text (embedding для Alpha-Bot RAG)
- **Alpha-Bot:** работает (bot.py), RAG через ollama + ChromaDB
- **HumanLike Agent:** установлен, миссии не настроены
- **SSH:** key-only, UFW active (22/80/443)
- **Каналы:** Telegram default OK -> `main`; Telegram `home-monitor` / `@Homegnom_bot` OK -> agent `home-monitor`; Discord OK
- **Последнее обновление:** 2026-05-17

### OpenClaw Telegram Routing
- **default Telegram account:** основной бот, обычные direct-сессии и группа `-1003781262788` остаются на agent `main`.
- **home-monitor Telegram account:** `@Homegnom_bot`, accountId `home-monitor`, allowlist только `109592643`, routed to agent `home-monitor`, session `dmScope=per-account-channel-peer`.
- **home-monitor agent model:** `ollama/phi3:instruct`; token нового бота хранится в `~/.openclaw/openclaw.json` и не должен попадать в ответы/логи.

### OpenClaw Model/Auth Routing
- **main default model:** `openai/gpt-5.5` with Codex runtime (`agentRuntime.id=codex`).
- **main Codex account auth order:** config-level `auth.order.openai` may list `openai-codex:stasiintegraleus@gmail.com` -> `openai-codex:integraleus55@gmail.com`; effective runtime auth for `openai/gpt-5.5` uses authProvider `openai-codex` with the same two effectiveProfiles in that order.
- **main effective switch sequence:** `openai/gpt-5.5` + `openai-codex:stasiintegraleus@gmail.com` -> `openai/gpt-5.5` + `openai-codex:integraleus55@gmail.com` -> `ollama/phi3:instruct`.
- **main model fallback:** after Codex OAuth profile failover, fall back directly to `ollama/phi3:instruct`; there is no separate third gateway step named `codex/gpt-5.5+oauth`, because Codex OAuth is the runtime/authProvider used by `openai/gpt-5.5`.
- **main Codex limit switching:** `scripts/heartbeat-token-limits.sh` now runs `scripts/codex-account-limit-switch.mjs`, which checks both configured Codex OAuth accounts directly. If the first account in order has less than 20% remaining on either 5-hour or weekly quota, or is blocked, and the other account has more than 20% remaining on both windows, heartbeat rewrites `openclaw models auth order --provider openai-codex` to put the healthier account first.
- **Legacy route cleanup:** do not keep `codex/gpt-5.5` or `openai-codex/gpt-5.5` in configured model fallbacks; `openclaw doctor --fix` repairs older Codex refs to canonical `openai/*`.
- **Status display caveat:** compact status may show only `gpt-5.5` with runtime `OpenAI Codex`; it does not display the selected `openai-codex` OAuth profile. Verify live account with `/codex account` when responsive.
- **Verify/restore config:** `openclaw models status --json`, `openclaw config get auth.order --json`, `openclaw models auth order get --provider openai-codex`, `openclaw models auth order set --provider openai-codex openai-codex:stasiintegraleus@gmail.com openai-codex:integraleus55@gmail.com`, `openclaw models fallbacks list`.

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
- **OS:** Ubuntu 24.04.4 LTS, kernel 6.17.0-23-generic
- **CPU:** AMD Ryzen / GEEKOM A6, **RAM:** 16 ГБ DDR5, **SSD:** ~1 ТБ NVMe (6% занято на 2026-05-13)
- **Tailscale IP:** 100.114.189.16, **LAN:** 192.168.68.125
- **OpenClaw:** 2026.5.20, gateway local loopback `127.0.0.1:18789`, Telegram OK
- **Роль:** рабочий Alpha Platform стенд + Home OpenClaw host; hardening делать осторожно через карту зависимостей Alpha/n8n/Caddy
- **SSH:** `PasswordAuthentication yes`, `22/tcp Anywhere`; key-login для `stanislav@openclaw-home` НЕ подтверждён — до `key-login-ok` не отключать пароли и не убирать SSH Anywhere, если это текущий рабочий доступ
- **UFW:** active, default deny incoming; разрешены LAN `192.168.68.0/24`, Tailscale `100.64.0.0/10`, `80/443 Anywhere`, `22 Anywhere`
- **OpenClaw security audit:** 0 critical · 4 warn · 1 info; trusted mode (`workspaceOnly=false`, `exec.security=full`, elevated) допустим только при доверенном доступе
- **Alpha services:** active `alpha.accesspoint`, `alpha.domain`, `alpha.imitator`, `alpha.net`, `alpha.security`, `alpha.server`; failed `alpha.hmi.webviewer.service`, `alpha.security.useractivity.service`
- **Alpha issues:** WebViewer ждёт отсутствующий `/opt/Alpha.HMI/projects/demo/demo.hmi`; UserActivity ссылается на отсутствующего `user1`; `alpha.security.agent` шумит LDAP-ошибками пользователя подключения
- **Последнее обновление OpenClaw:** 2026-05-22; ближайший риск — Codex OAuth expiring ~13h после обновления
- **Последний аудит:** 2026-05-13

#### Local Codex / Claude CLI
- **Codex CLI:** `/usr/bin/codex` 0.136.0 installed; normal user profile `~/.codex` is logged in with ChatGPT.
- **OpenClaw wrapper:** `/home/stanislav/.local/bin/codex-local` unsets `CODEX_HOME` and runs `/usr/bin/codex`; use this from OpenClaw when the intended target is the local user Codex CLI.
- **Preferred runner:** `scripts/codex-local-run.sh` wraps `codex-local exec` with login check, OpenAI NL VPN route check, explicit `--cd`, and explicit sandbox mode. Default is `--read-only`; use `--write` only in the target project; reserve `--danger` for explicitly justified cases.
- **Command templates:** `docs/LOCAL_CODEX_RUNNER.md` contains ready read-only, workspace-write, and log-analysis examples; use it before launching local Codex for non-trivial work.
- **Reason:** OpenClaw sets `CODEX_HOME=/home/stanislav/.openclaw/agents/main/agent/codex-home`, so plain `codex` inside OpenClaw checks internal agent state and can report `Not logged in`.
- **Preferred operating mode:** OpenClaw Codex remains the Telegram orchestration voice; use `/home/stanislav/.local/bin/codex-local` proactively for heavy local analysis/coding/review and as the first agent-level fallback before allowing work to degrade to `ollama/phi3:instruct`, whenever the OpenClaw agent has control of the turn.
- **Efficiency rule:** run `codex-local` from the target project/work directory with a narrow prompt and minimal necessary context; avoid launching it from the main workspace for tiny checks because it may load `AGENTS.md`/workspace context and spend thousands of tokens.
- **Known local Codex sandbox issue:** simple prompt smoke works, but Codex shell commands under `--sandbox read-only` may fail with bubblewrap `Failed RTM_NEWADDR: Operation not permitted`; do not treat that as auth failure. Prefer narrow prompts that do not require shell when possible, or investigate/fix bubblewrap/user namespace separately before relying on sandboxed local Codex command execution.
- **Limit of current integration:** `codex-local` is a CLI tool, not yet an OpenClaw gateway model provider. A true gateway-level fallback chain using local Codex before Ollama requires a separate `local-codex-cli` adapter/provider.
- **Route requirement:** before using local Codex/Claude for external/API work, verify OpenAI/Anthropic endpoints route through NL VPN `awg0` with source `10.8.1.19`.
- **Claude CLI:** `/usr/bin/claude` logged in as `integraleus50@gmail.com`, Pro; use as auxiliary reviewer/second opinion with normal safety boundaries.

## Проекты

### Alpha BPR
- **Код:** `/home/stanislav/projects/alpha-bpr`
- **Документальный baseline:** `docs/baseline/` — 12 управляемых документов + индекс + матрица трассировки
- **Baseline-коммит:** `86229e9 Add Alpha BPR development baseline`
- **Investor demo-pack:** `docs/investor-demo/` — README, TODO, 5-slide outline, 7-10 minute demo script, runnable `curl-flow.sh`, sample output
- **Investor demo-pack коммит:** `541a6d5 Add Alpha BPR investor demo pack`
- **Investor demo-pack проверка:** `dotnet build` OK, `dotnet test` 65/65 OK, `curl-flow.sh` прошёл end-to-end against local API after applying local dev DB migration `20260607151122_BatchStepDeviationEvaluationStatus`
- **Правило:** изменения поведения/API/БД/алгоритмов/шаблонов/приемки должны обновлять baseline и тесты в том же изменении
- **Проверка baseline:** сборка без ошибок, 44 теста прошли
- **Следующий приоритет:** EPIC-03B Domain correctness — статусы evaluation, временные инварианты, quality policy, interval clipping, provider fail-fast, запрет удаления published recipe

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
- Codex OAuth на main/openclaw-home был близок к истечению после обновления OpenClaw 2026.5.20; проверить/переавторизовать при сбоях модели
- Ollama может зависать при массовой индексации без rate limiting (починено в коде, но старые процессы могут работать без фикса)
- Gateway systemd service: disabled (не установлен как auto-start)
