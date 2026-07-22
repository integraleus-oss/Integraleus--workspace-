# План внедрения agent workflow для проектов OpenClaw

Статус: черновик процесса, требует подтверждения Станиславом перед применением как обязательного регламента.

Дата: 2026-07-22

## Зачем

Внедрить единый способ постановки, выполнения и аудита задач для внутренних и внешних агентов: Codex, Claude Code, OpenClaw main/home-monitor/local, фоновых задач, cron, subagents и ручных агентных сессий.

Цель не в том, чтобы добавить бюрократию, а в том, чтобы каждая значимая работа оставляла управляемый след: задача, границы, артефакт, проверка, аудит, решение и следующий шаг.

## Основано на

- Идеях из ролика по Claude Code workflow: Q&A до кода, проектный onboarding, явные роли, проверка результата, reusable команды.
- Текущих правилах `AGENTS.md`: artifact first, task packets, agent task packaging, evidence-based status, no unmanaged background drift.
- Текущей памяти проекта: активный cleanup order ставит `projects/openclaw-shared-memory`, heartbeat/Codex scripts, Alpha-Bot и OpenClaw rules/state/memory в ближайшие фокусы.
- Текущих ограничениях Synology: root-level изменения только после явного подтверждения Станислава; raw Synology data не покидают домашнюю сеть без разрешения.

## Область применения

Применять к:

- OpenClaw core/workspace changes.
- `projects/openclaw-shared-memory`.
- `projects/alpha-bot`.
- `projects/humanlike-agent`.
- `projects/rag-pipeline`.
- `projects/presentations`.
- Site/SEO work, включая `projects/spectech-sites` и локальные зеркала сайтов.
- Alpha BPR / Alpha Presale / Alpha Platform рабочие пакеты.
- NAS/home network/Synology migration work.
- Cron/heartbeat/subagent workflows.
- External agent work: Claude Code CLI, Codex CLI, review agents, browser/UI agents.

Не применять как тяжёлый процесс к:

- коротким ответам в чате;
- одношаговым read-only проверкам;
- мелким правкам, где риск низкий и артефакт уже очевиден;
- heartbeat checks без найденных изменений.

## Роли

- Main agent: владелец контекста, постановщик задачи, финальный редактор, принимает или отклоняет результаты агентов.
- Research agent: читает, картирует, задаёт вопросы, не меняет файлы.
- Implementation agent: меняет только разрешённые файлы в рамках task packet.
- Review agent: ищет баги, риски, пропущенные проверки, privacy/security gaps.
- Evidence agent/check runner: запускает проверки, собирает логи, screenshots, smoke outputs.
- Human owner: Станислав; подтверждает risky/external/root-level действия и утверждает регламент.

## Базовый жизненный цикл задачи

1. Intake
   - Кратко определить цель, проект, риск, ожидаемый результат.
   - Если задача значимая, создать папку `state/tasks/YYYY-MM-DD-short-name/`.
   - Создать `TASK_PACKET.md` или `PLAN.md` в первые 5-10 минут.

2. Exploration / Q&A
   - Найти project root и source-of-truth файлы.
   - Зафиксировать, что можно и нельзя трогать.
   - Отметить открытые вопросы.
   - Для read-only audit явно указать: no edits.

3. Plan gate
   - Сформулировать шаги, проверки, rollback, stop conditions.
   - Для опасных действий получить подтверждение Станислава.
   - Для Synology root-level изменений подтверждение обязательно.

4. Implementation
   - Работать маленькими проверяемыми инкрементами.
   - Не смешивать unrelated cleanup с целевой задачей.
   - Если агенту нужен контекст, передать task packet, а не весь приватный хвост переписки.

5. Evidence
   - Создать или обновить `EVIDENCE.md`, `REPORT.md`, `MIGRATION_LOG.md` или аналог.
   - Записать команды проверки, результаты, ограничения.
   - Для UI: screenshots/smoke/browser checks.
   - Для infra: service status, logs, network checks.
   - Для data/NAS: SMART, copy verification, counts/checksums.

6. Review
   - Для medium/high risk задач запускать Claude/Codex review по отдельному `AUDIT_PACKET.md`.
   - Review output не применять автоматически; main agent принимает решение.
   - Все rejected findings либо закрыть, либо занести в TODO/open risks.

7. Commit / handoff
   - Коммитить законченные инкременты отдельно.
   - В финальном сообщении указывать изменённые файлы, проверки, commit hash, незакрытые риски.
   - Для долгих работ создавать explicit checkpoint, а не полагаться на память.

## Стандартные артефакты

Минимальный пакет:

- `TASK_PACKET.md` или `PLAN.md`
- `TODO.md`
- `EVIDENCE.md` или `REPORT.md`

