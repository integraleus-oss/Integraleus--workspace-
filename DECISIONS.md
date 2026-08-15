# DECISIONS

---
### ID: D-2026-03-07-01
TYPE: DECISION
STATUS: STABLE
DATE: 2026-03-07
TITLE: Memory baseline (anti-drift light)
CONTENT: Используем минимальную структуру памяти из 5 файлов: CONSTITUTION.md, STATE.md, DECISIONS.md, MEMORY.md, memory/YYYY-MM-DD.md.
RATIONALE: Достаточно для continuity без перегруза протоколами.

---
### ID: D-2026-03-07-02
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-03-07
TITLE: Memory update loop
CONTENT: После значимого обсуждения формируется Candidate memory block; запись в DECISIONS/STATE делается только после явного approve от пользователя.
RATIONALE: Сохраняем контроль качества и убираем шум.

---
### ID: D-2026-04-04-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-04-04
TITLE: Synology NAS — данные не покидают домашнюю сеть
CONTENT: Любые файлы и данные с Synology NAS (192.168.68.103, монтирование /mnt/synology/*) НЕ ДОЛЖНЫ покидать домашнюю сеть без явного разрешения Станислава. Запрещено: отправка в чаты/email/интернет, копирование на VPS/Garden/внешние серверы, включение содержимого в ответы на внешних поверхностях. Разрешено: локальная обработка на openclaw-home, показ результатов анализа Станиславу (без сырых данных). При необходимости передачи наружу — спросить разрешение.
RATIONALE: Прямое указание Станислава 04.04.2026. Личные данные не должны утекать.

---
### ID: D-2026-03-18-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-03-18
TITLE: Model routing and fallback policy
CONTENT: Ручной выбор пользователя имеет высший приоритет. По умолчанию main session работает на Sonnet. Opus используется для аналитики, коммерческих писем, расчётов, длинных документов и задач с высокой ценой ошибки. Codex используется для кода, shell/ssh/docker/devops, конфигов, отладки и технического исполнения. Fallback chains: routine = Sonnet → Codex → Opus; analysis = Opus → Sonnet → Codex; technical = Codex → Sonnet → Opus. При timeout/provider error/empty response/repeated transport failure допускается не более 1 retry, затем переход на следующую модель по приоритету; silent failure недопустим.
RATIONALE: Уменьшаем зависания и молчание агента, сохраняя качество на важных задачах и скорость на рутине.

---
### ID: D-2026-03-21-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-03-21
TITLE: Gateway-level fallback chains (Main + Garden)
CONTENT: На обоих серверах настроены fallback chains на уровне gateway (agents.defaults.model.fallbacks). Main: Opus (API key) → Codex (OAuth) → Qwen3-Coder-Free (OpenRouter). Garden: Codex (OAuth) → Qwen3-Coder-Free (OpenRouter). OpenRouter ключ: отдельный, общий для обоих серверов (profile openrouter:fallback / openrouter:garden). Мониторинг OAuth ошибок Garden добавлен в HEARTBEAT.md.
RATIONALE: Исключить простой при протухании OAuth или даунтайме провайдера. Три уровня: платный API key → OAuth подписка → бесплатная модель.

---
### ID: D-2026-03-23-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-03-23
TITLE: Маркировка оценочных суждений в документах
CONTENT: Все оценочные данные, субъективные суждения и приблизительные цифры в генерируемых документах должны быть явно помечены (например: «оценка автора», «приблизительно», «по экспертной оценке»). Фактические данные и проверяемые утверждения — без пометок. Цель: читатель всегда понимает, где факт, а где мнение/оценка.
RATIONALE: Честность и прозрачность перед читателем. Пользователь явно попросил ввести это правило.

---
### ID: D-2026-03-23-02
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-03-23
TITLE: Актуальность моделей в документах
CONTENT: При генерации документов, содержащих упоминания ИИ-моделей (названия, размеры, рекомендации), перед генерацией выполнять веб-поиск актуальных версий. Не использовать устаревшие поколения (например Qwen 2.5, если уже вышел Qwen 3.5). Указывать дату актуальности в документе.
RATIONALE: Модели обновляются быстро, документы с устаревшими рекомендациями вводят в заблуждение.

---
### ID: D-2026-03-28-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-03-28
TITLE: Не выдумывать цифры
CONTENT: Если не знаешь конкретную цифру (стоимость, объём, количество) — НЕ выдумывай. Варианты: (1) оставить пустым / плейсхолдером «[уточнить]», (2) написать «точный расчёт после аудита», (3) спросить у пользователя. Никогда не подставлять правдоподобную но выдуманную цифру — это хуже, чем пробел.
RATIONALE: Выдуманные цифры в коммерческих презентациях и документах подрывают доверие. Пользователь явно указал на проблему.

---
### ID: D-2026-04-01-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-04-01
TITLE: Resilience: fallback на ручной план
CONTENT: Если все AI-сервисы упали, процессы не должны встать. Cron-задачи имеют 3-уровневый fallback: основная модель → Qwen3-Coder-Free (OpenRouter) → GPT-5.4 (Codex OAuth). Если все три модели недоступны, задача логируется как failed и алертит пользователя в следующем хартбите. Критичные мониторинги (серверы, безопасность) никогда не зависят от одного провайдера. OpenRouter ключ добавлен в auth-profiles.json для isolated агентов.
RATIONALE: Тройной отказ 31.03.2026 показал, что без fallback на бесплатные модели система молчит. Принцип из статьи aigenthub.ru: если AI упал, процессы не встают.

---
### ID: D-2026-04-01-02
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-04-01
TITLE: Автономия: граница «делаю молча» vs «спрашиваю»
CONTENT: Делаю молча (без спроса): чтение файлов, web search, проверки статусов, обновление heartbeat-state, memory-файлы, коммиты в workspace. Предлагаю и жду подтверждения: отправка сообщений наружу, удаление файлов/данных, изменение конфигов (openclaw.json, auth-profiles), рестарт сервисов, apt upgrade, изменение cron-задач, изменение SOUL.md/AGENTS.md. Исключение: если пользователь дал явное «делай» — выполняю без повторных вопросов.
RATIONALE: Чёткая граница убирает лишние вопросы на рутине и сохраняет контроль на важном. Вдохновлено режимом «советчик → автономия» из aigenthub.ru.

---
### ID: D-2026-06-04-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-06-04
TITLE: OpenClaw/Codex/Claude token and limit monitoring
CONTENT: OpenClaw can directly monitor OpenAI Codex OAuth usage via `openclaw models status`: 5-hour and weekly remaining windows with reset times. Claude CLI `auth status` only shows login and subscription type; direct Claude remaining-limit monitoring currently uses interactive `/usage` via a short tmux probe; statusline `rate_limits` should replace that if exposed through a stable file/API. OpenClaw session/context tokens and cron run usage are available via status/sessions/cron history. API-key quota exhaustion is monitored mostly through per-run usage and log/error patterns. Every heartbeat must run `scripts/heartbeat-token-limits.sh`, alerting on Codex 5h <20%, Codex week <15%, active session context >80%, Claude 5h usage >=80%, Claude weekly usage >=85%, and new rate-limit/auth/fallback/context-overflow log events.
RATIONALE: Станислав попросил настроить слежение за лимитами токенов аккаунта и предупредительные алерты, чтобы Codex/Claude/OpenClaw не уходили в silent failure.

---
### ID: D-2026-06-07-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-06-07
TITLE: Main Codex account limits switch at 20%
CONTENT: Heartbeat monitoring must run `scripts/codex-account-limit-switch.mjs` through `scripts/heartbeat-token-limits.sh`. The script probes each configured main Codex OAuth profile directly with Codex app-server `account/rateLimits/read` using isolated `authProfileId` requests. If the first account in `openai-codex` order is below 20% remaining on either the 5-hour or weekly window, or is blocked, and the other configured account is above 20% remaining on both windows and not blocked, it rewrites `openclaw models auth order --provider openai-codex` to put the healthier account first. If both accounts are low/blocked, it warns instead of switching blindly.
RATIONALE: Станислав попросил следить за лимитами на обоих Codex аккаунтах и переключать порядок, когда активный аккаунт падает ниже 20%, но только если второй реально здоровее.

---
### ID: D-2026-06-04-02
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-06-04
TITLE: Alpha BPR Historian integration order is SDK-first
CONTENT: Для Alpha BPR первый live smoke истории делаем через официальный Alpha.Domain.Client SDK: read-only browse/init тегов через Alpha.Server и короткий history read через Alpha.Historian. RMap не является первым шагом по умолчанию; это второй этап/SQL-слой, если он нужен или специалисты подтвердят его как штатный путь для стенда. Reports проверяется отдельным smoke после подтверждения history access, base URL, template/report id, auth/session behavior и URL/template variables. Dev PostgreSQL `54329` на main — это локальная BPR БД, не Home/RMap target.
RATIONALE: Alpha.Domain.Client подтверждён install-folder docs и KB SCADA Systems как официальный SDK-путь к Runtime/Historian и требует меньше вмешательства в стенд. RMap требует изменений PostgreSQL через extension/FDW/user mapping/grants, поэтому должен идти после SDK-smoke или только при явном DB-admin окне.

---
### ID: D-2026-06-04-03
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-06-04
TITLE: Local Codex CLI from OpenClaw uses codex-local
CONTENT: Внутри OpenClaw обычный `codex` наследует `CODEX_HOME=/home/stanislav/.openclaw/agents/main/agent/codex-home` и поэтому может показывать `Not logged in`, даже когда пользовательский Codex в `~/.codex` авторизован. Для запуска именно локального пользовательского Codex из OpenClaw использовать `/home/stanislav/.local/bin/codex-local`, который снимает `CODEX_HOME` и вызывает `/usr/bin/codex`. Перед внешней/API-работой через Codex проверять, что OpenAI endpoints идут через NL VPN (`awg0`, source `10.8.1.19`).
RATIONALE: Станислав одобрил memory candidate после подключения локального Codex. Это предотвращает путаницу между OpenClaw internal Codex home и обычным локальным Codex CLI.

---
### ID: D-2026-06-04-04
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-06-04
TITLE: Prefer local Codex CLI for heavy local work
CONTENT: Максимально эффективный текущий режим: OpenClaw Codex остаётся основным голосом и координатором Telegram-сессии, а `/home/stanislav/.local/bin/codex-local` является предпочтительным внешним помощником для тяжёлой локальной работы и первым agent-level fallback перед `ollama/phi3:instruct`, когда агент уже получил управление. Использовать `codex-local` чаще и проактивно для больших/долгих локальных задач: анализ кода, конфигов, логов, генерация и проверка патчей, smoke/review, второй проход по рискованным техническим выводам. Запускать его в целевой рабочей папке с узким промптом и минимально нужным контекстом, чтобы не сжигать токены на весь main workspace. Для чтения/ревью использовать read-only; для правок — workspace-write только в целевом проекте, затем независимо проверять diff и тесты. Не заявлять, что `codex-local` уже является gateway-level model fallback: для автоматической цепочки OpenClaw runtime `OpenClaw Codex -> local codex-local -> Ollama` нужен отдельный provider/adapter.
RATIONALE: Станислав попросил чаще подключать локальный Codex, потому что у него больше доступных лимитов. Реалистичная и безопасная схема сейчас — использовать local Codex как внешний CLI-инструмент агента и первый ручной fallback, не притворяясь, что он уже интегрирован в gateway-level fallback chains.

---
### ID: D-2026-06-05-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-06-05
TITLE: Alpha BPR uses a controlled 12-document development baseline
CONTENT: Для Alpha BPR обязательным является управляемый комплект из 12 baseline-документов в `/home/stanislav/projects/alpha-bpr/docs/baseline/`: Product Scope MVP, System Architecture, Module Requirements, Implementation Design, Development Validation Plan, API Specification, Database Schema Specification, Algorithm Specification, Template Schema Specification, QA/Golden Tests, Roadmap/Epic Breakdown и Definition of Done. Матрица трассировки связывает требования, реализацию, проверки и пробелы. Каждое изменение поведения, API, БД, алгоритма, шаблона или критериев приемки должно одновременно обновлять соответствующие документы и тесты. Реализованное, целевой MVP и заблокированные внешние контракты должны быть явно разделены.
RATIONALE: Станислав подтвердил необходимость формального комплекта документов, чтобы руководство разработкой и команда Alpha BPR работали по единым инженерным правилам.

---
### ID: D-2026-06-06-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-06-06
TITLE: Main OpenClaw Codex account fallback order
CONTENT: Для агента `main` рабочая конфигурация: каноническая основная модель `openai/gpt-5.5` с Codex runtime (`agentRuntime.id=codex`); config-level `auth.order.openai` может содержать Codex OAuth profile ids `openai-codex:stasiintegraleus@gmail.com` -> `openai-codex:integraleus55@gmail.com`, а effective runtime auth для `openai/gpt-5.5` идёт через authProvider `openai-codex`, где effectiveProfiles должны быть этими же двумя профилями в том же порядке. Фактическое переключение: `openai/gpt-5.5` + `openai-codex:stasiintegraleus@gmail.com` -> `openai/gpt-5.5` + `openai-codex:integraleus55@gmail.com` -> model fallback `ollama/phi3:instruct`. Отдельной третьей gateway-ступени `codex/gpt-5.5+oauth` сейчас нет: это не отдельный fallback после двух аккаунтов, а тот же Codex runtime/authProvider, через который работает `openai/gpt-5.5`. В model fallback не держать legacy routes `codex/gpt-5.5` и `openai-codex/gpt-5.5`. Проверка конфигурации: `openclaw models status --json`, `openclaw config get auth.order --json`, `openclaw models auth order get --provider openai-codex`, `openclaw models fallbacks list`; live account проверять отдельной `/codex account`, когда Gateway command path отвечает.
RATIONALE: Станислав попросил сделать порядок без выдумок и ошибок: использовать canonical OpenClaw route `openai/gpt-5.5`, переключать нужные Codex OAuth-аккаунты внутри runtime auth, а на Ollama переходить только как model fallback.

---
### ID: D-2026-06-07-02
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-06-07
TITLE: Deliverable tasks start with an artifact
CONTENT: Для любой обещанной deliverable-задачи (документы, demo-pack, презентация, скрипт, код, архив, отчёт) работа считается начатой только после появления минимального артефакта на диске. В первые 5-10 минут нужно создать целевую папку/файл или черновик. Рядом должен быть видимый чеклист в README/TODO или самом артефакте. Статусы давать только по фактам: какие файлы созданы/изменены, `git status`, что проверено, последний релевантный commit. Если за 30 минут нет материального артефакта, нужно прямо сообщить Станиславу, что результата ещё нет и почему. Большие deliverable дробить на маленькие полезные шаги. Долгую работу не оставлять в неуправляемом фоне: либо доводить текущий turn до результата, либо заводить явный TaskFlow/cron/checkpoint.
RATIONALE: 2026-06-07 investor demo-pack для Alpha BPR не был доведён до артефакта из-за ухода в проверки, статусные ответы и удержания задачи "в голове". Станислав явно одобрил правило, чтобы такие сбои не повторялись.

---
### ID: D-2026-06-07-03
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-06-07
TITLE: Deliverable ready state requires files, verification, and git state
CONTENT: Готовность deliverable-задачи нельзя считать достигнутой по намерению, плану или устному статусу. Минимальный готовый инкремент должен иметь: файлы на диске, локальный чеклист/README со статусом, фактическую проверку, `git status`, и либо commit, либо явное сообщение, почему commit/export не сделан. Для Alpha BPR investor demo-pack текущий готовый инкремент — commit `541a6d5 Add Alpha BPR investor demo pack` с проверенным `docs/investor-demo/curl-flow.sh`.
RATIONALE: Станислав одобрил memory candidate после восстановления работы над investor demo-pack. Правило фиксирует практический критерий готовности, чтобы будущие deliverable не зависали в "почти сделано".

---
### ID: D-2026-06-08-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-06-08
TITLE: Consequential and critical changes require scoped confirmation
CONTENT: Для действий с последствиями сначала описывать действие, риск и границы изменения. Явный запрос Станислава считается подтверждением только на прямо указанную область. Любое расширение объёма, внешнее действие, отправка сообщений от имени пользователя, изменение runtime/system/project configs, зависимостей, БД, API endpoints, auth/security, бизнес-логики, destructive-операции и root-level изменения требуют отдельного явного подтверждения. Для критических файлов использовать маленькие атомарные изменения, двойную проверку, `git diff`, релевантные тесты/линтеры/type checks при наличии и фактический отчёт о файлах, проверках, `git status` и commit/export state. Для презентаций и других визуальных deliverable проверка ZIP/XML недостаточна: нужно проверять реальное отображение или хотя бы наличие видимых shape/content objects через профильный инструмент.
RATIONALE: Станислав прислал и одобрил правила безопасности после сбоя с пустой Alpha BPR презентацией. Правило фиксирует границы подтверждения и усиленную проверку критических зон, не отменяя автономное выполнение явно запрошенных безопасных действий.

---
### ID: D-2026-06-08-02
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-06-08
TITLE: Personal agent operating profile
CONTENT: Документ `agent_rules_for_personal_agent_2026-06-08.md`, присланный Станиславом 2026-06-08, принят как обязательный рабочий профиль персонального агента с приоритетом системных правил OpenClaw/Codex, `AGENTS.md`, `SOUL.md` и уже одобренных решений. Обязательные принципы: не говорить "готово" без проверяемого результата; не придумывать факты, команды, тесты, логи, файлы, ссылки или цитаты; перед кодовыми изменениями читать релевантный контекст, оценивать blast radius, проверять текущий diff и после изменений запускать применимые проверки; для внешних действий, деплоя, production restart, auth/env/config, БД/миграций, удаления данных, установки зависимостей и других труднообратимых действий получать явное подтверждение; длинные deliverable и operational задачи вести через task-local state `state/tasks/<date>-<slug>/status.md`; security incidents логировать структурно в `logs/security_log.json` без записи секретов; память пополнять только durable high-signal фактами без секретов и шума; финальный отчёт разделять на сделано, подтверждено, не проверено/риски.
RATIONALE: Станислав явно попросил изучить документ и сделать правила обязательными, затем ответил `Approve` на Decisions Candidate. Правило объединяет новый документ с уже действующим режимом безопасности, памяти и deliverable-протоколом.

---
### ID: D-2026-06-20-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-06-20
TITLE: Supervised local Codex and Claude CLI workflow
CONTENT: Для совместной работы локального Codex CLI и Claude Code CLI использовать supervised-схему: OpenClaw является диспетчером/супервизором, Codex по умолчанию writer/test-runner, Claude по умолчанию reviewer/second opinion, если явно не назначен writer. Новые задачи вести через `/home/stanislav/agent-runs/<date>-<slug>/` с `TASK.md`, `STATUS.md`, `HANDOFF.md`, `events.jsonl`, `logs/`, `artifacts/`. Для каждого проекта должен быть один активный writer; текущий writer фиксируется convention-only lock-файлом в `/home/stanislav/agent-runs/_locks/`. Второй агент читает, ревьюит и предлагает, но не правит проект без смены writer-lock. Запускать будущие Codex/Claude задачи из реального project root (`codex -C <project>`, `cd <project> && claude`), а не из `/home/stanislav`. Текущие Termius-сессии не переносить насильно: дождаться checkpoint, зафиксировать `STATUS.md`/`HANDOFF.md`, затем следующий шаг вести уже через supervised ledger. Dashboard v1 должен быть read-only; pause/stop/control кнопки добавлять только после стабильной наблюдаемости.
RATIONALE: 2026-06-20 аудит активных Termius-сессий показал, что Codex и Claude работали из `/home/stanislav`, состояние было размазано между терминалами, session logs, Synology exchange и git status, а single-writer граница не была явно зафиксирована. Станислав попросил подготовить безрисковый переход к схеме, где OpenClaw следит за работой агентов, а он может наблюдать через браузер/dashboard без терминалов.

---
### ID: D-2026-06-24-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-06-24
TITLE: Home Ollama local fallback prefers qwen2.5:3b over qwen3:4b
CONTENT: На openclaw-home `qwen3:4b` удалён после теста 2026-06-24: на CPU он давал около 15-16 tok/s, имел тяжёлый Qwen3 reasoning overhead и часть простых задач не завершал финальным ответом до лимита. `qwen3:8b` не ставить без отдельной причины. `qwen2.5:3b` прошёл 4 из 5 локальных fallback-задач и одну частично: около 22-25 tok/s, без reasoning overhead; использовать его как основной кандидат для быстрого локального OpenClaw fallback. Для exact code-only/strict-format задач применять более жёсткий system prompt/шаблон или постобработку.
RATIONALE: Станислав одобрил Memory Candidate после сравнительного теста `qwen3:4b` и `qwen2.5:3b` на задачах: русский текст, Alpha-док, короткий код, классификация сообщения, RAG-вопрос. Отчёты: `reports/local-ai/qwen3-4b-eval-2026-06-24.md` и `reports/local-ai/qwen2.5-3b-eval-2026-06-24.md`.

---
### ID: D-2026-06-24-02
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-06-24
TITLE: MVP work uses Claude for product thinking and Codex for execution
CONTENT: Для MVP-работы использовать гибридный режим: Claude Code применять для product thinking, архитектуры, UI/design и ревью сложных фич; Codex применять как быстрый writer/test-runner для итераций, shell/git/tests/API и каркасов. Большие MVP вести через supervised Ralph-like loop: `SPEC`/`TODO` -> small tasks -> tests -> commit -> review. Не запускать длинные автономные Codex loops при низкой weekly quota; сначала проверить текущие лимиты и при необходимости назначить Claude planner/reviewer, а Codex оставить для коротких исполнительских проходов.
RATIONALE: Станислав одобрил Memory Candidate после изучения Kinescope-ролика "Claude Code или Codex - что подходит для создания MVP" и предыдущего обсуждения Ralph Loop. Практический вывод: Claude Code надёжнее для целостного продукта, дизайна и сложной автономной работы; Codex быстрее и дешевле для инженерных итераций, но требует нарезки задач и контроля контекста.

---
### ID: D-2026-07-01-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-01
TITLE: Alpha BPR Home production-pilot closeout accepted
CONTENT: 2026-06-30 Alpha BPR Home production-pilot autonomously closed through backup/restore drill, restart/reboot soak, real host reboot gate, post-reboot readiness, HMI/BFF, Alpha.Reports, PS01/FILL Historian freshness, and final closeout commit `d479a68 Close Alpha BPR production pilot`. Remaining boundaries are human production sign-off, TLS/domain/CA/browser-trust decisions, missing future secrets/licenses, and explicit go-to-market/show/sell approval.
RATIONALE: Станислав одобрил Memory Candidate после финального отчёта по production-pilot closeout в Telegram topic `HOME:Alpha-BPR`.

---
### ID: D-2026-07-01-02
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-01
TITLE: Alpha BPR Home production-pilot release/show package accepted
CONTENT: Alpha BPR Home production-pilot baseline `d479a68 Close Alpha BPR production pilot` is tagged locally as `home-production-pilot-2026-06-30`. A docs-only release/show package was added and committed as `88ae13c Add Alpha BPR production pilot show package`, including release handoff, show route, pre-show checks, explicit boundaries, and next production-readiness backlog. The Alpha BPR repo was clean after the commit.
RATIONALE: Станислав одобрил Memory Candidate после выполнения release/handoff + show package для Telegram topic `HOME:Alpha-BPR`.

---
### ID: D-2026-07-01-03
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-01
TITLE: Alpha BPR production-readiness docs pack accepted
CONTENT: Alpha BPR production-readiness docs pack was added and committed as `423b12c Add Alpha BPR production readiness pack`. It includes a readiness checklist, monitoring/backup plan, TLS/sign-off decision sheet, and standalone HTML diagrams/charts with architecture, readiness flow, and backlog/backup cadence. The Alpha BPR repo was clean after the commit.
RATIONALE: Станислав одобрил Memory Candidate после выполнения production-readiness pack с диаграммами/графиками/архитектурными схемами для Telegram topic `HOME:Alpha-BPR`.

---
### ID: D-2026-07-02-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-02
TITLE: pm-claude-skills deferred for marketing and sales
CONTENT: Тему `pm-claude-skills` считать отложенной рабочей веткой для маркетинга, продаж и документов. Позже можно вернуться к выборочной адаптации skills под договоры, письма, КП и регламенты: `proposal-writer`, `contract-review`, `process-documentation`, `sop-writer`, `compliance-checklist`. С Alpha Presale эту ветку не смешивать.
RATIONALE: Станислав ответил `Делай` на Memory Candidate в Telegram topic `Общий офис / Маркетинг и продажи` после предложения зафиксировать эту тему как отложенную durable-ветку.

---
### ID: D-2026-07-07-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-07
TITLE: Test Home LLM GPU needs with rented GPU server first
CONTENT: Станислав рассматривает GPU для openclaw-home ради повышения уровня локальных LLM. Предпочтительный путь перед покупкой: сначала тестировать уровень моделей на арендованном GPU-сервере RTX 3090/4090 на 1-3 дня, а не покупать eGPU вслепую. eGPU к Home через USB4 считать экспериментом для проверки совместимости, не базовым вариантом; для устойчивого локального решения предпочтительнее отдельный NVIDIA GPU node минимум с 24GB VRAM.
RATIONALE: Станислав одобрил Memory Candidate после обсуждения стоимости, проката видеокарт и аренды GPU-серверов в Telegram direct 2026-07-07.

---
### ID: D-2026-07-23-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-23
TITLE: OpenClaw Shared Memory Phase 1.5 workflow pilot accepted
CONTENT: Phase 1.5 Agent Workflow integration for OpenClaw Shared Memory completed in commit `4bee741`: project-specific workflow artifacts, redacted Phase 2 review packet, security precheck, evidence, sample Memory Candidate, explicit backup `BYPASSRLS` runbook step, typed negative-test assertions, and automated local pilot runner were added. No Synology, runtime, real-memory, or external-review action was performed.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-23 after the Phase 1.5 completion report.

---
### ID: D-2026-07-23-02
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-23
TITLE: OpenClaw Shared Memory Phase 2 prep package accepted
CONTENT: Phase 2 preparation for OpenClaw Shared Memory completed in commit `c5dbe0d`: a reproducible Synology deploy package/archive/checksum flow, rollback procedure, deployment evidence, and draft Phase 3 approval request were added. The package was inspected for required files, checksum, no secrets, no wildcard bind, and tests passed. Synology deployment, OpenClaw runtime/MCP changes, real-memory import, external review, and push remain blocked until explicit approval.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-23 after the Phase 2 prep package completion report.

---
### ID: D-2026-07-23-03
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-23
TITLE: OpenClaw Shared Memory Phase 3 network boundary
CONTENT: For OpenClaw Shared Memory Phase 3, the deployment network boundary is local-network-only: default bind is Synology LAN `192.168.68.103`; VPN may be enabled only as a private route into the home LAN and does not imply WAN/public exposure. Tailscale-only bind is optional later hardening only after explicit selection.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-23 after clarifying that the system must work only in the local network, while VPN may be enabled.

---
### ID: D-2026-07-23-04
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-23
TITLE: OpenClaw Shared Memory pilot accepted on openclaw-home
CONTENT: OpenClaw Shared Memory pilot was deployed on `openclaw-home` instead of Synology in commit `2607be5 feat: deploy shared memory pilot on openclaw home`. It runs as `openclaw-shared-memory-home-postgres`, bound to LAN `192.168.68.125:55432`, with runtime secrets outside git, role-scoped users, verified RLS/privacy smoke, mirror allowlist, backup, and restore drill. OpenClaw runtime/MCP remains disconnected, real memory was not imported, and Synology remains storage/backup candidate only.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-23 after the openclaw-home pilot deployment report.

---
### ID: D-2026-07-23-05
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-23
TITLE: OpenClaw Shared Memory Phase 4 prep accepted
CONTENT: Phase 4 prep for OpenClaw Shared Memory completed in commit `d61d50a docs: prepare shared memory phase 4 read-only gateway`: read-only MCP/API gateway task packet, precheck, approval request, evidence, MCP tool allowlist, TODO update, and `run_phase4_readonly_preflight.py` were added. The preflight verified reader-only smoke access, privacy denial, audit retrieval, candidate filtering, and direct write denial. OpenClaw runtime/MCP was not connected, Gateway was not restarted, real memory was not imported, and Phase 4 runtime wiring remains blocked until separate explicit approval.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-23 after the Phase 4 prep completion report.

---
### ID: D-2026-07-23-06
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-23
TITLE: OpenClaw Shared Memory Phase 4 read-only MCP runtime accepted
CONTENT: Phase 4 runtime read-only MCP wiring for OpenClaw Shared Memory completed in commit `520b15d feat: wire shared memory read-only mcp runtime`: `openclaw-shared-memory-readonly` was registered in OpenClaw `mcp.servers`, backed by `scripts/mcp_readonly_server.py`, exposing only provider-safe read-only tools `search_memory`, `get_with_audit`, and `list_candidates`. Runtime secrets remain outside git/config, Gateway was not restarted, MCP cache was reloaded, configured MCP smoke and read-only preflight passed, write tools and real-memory import remain blocked, and markdown memory remains fallback/source.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-23 after the Phase 4 runtime read-only MCP wiring report.

---
### ID: D-2026-07-24-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-24
TITLE: OpenClaw Shared Memory Phase 5 prep accepted
CONTENT: Phase 5 memory import prep for OpenClaw Shared Memory completed in commit `9ab9a56 docs: prepare shared memory phase 5 import prep`: controlled markdown-to-candidate import task packet, import precheck, approval request, evidence, synthetic fixture, and dry-run planner were added. The planner validates candidate previews without DB writes, refuses protected real-memory paths such as `MEMORY.md` by default, and rejects secret-like content. Real-memory import, candidate writes, write MCP exposure, promotion/reject/archive/supersede, and replacing markdown as source of truth remain blocked until separate explicit approval.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-24 after the Phase 5 prep completion report.

---
### ID: D-2026-07-24-02
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-24
TITLE: OpenClaw Shared Memory Phase 5 tiny candidate import accepted
CONTENT: Phase 5 tiny candidate-write pilot for OpenClaw Shared Memory completed in commit `215e8ee feat: import shared memory phase 5 candidates`: exactly three approved `DECISIONS.md` OpenClaw Shared Memory entries were imported into the DB as `project` privacy `candidate` records only. Candidate IDs are `19309b52-9d04-47cb-83c8-fba1024522f4`, `31ea008d-0ce1-4032-a499-2a75e34f6de6`, and `bf8b3331-7957-4e17-84e7-d9cf062b0c7c`. Each candidate has a `proposed` audit event, no promotion occurred, write MCP tools remain unexposed, and markdown remains the source of truth.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-24 after the Phase 5 tiny candidate-write pilot completion report.

---
### ID: D-2026-07-24-03
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-24
TITLE: OpenClaw Shared Memory Phase 5 promotion accepted
CONTENT: Phase 5 manual promotion pilot for OpenClaw Shared Memory completed in commit `64a3593 feat: promote shared memory phase 5 candidates`: the three owner-approved imported candidate records `19309b52-9d04-47cb-83c8-fba1024522f4`, `31ea008d-0ce1-4032-a499-2a75e34f6de6`, and `bf8b3331-7957-4e17-84e7-d9cf062b0c7c` were promoted from `candidate` to `shared` with privacy class `project`. Audit for each record shows `proposed` then `promoted`; the candidate queue no longer lists them; reader search finds all three shared records; write MCP tools remain unexposed; markdown remains source of truth until a separate migration decision.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-24 after the Phase 5 manual promotion pilot completion report.

---
### ID: D-2026-07-24-04
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-24
TITLE: OpenClaw Shared Memory Phase 6 skill decision prep accepted
CONTENT: Phase 6 Agent Workflow skill decision prep for OpenClaw Shared Memory completed in commit `d33f5d4 docs: prepare shared memory phase 6 skill decision`: pending Skill Workshop proposal `agent-workflow-v2-20260722-747ac395f5` was inspected through Skill Workshop and found pending/create/clean. It was compared against actual Shared Memory Phase 1.5-5 evidence. Recommendation is to revise before applying because the proposal is structurally sound but stale relative to real gates for read-only MCP, candidate-only import, manual promotion, privacy classes, markdown source-of-truth, role-scoped DB access, and dirty-worktree discipline. No Skill Workshop lifecycle action was performed.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-24 after the Phase 6 skill decision prep completion report.

---
### ID: D-2026-07-24-05
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-24
TITLE: OpenClaw Shared Memory Phase 6 skill proposal revision accepted
CONTENT: Phase 6 Agent Workflow proposal revision completed in commit `27b1f08 docs: revise shared memory agent workflow proposal`: pending Skill Workshop proposal `agent-workflow-v2-20260722-747ac395f5` was revised from Shared Memory Phase 1.5-5 evidence and is now `v2`, `pending/create/clean`. The revised proposal adds concrete gates for artifact-first execution, separate approvals for runtime/DB/import/promotion/write MCP/source-of-truth changes, Memory Candidate admission, privacy classes, markdown source-of-truth boundary, role-scoped DB practice, Synology/home-LAN boundaries, and dirty-worktree discipline. No apply/reject/quarantine action, DB write, runtime/MCP change, import, promotion, or migration decision was performed.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-24 after the Phase 6 proposal revision completion report.

---
### ID: D-2026-07-24-06
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-24
TITLE: OpenClaw Shared Memory Phase 6 Agent Workflow skill applied
CONTENT: Phase 6 final Agent Workflow skill decision completed in commit `b592e94 docs: apply shared memory agent workflow skill`: Skill Workshop proposal `agent-workflow-v2-20260722-747ac395f5` was inspected as `v2 pending/create/clean`, applied through Skill Workshop, and re-inspected as `applied/create/v2/clean`. Live skill file `skills/agent-workflow-v2/SKILL.md` was created and committed. Phase 6 is closed; no Shared Memory DB write, runtime/MCP change, import, promotion, or migration/source-of-truth decision was performed. Follow-up: live skill text still contains proposal-era wording and should be cleaned up only through a separate Skill Workshop update/apply cycle.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-24 after the Phase 6 final skill decision completion report.

---
### ID: D-2026-07-24-07
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-24
TITLE: OpenClaw Shared Memory Phase 6.1 Agent Workflow skill wording cleanup accepted
CONTENT: Phase 6.1 Agent Workflow live skill wording cleanup completed in commit `27625a3 docs: clean up agent workflow skill wording`: Skill Workshop update proposal `agent-workflow-v2-20260724-8fa58cd92a` was created for live skill `agent-workflow-v2`, inspected as `pending/update/v1/clean`, applied, and re-inspected as `applied/update/v1/clean`. Live `skills/agent-workflow-v2/SKILL.md` now says `Status: live skill`; proposal-era phrases `pending proposal, not applied`, `not a live rule`, `not installed`, and `later apply` are absent. No workflow gate was intentionally changed, and no Shared Memory DB write, runtime/MCP change, import, promotion, or migration/source-of-truth decision was performed.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:1751` on 2026-07-24 after the Phase 6.1 skill wording cleanup completion report.

---
### ID: D-2026-07-25-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-25
TITLE: OpenClaw Redis runtime state and queue layer direction
CONTENT: Для OpenClaw Redis рассматривается не как память агента, а как временный runtime state / queue layer для диспетчера задач. Первый spike: heartbeat alert suppression. Later MVP candidates: Telegram inbound dedupe and task locks / active run registry. Все Redis-данные временные, с TTL, без сырого приватного контента; Postgres и Markdown остаются source of truth, Redis можно потерять без потери важных фактов. Подготовлены артефакты `state/tasks/openclaw-runtime-state-queue/TODO.md` и `docs/ops/openclaw-runtime-state-queue.md`; код и установка Redis пока не выполнялись.
RATIONALE: Stanislav approved the Memory Candidate in Telegram topic `HOME:2257` on 2026-07-25 after the OpenClaw Runtime State & Queue Layer MVP artifact and integration audit were created.

---
### ID: D-2026-07-26-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-26
TITLE: Cross-topic memory file boundaries
CONTENT: When the same personal agent coordinates work across Telegram topics, keep `DECISIONS.md` as the approved durable decision register, keep `STATE.md` as a compact cross-topic index of current truth, gates, and pointers, keep `memory/YYYY-MM-DD.md` as chronological daily narrative, and keep detailed task work in `state/tasks/...`, `docs/ops/...`, or equivalent project artifacts. Do not duplicate long topic snapshots in `STATE.md`; move detailed history to daily memory and task packets. Live skills must change only through Skill Workshop, and runtime/code/Gateway changes require separate explicit approval.
RATIONALE: Stanislav explicitly approved the proposed Memory Candidate in the main Telegram direct chat on 2026-07-26 after reviewing how `DECISIONS.md`, `STATE.md`, daily memory, task packets, live skills, Redis, code, and Gateway should be separated across topics.

---
### ID: D-2026-07-28-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-07-28
TITLE: mattpocock skills selective adaptation
CONTENT: Treat `mattpocock/skills` as a reference library for engineering discipline, not as a package to install wholesale into OpenClaw. First adapted directions are: pending Skill Workshop proposal `debugging-feedback-loop-20260728-74757679c8` for a standalone feedback-loop-first debugging skill, and applied `agent-workflow-v2` update `agent-workflow-v2-20260728-6b35940606`, which restored the full workflow gates while adding debugging default, two-axis review, tracer-bullet task slicing, and domain vocabulary discipline. The initial update proposal `agent-workflow-v2-20260728-e5caa32aae` was applied but required the corrective integrated update `agent-workflow-v2-20260728-6b35940606` so the live skill remained a full workflow rather than proposal text.
RATIONALE: Stanislav approved the Memory Candidate in the main Telegram direct chat on 2026-07-28 after the repo review and pending proposal creation, then explicitly approved applying the `agent-workflow-v2` update and approved this memory correction.

---
### ID: D-2026-07-31-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-07-31
TITLE: hmi-screen-design as Alpha.HMI HPHMI review layer
CONTENT: Use the approved `hmi-screen-design` archive as the detailed HPHMI/ISA-101 reference layer for Alpha.HMI and SCADA mnemonic design/review. It supplies `CORE.md`, `COMPACT.md`, focused references, `rules/hmi-rules.json` with 84 atomic rules, and `assets/hphmi-palette.json`. The higher-priority Alpha Platform-first rule remains in force: requested Alpha Platform projects must be built with actual Alpha Platform means, while `hmi-screen-design` guides screen hierarchy, palette, object library style, labels, analog displays, alarms, trends, faceplates, controls, schematic completeness, rendered-screenshot review, and future lint/check tooling. Map the package to actual Alpha.HMI/WebViewer, Alpha.HMI.Alarms, alpha.hmi.charts, Alpha.Historian, Alpha.Reports, Alpha.Security, and Alpha.Imitator rather than treating it as an Alpha project or replacing local Alpha docs/examples.
RATIONALE: Stanislav approved the Memory Candidate in the main Telegram direct chat on 2026-07-31 after the Telegram archive was recovered, inventoried, and reviewed in `state/tasks/2026-07-31-alpha-archive-review/REPORT.md`.

---
### ID: D-2026-08-01-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-08-01
TITLE: Alpha Platform TZ requirements must be Alpha-native
CONTENT: Если в любом техническом задании на систему АСУ ТП, SCADA/HMI или диспетчеризацию написано сделать проект средствами программного продукта Альфа платформа, то весь заявленный проект должен выполняться средствами Альфа платформы, включая серверную часть проекта и HMI. Внешние HTML/JS/API helper-страницы допустимы только как диагностика и не засчитываются как операторская поверхность, управление, аварии, тренды, архив, отчёты, безопасность, аудит, серверная конфигурация или приёмочное evidence. Сдаваемые требования нужно закрывать через нативные артефакты и проверенный runtime Alpha.Server, Alpha.Domain/AccessPoint, Alpha.HMI/WebViewer, Alpha.HMI.Alarms, alpha.hmi.charts, Alpha.Historian, Alpha.Reports, Alpha.Security, Alpha.Imitator и другие актуальные компоненты из `docs/alpha_platform/PRODUCT_CHEATSHEET.md`, если они требуются ТЗ.
RATIONALE: Stanislav approved the Memory Candidate in the main Telegram direct chat on 2026-08-01 after rejecting the PS01 hybrid Alpha.HMI/WebViewer plus external HTML command helper as non-compliant with the TZ, then clarified that the rule applies to any ASU TP or dispatching TZ that names Alpha Platform and includes both server-side project work and HMI.
## 2026-08-08 — Производственные Alpha-проекты как локальный reference corpus

Decision: использовать локально сохранённые комплекты `12105`, `14443` и
`20167` как reference corpus реальных паттернов Alpha.HMI, Alpha.DevStudio и
Alpha.Server для Alpha-HMI-DEV, Alpha-BPR и Alpha-Presale.

Boundaries:

- переносить только проверенные архитектурные знания и адресные рекомендации;
- не копировать в продуктовые проекты сырые IP-адреса, endpoint-имена,
  абсолютные пути, бинарные зависимости, backup/output-дубли и небезопасные
  настройки;
- не считать статически найденные `.hmi`, `.omobj` и `.omx` доказательством
  импорта, компиляции или runtime;
- каждый повторно используемый объект должен пройти текущие Alpha.HMI gates:
  происхождение, статическую проверку, адаптацию, импорт/компиляцию и требуемое
  runtime/live evidence;
- исторические библиотеки адаптировать к текущим компонентам Alpha Platform.

Evidence:

- `state/tasks/2026-08-08-shared-alpha-project-examples/REPORT.md`;
- `state/tasks/2026-08-08-shared-alpha-project-examples/TODO.md`;
- SHA-256 исходного архива:
  `f380f1b91757de2a63eb0adbbb901f6f5cbd104020328df7611bb43ebdb05895`.

Approval: Stanislav approved the Memory Candidate in Telegram direct chat on
2026-08-08.

---
### ID: D-2026-08-10-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-08-10
TITLE: Reusable verification sequence for native Alpha Platform projects
CONTENT: For subsequent native Alpha Platform projects, use the verified sequence `backup -> native compile/rebuild -> timer-driven self-reset command logic -> direct runtime/OPC UA scenario tests -> HMI write permission/ACL test plus state readback -> mandatory rollback with configuration hashes, ports, services, and process/data-exchange tick verification`. Do not count an HMI command as end-to-end merely because the form renders live values or the button reaches TCPServer: the write must be accepted by an explicitly permitted client, change the command/runtime state, and return confirmed feedback to HMI. Keep command processing on an independent periodic timer rather than a self-triggering dependency cycle. When restoring a working stand, tolerate and explicitly report configured-tag versus deployed-node drift; verify the actually exchanged node set instead of assuming the CSV count equals runtime availability.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-10 after the NS1 iteration proved native compile/rebuild, Start/Stop and LOCAL/FAULT/NOT_READY runtime scenarios, exposed the Alpha.Om self-trigger cycle and the PS01 122-configured/95-runtime node drift, and restored PS01 with hashes, services, ports, and stable 95-tag exchange verified. Native HMI button write/readback remains an open gate until TCPServer client ACL is corrected and the scenario is repeated from HMI.

---
### ID: D-2026-08-11-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-11
TITLE: Deterministic Codex-Claude engineering orchestration on OpenClaw Home
CONTENT: Build the joint engineering workflow as OpenClaw orchestration with Codex as implementer, fresh-session Claude Code as independent structured reviewer, deterministic pre-review and post-fix gates, and a policy/state machine as the only acceptance authority. LLMs may create task packets, implementation, and findings, but may not vote on acceptance or silently lower severity. The protocol must include a JSON reviewer contract with severity floors and evidence fields; stable finding and occurrence identities; human-only accepted-risk/false-positive resolution; targeted fix verification plus one final full review; iteration and FAILED_INFRA budgets; whitelist-only infrastructure failure classification with unknown/repeated failures escalated; task-packet lint; task-type evidence manifests; isolated worktree runtime/dependencies; red-to-green evidence for critical changes; and advisory-by-default visual smoke. Target states are ACCEPTED, REWORK, FAILED_INFRA, and ESCALATED. Implementation order: reviewer JSON Schema and examples, state-machine/policy specification, then fresh `claude -p` wrapper integration and a bounded dry run.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-11 after jointly closing the acceptance, severity, review-churn, infrastructure-failure, evidence-completeness, and runtime-isolation gaps.

---
### ID: D-2026-08-12-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-12
TITLE: Local accepted integration point for the Codex-Claude orchestrator runner
CONTENT: Treat local commit `9f00f70` (`feat(orchestrator): add local integration runner`) as the accepted integration point for the Codex-Claude orchestrator runner. Keep this workflow local without GitHub or push. The accepted point is protected by an encrypted Synology backup stored inside the home network. The next functional slice is connecting the runner to real local Codex and Claude launches with deterministic handling of `REWORK`, `FAILED_INFRA`, `ESCALATED`, and `ACCEPTED`; unattended activation and runtime/config changes remain separate approval gates.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-12 after the integration slice passed targeted Claude closure, 14/14 integration tests, 84/84 core regression tests, py_compile and whitespace checks, was committed locally as `9f00f70`, and was included in a verified encrypted Synology backup.

---
### ID: D-2026-08-12-02
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-12
TITLE: Accepted local production-CLI baseline for the Codex-Claude orchestrator
CONTENT: Treat local commit `59d42a3` as the completed local production-CLI baseline for the Codex-Claude orchestrator. The accepted chain includes the bounded production entrypoint from `f5afeea`, strict task-packet and approved-worktree validation, fixed local Codex/Claude launchers, at most two Codex attempts and one policy-authenticated REWORK, fail-closed handling, deterministic policy admission, and a successful isolated canary ending `ACCEPTED / R17_ACCEPT`. Keep the workflow local without GitHub or push. The baseline is protected by a verified GPG AES-256 Synology backup inside the home network. The next implementation slice is an automatic builder for trusted review manifest, binding, and evidence inputs derived from the actual Codex change and observed gates. Unattended execution, cron, Gateway/runtime/config changes, deploy, and automatic commit/push remain separate approval gates.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-12 after the production CLI passed 58/58 integration tests, 84/84 core tests, py_compile and whitespace checks, independent targeted closure `PRODUCTION_CLI_CLOSURE_PASS`, and a one-attempt isolated canary accepted mechanically as `R17_ACCEPT`; commits `f5afeea` and `59d42a3` were created locally and the encrypted Synology backup was decrypted and checksum-verified.

---
### ID: D-2026-08-13-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-13
TITLE: Canonical origin and dedicated Metrika counter for special-tech.ru
CONTENT: Use `https://www.special-tech.ru` as the single canonical origin for `special-tech.ru`. Redirect HTTP and non-www variants to it with permanent 301 redirects while preserving path and query string. Use dedicated Yandex Metrika counter `110922935` for this site.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram topic `HOME:990` on 2026-08-13 after production redirects were deployed and verified, canonical/robots/sitemap/HSTS were checked, and the active dedicated counter was confirmed through the Metrika API.

---
### ID: D-2026-08-13-02
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-13
TITLE: Distinct roles for the two SPETSTECH sites
CONTENT: Treat `specialtechnology.ru` as the content and SEO site and `https://www.special-tech.ru` as the commercial site for license calculations, consultations, and leads. Do not duplicate full articles between the domains. Connect them with relevant contextual links, preserve source attribution through UTM campaign `cross_site_navigation`, and measure each direction separately with Yandex Metrika goals `content_site_click` on counter `110922935` and `commercial_site_click` on counter `107569860`.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram topic `HOME:990` on 2026-08-13 after the same-period Metrika comparison, production publication of cross-site routes, creation of directional goals, Chromium UTM verification, production backup, and Yandex recrawl submission.

---
### ID: D-2026-08-13-03
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-13
TITLE: Accepted trusted-input builder for the local Codex-Claude orchestrator
CONTENT: Treat local commit `7fa0a0b` (`feat(orchestrator): seal trusted review inputs`) as the accepted trusted-input builder increment for the local Codex-Claude orchestrator. The production cycle derives digest-bound review manifests, projection bindings, evidence, policy inputs, and sealed reviewer contracts from the observed Git change and gate results. The managed chain permits at most two Codex implementation attempts followed, when policy requires it, by one separate review-only final-full leg; the final-full leg must record `SKIPPED_REVIEW_ONLY` and must not launch a third Codex attempt. Exact-JSON, schema, semantic, seal, and policy admission remain fail-closed, with separately bounded format-only and contract-only repair paths. Keep the workflow local without GitHub, push, deploy, unattended activation, or automatic commits unless separately approved.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-13 after clean canary r17 completed attempt 1 as authenticated REWORK, attempt 2 as targeted closure, and attempt 3 as review-only final-full, ending `ACCEPTED / R17_ACCEPT`. Verification passed with 83/83 integration tests, 84/84 accepted-core tests, `py_compile`, and `git diff --check`; the scoped increment was committed locally as `7fa0a0b`.

---
### ID: D-2026-08-15-01
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-15
TITLE: Reviewer control-character transport edge closed for the local orchestrator
CONTENT: Treat local commits `bb14bbc` (`fix(orchestrator): reinforce reviewer transport retries`) and `a5a7e55` (`test(orchestrator): reproduce reviewer control edge`) as the closed reviewer control-character transport increment. The controller states the decoded `U+0000` through `U+001F` prohibition from the initial review launch onward, supplies safe textual handling for intended newlines and tabs, and preserves strict fail-closed validation without sanitizing or silently rewriting reviewer JSON. Regression coverage must reproduce decoded `U+0009` in a contract-repair candidate and prove bounded recovery. Real-project smoke r3 reached `R17_ACCEPT`; post-review smoke r4 passed strict transport/schema and exposed the next independent semantic blocker, `bad_evidence_reference`. Keep the source `home-agent-factory` unchanged until a separate transfer/commit decision.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-15 after focused 12/12, integration 83/83, core 84/84, `py_compile`, and `git diff --check` passed; independent commit review findings were addressed; r3 proved terminal acceptance and r4 proved the control-character edge no longer caused admission failure while semantic evidence-reference errors still failed closed.

---
### ID: D-2026-08-15-02
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-15
TITLE: Reviewer evidence-reference discipline closed for the local orchestrator
CONTENT: Treat local commit `48c85c3` (`fix(orchestrator): enforce reviewer evidence discipline`) as the closed reviewer evidence-reference increment. Reviewer guidance now requires referential integrity against the supplied evidence manifest on the initial review and every bounded retry; dangling evidence IDs remain strictly rejected. Any `artifact_ref` must carry a verified `content_digest`, and reviewers may not invent digests. Initial transport-invalid verdicts receive the structured validator report and use the existing bounded contract-repair path without weakening or sanitizing the validator. Real-project smoke r8 passed strict transport, schema, and semantic validation with zero errors and ended terminal `ACCEPTED / R17_ACCEPT`; its final-full leg was review-only and did not launch a third Codex implementation attempt. Keep this workflow local: no push, deploy, Gateway/cron change, or unattended activation without a separate approval gate.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-15 after focused 15/15, integration 86/86, core 84/84, `py_compile`, and `git diff --check` passed; smoke r8 proved strict evidence-reference admission, bounded fail-closed transport repair, review-only final-full handling, and terminal acceptance.

---
### ID: D-2026-08-15-03
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-15
TITLE: Controlled-manual-pilot release checkpoint for the local orchestrator
CONTENT: Treat local commit `b300207` and annotated tag `orchestrator-local-cli-r1-2026-08-15` as the release checkpoint for the tested Codex-Claude local CLI orchestrator. Its operational status is `READY FOR CONTROLLED MANUAL PILOT; NOT ACTIVATED`. Manual pilot admission remains deny-by-default per repository and requires an explicit task packet with exact project commit/path, allowed and forbidden files, deterministic gates, budgets, timeouts, evidence paths, and commit/push/deploy boundaries. The ceiling remains two Codex implementation legs plus one review-only final-full leg, with bounded reviewer repair and fail-closed stop conditions. This checkpoint does not authorize Gateway, OpenClaw runtime/config, cron, systemd/daemon, unattended execution, automatic commit, push, deploy, or modification of the clean source `home-agent-factory`. The checkpoint is protected by a verified GPG AES-256 Git-bundle backup on Synology inside the home network; recovery verification passed external and internal SHA-256, decryption, `git bundle verify`, complete-history/ref checks, and exact commit matching.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram direct chat on 2026-08-15 after the readiness packet was committed as `b300207`, the 86/86 integration suite and Python compile passed, the annotated tag was created, the encrypted Synology backup was independently restored and verified, and post-release evidence was committed as `c35644b` without activation or Gateway/cron changes.

---
### ID: D-2026-08-15-04
TYPE: DECISION
STATUS: ACTIVE
DATE: 2026-08-15
TITLE: Controlled manual pilot returns the local orchestrator for rework
CONTENT: The controlled manual pilot of the local Codex-Claude orchestrator is complete with status `RETURN FOR REWORK; NOT ACTIVATED`. Four bounded real tasks ran in isolated detached `home-agent-factory` worktrees at `3d9c27e`: T01, T03, and T04 reached `ACCEPTED / R17_ACCEPT`; T02 correctly stopped at `ESCALATED / R12_FINDINGS_EXHAUSTED` after its two permitted Codex attempts. The 86-test integration suite passed, failure drills remained fail-closed, the source repository stayed clean, and no push, deploy, Gateway, cron, systemd, daemon, or unattended mode was enabled. Two blocking workflow defects remain: carried `prior-findings.json` evidence preserves IDs/statuses but omits the descriptions and evidence needed for honest targeted re-verification; foreground `Ctrl-C` stops the process without orphan continuation but produces an unhandled traceback and no structured `INTERRUPTED` terminal record. Keep the orchestrator local, manual, and not activated. Before any OpenClaw integration, fix both defects, add regression tests, and repeat only the T02 re-verification and live interruption drills with complete sealed evidence.
RATIONALE: Stanislav explicitly approved the Memory Candidate in Telegram topic `HOME:2922` on 2026-08-15 after reviewing the completed manual-pilot report, four trial outcomes, 86/86 test result, failure drills, unchanged source repository, and the recommendation to return for bounded rework.
