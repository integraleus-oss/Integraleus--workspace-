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