Расширенный пакет:

- `AGENT_BRIEF.md`
- `AUDIT_PACKET.md`
- `ROLLBACK.md`
- `MIGRATION_CHECKLIST.md`
- `SECURITY_PRECHECK.md`
- `HANDOFF.md`

## Шаблон TASK_PACKET.md

```markdown
# Task Packet: <name>

Status: draft / approved / in_progress / blocked / done
Owner: main agent
Human approval required: yes/no

## Goal

## Context

## Allowed files/systems

## Forbidden files/systems

## Inputs and source of truth

## Expected artifact

## Checks

## Stop conditions

## Review requirements

## Commit / delivery rules
```

## Шаблон AUDIT_PACKET.md

```markdown
# Audit Packet: <name>

Review mode: read-only

## Goal

## Diff / files / artifact to review

## Known constraints

## Focus areas

- bugs/regressions
- missing tests/checks
- privacy/security
- rollback/handoff gaps
- inconsistencies with existing project rules

## Do not

- do not edit files
- do not change runtime
- do not contact external services unless explicitly allowed

## Expected output

Findings first, severity ordered, with file/line references where possible.
```

## Внедрение по проектам

### 1. OpenClaw Shared Memory / База знаний

Приоритет: высокий.

Почему: активный проект с privacy/RLS/Synology boundaries и уже существующими Phase/Evidence/Audit требованиями.

Внедрить:

- `projects/openclaw-shared-memory/docs/AGENT_BRIEF.md`
- `state/tasks/.../TASK_PACKET.md` для каждой фазы.
- `AUDIT_PACKET.md` перед Claude review.
- `EVIDENCE.md` обязателен для Phase 0/1/2.
- Запрет реального импорта памяти без отдельного approval.
- Synology deployment только после явного разрешения.

Статус:

- [ ] Создать/обновить AGENT_BRIEF.
- [ ] Завести актуальный phase task packet.
- [ ] Закрепить audit packet format.
- [ ] Проверить текущий dirty state и commit strategy.

### 2. NAS / Home Network / Synology DS925+ Migration

Приоритет: высокий после покупки железа.

Внедрить до любых изменений:

- `state/tasks/YYYY-MM-DD-synology-ds925-migration/PLAN.md`
- `PRECHECKS.md`
- `MIGRATION_CHECKLIST.md`
- `ROLLBACK.md`
- `EVIDENCE.md`

Обязательные gates:

- read-only audit старого DS218play;
- SMART/storage health;
- список shares/users/NFS/SMB mounts;
- выбор дисков и compatibility confirmation;
- no root-level DSM changes without approval;
- migration dry run or first-pass sync;
- verification before IP swap.

Статус:

- [ ] Создать migration task folder после подтверждения покупки/дисков.
- [ ] Снять read-only inventory.
- [ ] Подготовить copy/verification plan.

### 3. Alpha-Bot

Приоритет: средний/высокий.

Внедрить:

- `projects/alpha-bot/AGENT_BRIEF.md`
- отдельный `TASK_PACKET.md` для RAG/docs/bot/runtime изменений.
- Preflight: читать `.env` только из `projects/alpha-bot/.env`, не из `/opt`.
- Проверки: syntax/import smoke, bot dry run where safe, RAG index integrity, no secrets in output.
- Deployment boundary: правим только `projects/`, `/opt` не трогаем напрямую.

Статус:

- [ ] Создать AGENT_BRIEF.
- [ ] Создать стандарт проверок Alpha-Bot.

### 4. HumanLike Agent

Приоритет: средний.

Внедрить:

- `projects/humanlike-agent/AGENT_BRIEF.md`
- отдельный safety/privacy task packet для userbot изменений.
- Явный запрет внешних сообщений от имени пользователя без approval.
- Проверки: Telethon session health read-only, DB backup before migrations, no unsolicited sends.

Статус:

- [ ] Создать AGENT_BRIEF.
- [ ] Зафиксировать external-send approval gate.

### 5. Sites / SEO / Spectech

Приоритет: высокий для активных работ.

Внедрить:

- task packet для каждого сайта/домена.
- `EVIDENCE.md` с HTTP smoke, sitemap, schema, screenshots при UI.
- Separate live mirror vs deploy source distinction.
- No secret/token exposure in chat.
- Перед деплоем: explicit scope + rollback path.

Статус:

- [ ] Обновить `state/tasks/2026-07-21-spectech-site-audit/` шаблоном review gates.
- [ ] Создать reusable site smoke checklist.

### 6. Alpha BPR / Alpha Presale / Alpha Platform

Приоритет: средний, повышается при активных задачах.

Внедрить:

