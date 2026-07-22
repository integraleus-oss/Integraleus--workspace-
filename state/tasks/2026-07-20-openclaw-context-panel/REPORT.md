# Идеи из raytsystem для локальной панели OpenClaw

Дата: 2026-07-20
Источник: <https://github.com/romarayt/raytsystem-public-os>
Проверенный commit: `b5ac70560112758f78dd15852422ee697ac336f4`

## Короткий вывод

Репозиторий из видео — `romarayt/raytsystem-public-os`. Его не стоит ставить
поверх нашего workspace как готовую систему: проект pre-1.0, со своим runtime,
ledger, tasking, web UI, skill-форматом и политиками. Но как референс он
полезен. Для OpenClaw лучше забрать не кодовую базу, а архитектурный паттерн:
отдельная loopback-only панель, которая строит проверяемый read model поверх
существующих `docs/`, `skills/`, `agents/`, `memory/`, `state/tasks/`,
cron/heartbeat/systemd, не становясь новым источником истины.

## Что в репозитории реально ценно

1. **Единый Command Center.**
   Raytsystem показывает workspace health, tasks, runs, catalog и safety в одном
   локальном интерфейсе. Для OpenClaw аналогом может быть первая страница:
   активные агенты, свежие heartbeat-состояния, доступность Telegram, cron,
   опасные/зависшие задачи, публичные демо-ссылки, последние измененные файлы.

2. **Knowledge Universe как производный граф.**
   Хорошая идея — не “рисовать Markdown”, а собрать typed graph из разных
   плоскостей: workspace, instruction, skill, agent, task, run, artifact,
   source/evidence, policy, adapter, file/module/function. Важно: граф
   rebuildable, не canonical truth.

3. **Линзы графа.**
   У них есть Universe / Knowledge / Work / Agent / Evidence / Code. Для нас
   лучше начать с четырех линз:
   - `Context`: `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`,
     `STATE.md`, `DECISIONS.md`;
   - `Skills`: local skills, bundled OpenClaw skills, proposal/state связи;
   - `Work`: `state/tasks/**`, active sessions, cron, heartbeat checks;
   - `Automation`: scripts, systemd units, bots, tunnels, cron jobs.

4. **Task ledger отдельно от knowledge.**
   У raytsystem task progress не инвалидирует knowledge generation. У нас это
   особенно правильно: `memory/`, `STATE.md`, `DECISIONS.md` нельзя смешивать с
   текущими задачами. Панель должна показывать `state/tasks/**` и active
   sessions как operational plane, а не писать в память автоматически.

5. **Agents/Skills как inert catalog.**
   Сильная граница: skill bodies и agent instructions в UI являются данными, а
   не инструкциями к исполнению. Для OpenClaw это обязательное правило: панель
   может показывать `SKILL.md`, зависимости, hash, last modified, source, но не
   “выполнять” команды из markdown.

6. **LINT как отдельный read-only режим.**
   У raytsystem linter проверяет поколение, stale projection, wikilinks,
   markdown links, orphan pages, duplicate frontmatter IDs, aliases/slugs,
   операции и secrets. Для нас MVP:
   - битые относительные ссылки в `docs/**/*.md`, `skills/**/SKILL.md`,
     `state/tasks/**/*.md`;
   - ссылки на несуществующие файлы из `AGENTS.md`, `TOOLS.md`,
     `HEARTBEAT.md`, `STATE.md`, `DECISIONS.md`;
   - orphan task packets без `TODO.md` или без статуса;
   - secret-shaped строки в tracked/plain files;
   - предупреждение, если Synology paths попали в внешний/публичный артефакт.

7. **Public hygiene / secret scanner.**
   У них отдельный `scripts/public_hygiene.py` и `SecretScanner` с patterns для
   private keys, GitHub/OpenAI/Anthropic/AWS/Slack/Telegram tokens, bearer/JWT,
   credential URLs, email/phone. Нам стоит сделать похожий `openclaw-context
   lint --secrets`, но с allowlist для известных безопасных примеров и
   redaction by default.

8. **Feature flags и disabled-by-default.**
   Raytsystem явно разделяет catalog/UI от runtime execution. Нам это полезно
   для панели: v1 только read-only plus local cache rebuild. Любые writes
   отдельно: `refresh-index`, `ack finding`, `open task packet`, и все они
   требуют idempotency/audit.

## Что не надо переносить

- Не переносить их ledger/normalized/raw модель целиком. У OpenClaw уже есть
  `MEMORY.md`, daily memory, `STATE.md`, `DECISIONS.md`, task packets и sessions.
- Не запускать их provider/runtime adapters. У нас уже есть OpenClaw gateway,
  Codex runtime, tools, sessions, cron и skills.
- Не делать “редактор памяти” в первой версии. Риск слишком высокий:
  memory/security правила важнее удобства.
- Не сканировать Synology с выводом сырых данных в панель. Только агрегаты и
  локальные redacted findings.

## MVP панели OpenClaw

### 1. Индексатор