- task packet для демо/презентаций/кодовых изменений.
- Alpha product guardrail: читать product cheatsheet перед любыми продуктами Alpha.
- Alpha licensing guardrail: читать licensing playbooks перед расчётами.
- Evidence для демо: screenshots, routes, smoke, commit hashes.
- Handoff checklist при передаче customer-facing материалов.

Статус:

- [ ] Найти текущие canonical roots.
- [ ] Добавить/обновить AGENT_BRIEF там, где проект активен.

### 7. Presentations

Приоритет: средний.

Внедрить:

- intake form: audience, goal, source facts, brand style, approval.
- draft/export checklist.
- visual QA checklist: slide count, readable text, image rights/source, no unsupported claims.
- external-send approval gate.

Статус:

- [ ] Создать presentation task packet template.

### 8. RAG Pipeline / Knowledge Utilities

Приоритет: средний.

Внедрить:

- source provenance checklist.
- no raw private Synology data outside LAN.
- index build evidence: file counts, source paths, excluded paths, checksums where useful.
- retrieval QA sample.

Статус:

- [ ] Создать RAG evidence template.

### 9. Heartbeat / Cron / Background Agents

Приоритет: высокий.

Внедрить:

- для каждой cron/background задачи: owner, timeout, model, expected output, failure mode.
- auto-failover rules documented in task packet.
- resource usage tracking.
- context pressure handling: start fresh sessions or force compaction before long work.

Статус:

- [ ] Синхронизировать heartbeat/Codex scripts с новым task packet style.
- [ ] Зафиксировать context WARN response.

## Работа с внешними агентами

### Claude Code

Использовать для:

- independent code review;
- UX/edge-case review;
- plan critique;
- risk audit.

Не использовать как единственного исполнителя без task packet.

Правило:

- Claude получает `AUDIT_PACKET.md`, diff/artifact and boundaries.
- Output must be GO / GO_WITH_FIXES / NO_GO plus findings.

### Codex CLI / Subagents

Использовать для:

- implementation slices;
- repo inspection;
- tests/checks;
- artifact generation.

Правило:

- Implementation packet must include allowed/forbidden files.
- Subagent may not decide external deployment or risky changes.

### External tools / web / marketplaces

Использовать для:

- current prices/specs/laws/docs.

Правило:

- recommendations that affect spending require fresh source check.
- raw private data is not sent externally.

## Rollout plan

### Phase 0: Стандарты и шаблоны

Цель: создать reusable templates.

- [ ] Finalize this plan with Stanislav.
- [ ] Create `templates/agent-workflow/TASK_PACKET.md`.
- [ ] Create `templates/agent-workflow/AUDIT_PACKET.md`.
- [ ] Create `templates/agent-workflow/EVIDENCE.md`.
- [ ] Create `templates/agent-workflow/AGENT_BRIEF.md`.

### Phase 1: Активные проекты

Цель: применить к 2-3 текущим фронтам.

- [ ] OpenClaw Shared Memory.
- [ ] NAS DS925+ migration.
- [ ] Spectech/Sites active work.

### Phase 2: Остальные проекты

Цель: coverage without churn.

- [ ] Alpha-Bot.
- [ ] HumanLike.
- [ ] RAG pipeline.
- [ ] Presentations.
- [ ] Alpha BPR/Presale.

### Phase 3: Agent operations

Цель: сделать процесс привычным.

- [ ] Update HEARTBEAT.md if needed.
- [ ] Add cron/background task packet requirements.
- [ ] Add review packet to Claude wrappers.
- [ ] Document context pressure response.

## Stop conditions

Остановиться и спросить Станислава, если:

- процесс предлагается применить как обязательный регламент;
- нужно менять `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `MEMORY.md`;
- требуется root-level изменение Synology;
- требуется отправка сообщения/документа наружу;
- нужно раскрыть приватные данные в group/external context;
- изменение затрагивает production/deploy/access rights.

## Quality checklist

- [ ] Есть артефакт на диске.
- [ ] Scope и exclusions видны.
- [ ] Роли не превращены в фиктивную оргструктуру.
- [ ] Privacy/external-send boundaries указаны.
- [ ] Есть rollout phases.
- [ ] Есть project-by-project mapping.
- [ ] Есть open questions.

## Открытые вопросы

- Где хранить общие шаблоны: `templates/agent-workflow/`, `state/templates/`, skill proposal, или отдельный проектный каталог?
- Нужно ли оформлять это как reusable skill через Skill Workshop?
- Нужно ли после подтверждения обновить `AGENTS.md`, или лучше держать как отдельный регламент?
- Какие проекты считать активными прямо сейчас: shared memory, NAS migration, sites, Alpha-Bot, cleanup?