Создать отдельный rebuildable каталог, например:

```text
.openclaw-context/
├── CURRENT
├── snapshots/<sha>.json
├── graph/<sha>.json
├── findings/<sha>.json
└── index.sqlite
```

Индекс строится из allowlisted roots:

```text
AGENTS.md
SOUL.md
USER.md
TOOLS.md
HEARTBEAT.md
MEMORY.md
STATE.md
DECISIONS.md
docs/**
skills/**
memory/YYYY-MM-DD.md
state/tasks/**
scripts/**
```

Для приватных файлов храним только metadata: path, type, mtime, size, hash,
frontmatter/title/status, outbound links. Текст показывать только там, где это
разрешено текущими правилами.

### 2. Граф `docs/skills/agents/memory`

Типы узлов:

- `workspace`
- `instruction`: `AGENTS.md`, `HEARTBEAT.md`, `TOOLS.md`, `SOUL.md`, `USER.md`
- `memory`: `MEMORY.md`, `memory/YYYY-MM-DD.md`
- `decision`: `DECISIONS.md`
- `state`: `STATE.md`, `state/tasks/**`
- `skill`: local/bundled skills
- `agent`: main, home-monitor, local, bots
- `automation`: cron, heartbeat sections, systemd services, scripts
- `project`: `projects/*`, docs packages, public demos
- `finding`: broken link, stale reference, possible secret, missing checklist

Типы связей:

- `mentions`, `links_to`, `defines`, `uses_skill`, `owned_by_agent`,
  `updates_memory`, `runs_script`, `monitors_service`, `depends_on`,
  `produces_artifact`, `has_finding`.

Первый UI можно сделать не full physics graph, а:

- left: filters/lenses;
- center: graph/list toggle;
- right: inspector with source refs and safe excerpts;
- fallback table always available.

### 3. Task-flow экран

Не заменять OpenClaw sessions. Сделать read model:

- current task packets from `state/tasks/**/TODO.md`;
- active sessions from `openclaw status --json` / sessions metadata;
- heartbeat outcomes from `memory/heartbeat-state.json`;
- cron jobs/runs;
- recent deploy/access artifacts.

Колонки:

- Inbox / Planned / Ready / Running / Review / Blocked / Done / Cancelled.

Но v1 может быть read-only: статус берется из чеклистов и session metadata.
Write-режим позже: создать task packet, отметить checklist item, записать
finding acknowledgement.

### 4. Проверка ссылок и секретов

Команды:

```bash
openclaw-context index --json
openclaw-context graph --json
openclaw-context lint --json
openclaw-context lint --secrets --json
```

Проверки v1:

- missing local markdown links;
- dead file references in instructions;
- stale symlinks;
- duplicate task packet IDs/titles;
- task packet without TODO/checklist;
- suspicious secret patterns;
- forbidden tracked files: `.env`, keys, `.session`, DBs, archives unless
  explicitly allowlisted;
- external URL inventory without fetching private data.

### 5. Индекс автоматизаций

Панель должна собрать “что само что делает”:

- heartbeat sections from `HEARTBEAT.md`;
- cron jobs from `openclaw cron list --json`;
- systemd units matching `openclaw`, `alpha-*`, bot services;
- scripts in `scripts/**`;
- public/demo access routes and tunnels;
- bots from `TOOLS.md`.

Для каждой автоматизации:

- owner/source file;
- schedule/trigger;
- last observed status;
- writes/egress risk;
- related service/script;
- latest evidence/check.

## Рекомендуемый порядок работ

1. Сделать `openclaw-context index --json`: только read-only scan и snapshot.
2. Добавить `lint --links --secrets` и вывод findings.
3. Нарисовать простой локальный HTML/React экран “Context Map” без мутаций.
4. Добавить graph JSON и 4 линзы: Context, Skills, Work, Automation.
5. Добавить Task-flow read model.
6. Только после этого обсуждать safe write actions.

## Практическое решение

Я бы сделал отдельный маленький проект внутри workspace:

```text
tools/openclaw-context-panel/
```

или, если хотим держать ближе к состоянию агента:

```text
state/tools/openclaw-context-panel/
```

Первый вариант лучше, если это будет поддерживаемый инструмент. Второй лучше
для быстрого прототипа. Начинать стоит с прототипа в `state/tools/`, потом
перенести в `tools/` после стабилизации.

## Источники в raytsystem

- `README.md`: surfaces, loopback-only model, core skills, security model.
- `docs/STATUS.md`: что реально available/experimental/disabled.
- `docs/07-web-control-plane-architecture.md`: state planes, Knowledge
  Universe, task ledger, catalog/skill boundary.
- `docs/11-code-graph-and-execution-plane.md`: code graph lifecycle, safe
  defaults, agent projection, execution boundaries.
- `src/raytsystem/linting.py`: link/orphan/secret/operation checks.
- `src/raytsystem/security/sensitivity.py`: deterministic secret scanner.
- `scripts/public_hygiene.py`: public-tree hygiene checks.
