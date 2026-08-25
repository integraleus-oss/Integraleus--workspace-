# STATE.md — Текущее состояние проектов и серверов

_Обновляется из любой сессии после значимых действий. Main session читает при старте._

## Текущий рабочий режим

- **Подтверждение:** явный запрос Станислава считается подтверждением только на указанную область; расширение объёма, внешние действия, конфиги, зависимости, БД, API/auth/security, бизнес-логика, destructive/root-level изменения требуют отдельного подтверждения.
- **Критические изменения:** маленькие атомарные патчи, предварительное описание действия/риска, `git diff`, релевантные тесты/линтеры/type checks при наличии, фактический статус по файлам/проверкам/git/commit.
- **Deliverable:** сначала артефакт/checklist на диске, затем рассуждения; готовность подтверждать реальной проверкой. Для PPTX/визуальных файлов не считать достаточными только `unzip`/XML-проверки.
- **Cross-topic память:** `DECISIONS.md` хранит только approved durable decisions; `STATE.md` — компактный cross-topic index текущей правды, gates и pointers; `memory/YYYY-MM-DD.md` — хронологию; `state/tasks/...` и `docs/ops/...` — подробности конкретных задач. Не дублировать длинные snapshots в `STATE.md`; live skills менять только через Skill Workshop; runtime/code/Gateway changes требуют отдельного approve. Durable decision: `D-2026-07-26-01`.
- **Личные правила агента:** действуют правила из `agent_rules_for_personal_agent_2026-06-08.md`: не выдавать намерение за выполнение, не придумывать факты/логи/тесты/файлы, вести task-local state для длинных задач, логировать security incidents в `logs/security_log.json` без секретов, а в финале разделять сделано/подтверждено/не проверено.

## Серверы

### Main VPS (155.212.227.115)
- **OS:** Ubuntu 24.04.4 LTS, kernel 6.8.0-107-generic
- **CPU:** AMD EPYC 7763, **RAM:** 11 ГБ, **Disk:** 145 ГБ (21% занято)
- **OpenClaw:** 2026.5.12
- **Ollama:** 0.17.6, модель nomic-embed-text (embedding для Alpha-Bot RAG)
- **Alpha-Bot:** работает (bot.py), RAG через ollama + ChromaDB
- **HumanLike Agent:** установлен, миссии не настроены
- **SSH:** key-only, UFW active (22/80/443)
- **Tailscale:** `openclaw-vps` / `100.127.146.46`; принимает subnet routes (`--accept-routes=true`). Доступ к домашней подсети `192.168.68.0/24` идёт через `tailscale0` via `openclaw-home`.
- **Synology через Tailscale:** с VPS проверено 2026-06-11 11:03 MSK: `192.168.68.103` ping 3/3 ~17.5 ms, DSM `5000/5001`, NFS `2049`, SSH `2222` доступны.
- **Каналы:** Telegram default OK -> `main`; Telegram `home-monitor` / `@Homegnom_bot` OK -> agent `home-monitor`; Discord OK
- **Последнее обновление:** 2026-05-17

### OpenClaw Telegram Routing
- **default Telegram account:** основной бот, обычные direct-сессии и группа `-1003781262788` остаются на agent `main`.
- **home-monitor Telegram account:** `@Homegnom_bot`, accountId `home-monitor`, allowlist только `109592643`, routed to agent `home-monitor`, session `dmScope=per-account-channel-peer`.
- **home-monitor agent model:** `ollama/phi3:instruct`; token нового бота хранится в `~/.openclaw/openclaw.json` и не должен попадать в ответы/логи.

### Домашний принтер
- **Модель:** Pantum CP1100, подключён к Synology `S218` (`192.168.68.103`) по USB.
- **Сетевая очередь:** Synology CUPS/IPP queue `usbprinter1`.
- **Основной URL для подключения:** `ipp://192.168.68.103:631/printers/usbprinter1`.
- **Bonjour/AirPrint-style имя:** `Pantum CP1100 @ S218`.
- **Windows LPR:** сервер `192.168.68.103`, очередь `usbprinter1`.
- **Автозапуск на Synology:** `openclaw-printer-share.service` запускает `/usr/local/sbin/openclaw-printer-share.sh`.
- **Чеклист настройки:** `state/printer-synology-setup-2026-06-19.md`.
- **Оговорка:** тестовая страница не печаталась; если задания не идут, первым делом проверить питание и USB-кабель Pantum ↔ Synology, потому что низкоуровневый USB-скан на Synology не показывал текущий не-хаб USB-девайс.

### OpenClaw Model/Auth Routing
- **main default model:** `openai/gpt-5.5` with Codex runtime (`agentRuntime.id=codex`).
- **main Codex account auth order:** config-level `auth.order.openai` lists `openai:stasiintegraleus@gmail.com` -> `openai:integraleus55@gmail.com`; compatibility command `openclaw models auth order get --provider openai-codex` still reports the legacy aliases `openai-codex:*` in the same order.
- **main effective switch sequence:** `openai/gpt-5.5` + `openai:stasiintegraleus@gmail.com` -> `openai/gpt-5.5` + `openai:integraleus55@gmail.com` -> `ollama/phi3:instruct`.
- **main model fallback:** after Codex OAuth profile failover, fall back directly to `ollama/phi3:instruct`; there is no separate third gateway step named `codex/gpt-5.5+oauth`, because Codex OAuth is the runtime/authProvider used by `openai/gpt-5.5`.
- **main Codex limit switching:** `scripts/heartbeat-token-limits.sh` now runs `scripts/codex-account-limit-switch.mjs`, which checks both configured Codex OAuth accounts directly. If the first account in order has less than 20% remaining on either 5-hour or weekly quota, or is blocked, and the other account has more than 20% remaining on both windows, heartbeat rewrites the OpenAI/OpenClaw-Codex auth order to put the healthier account first.
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
- **OS:** Ubuntu 24.04.4 LTS, kernel 6.17.0-35-generic
- **CPU:** AMD Ryzen / GEEKOM A6, **RAM:** 58 GiB detected, **SSD:** ~1 ТБ NVMe (12% занято на 2026-07-09)
- **Tailscale IP:** 100.114.189.16, **LAN:** 192.168.68.125
- **Tailscale subnet router:** approved/active route `192.168.68.0/24`; `AllowedIPs` and `PrimaryRoutes` include the home subnet. IP forwarding enabled via `/etc/sysctl.d/99-tailscale-subnet-router.conf`. Audit 2026-07-09: Tailscale itself is up, but `tailscale status` reports it cannot reach the configured DNS servers.
- **Synology NFS mounts:** `S218` (`192.168.68.103`) is mounted on Home under `/mnt/synology/` via `/etc/fstab` with `_netdev,noatime`: `Documents`, `video`, `music`, `homes`, `surveillance`, `PlexMediaServer`, `Lost`. Current fstab backup from setup: `/etc/fstab.openclaw-synology-20260619-1849.bak`. Setup checklist: `state/synology-home-mount-2026-06-19.md`.
- **Home ↔ PC file exchange:** use Synology folder `/mnt/synology/Documents/OpenClawExchange` for local file transfer between Stanislav's PC and Home. Files in this exchange are intended to stay inside the home network unless Stanislav explicitly permits otherwise.
- **OpenClaw:** 2026.6.10, gateway local loopback `127.0.0.1:18789`, Telegram default and home-monitor OK; update 2026.6.11 available.
- **OpenClaw model fallback gap:** audit 2026-07-09 found `openclaw models fallbacks list` returns `Fallbacks (0): none`, despite the recorded intended chain `openai/gpt-5.5` OAuth profile failover -> `ollama/phi3:instruct`. Treat this as a current config drift until restored or intentionally revised.
- **Ollama local fallback candidate:** `qwen2.5:3b` установлен и после теста 2026-06-24 является основным кандидатом для быстрого локального OpenClaw fallback: около 22-25 tok/s на CPU, 4/5 задач пройдены и одна частично. `qwen3:4b` удалён из Ollama из-за reasoning overhead и непригодной скорости/зависания на простых задачах; `qwen3:8b` не ставить без отдельной причины. Evidence: `reports/local-ai/qwen2.5-3b-eval-2026-06-24.md`.
- **Роль:** рабочий Alpha Platform стенд + Home OpenClaw host; hardening делать осторожно через карту зависимостей Alpha/n8n/Caddy
- **SSH:** active on `0.0.0.0:22`/`[::]:22`; audit 2026-07-09 effective `sshd -T` shows `passwordauthentication no`, `kbdinteractiveauthentication no`, `permitrootlogin without-password`.
- **UFW:** active, default deny incoming; разрешены LAN/private/Tailscale ranges, `80/443 Anywhere`, `631/tcp Anywhere` for CUPS; audit 2026-07-09 did not show public `22 Anywhere` in UFW rules.
- **RustDesk remote desktop:** installed 2026-06-19, version `1.4.7`, service `rustdesk.service` enabled/active, Ubuntu ID `232083379`. Works from Windows after unlocking GNOME Wayland session; keep GNOME autolock disabled for remote access (`org.gnome.desktop.screensaver lock-enabled=false`, `org.gnome.desktop.session idle-delay=0`). Do not store the unattended password in repo files.
- **OpenClaw security audit:** audit 2026-07-09 reported 0 critical · 5 warn · 2 info; trusted mode (`workspaceOnly=false`, `exec.security=full`, elevated) допустим только при доверенном доступе. Doctor also reports group-writable state dir (`~/.openclaw` mode 775), plaintext secret-bearing fields in `openclaw.json`, legacy state, and orphan transcripts; do not run `openclaw doctor --fix` blindly.
- **Alpha services:** audit 2026-07-09 showed system failed units: none. Alpha Platform, Alpha BPR API/HMI/sim/bridges, Docker, nginx, Ollama, OpenLDAP, RustDesk, Tailscale, fail2ban, CUPS, and OpenClaw gateway are running.
- **Alpha issues:** `alpha.security.agent` logs 23 Alpha Platform security violations every 5 minutes; classify before production/demo claims. Alpha BPR HMI/BFF `readyz` still reports UI `operator-reviewer-prototype.html`, while the latest integrated HMI work may expect a newer shell.
- **User failed units:** audit 2026-07-09 found `claude-token-refresh.service` and `snap.firmware-updater.firmware-notifier.service` failed. Claude refresh logged HTTP 403 code 1010 at 00:45, 02:46, and 08:49 MSK, while some runs skipped because the token was still valid.
- **Последний аудит:** 2026-07-09; report `audits/home/2026-07-09-home-audit.md`.

#### Local Codex / Claude CLI
- **Codex CLI:** `/usr/bin/codex` 0.140.0 installed; normal user profile `~/.codex` is logged in with ChatGPT.
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
- **Supervised Codex/Claude workflow:** current base is `/home/stanislav/agent-runs/`. It contains templates, `_bin/agent-task`, `_locks/`, `_dashboard/server.py`, and first ledger `/home/stanislav/agent-runs/2026-06-20-alpha-bpr-coordination/`. Use this structure for future coordinated local Codex/Claude work instead of unmanaged Termius-only sessions.
- **MVP workflow policy:** for MVP work, use Claude Code for product thinking, architecture, UI/design, and review of complex features; use Codex as fast writer/test-runner for shell/git/tests/API scaffolding and small implementation iterations. Large MVPs should run as a supervised Ralph-like loop: `SPEC`/`TODO` -> small tasks -> tests -> commit -> review. Do not start long autonomous Codex loops while weekly Codex quota is low; check current limits first.
- **Current supervised lock:** `/home/stanislav/agent-runs/_locks/alpha-bpr.lock` is convention-only with `writer=claude`, `reviewer=codex`, because the current Claude Termius session has the latest `alpha-bpr` edit. Do not start another `alpha-bpr` writer until checkpoint and lock update.
- **Dashboard state:** read-only dashboard stub exists at `/home/stanislav/agent-runs/_dashboard/server.py`; syntax/help verified, but no persistent dashboard service has been started. Planned first URL when explicitly started: `http://openclaw-home:8787/agents`.
- **Transition artifacts:** audit `state/codex-claude-coordination-audit-2026-06-20.md`; plan `state/codex-claude-transition-plan-2026-06-20.md`.

## Проекты

### Marketing/Sales Claude Skills
- **Статус:** первый пакет оформлен как pending Skill Workshop proposals, live skills не применялись.
- **Пакет:** `/home/stanislav/agent-runs/2026-07-03-marketing-sales-docs/`.
- **Proposals:** `sales-docs-pipeline-20260703-ceccd2cb19`, `proposal-writer-20260703-26994ecfcd`, `contract-review-20260703-92512ee0ba`, `process-documentation-20260703-973960ed4e`, `sop-writer-20260703-e76b518e77`, `compliance-checklist-20260703-dd98a819d3`; all scanned clean.
- **Проверка:** пакет включает workflow docs, review notes, pilot test case, фактический mini-run output, exported proposal bodies и Claude review. Применять только после явного approve.
- **Durable decision:** `D-2026-07-02-01`.

### Cross-Session Snapshot — 2026-07-04 08:31 MSK
- **Alpha BPR offline demo distribution:** topic `HOME:14` reported generated artifacts in `/home/stanislav/projects/alpha-bpr/dist/`: `alpha-bpr-offline-20260703-demo.tar.gz`, `.run`, `.ps1`, and unpacked folder. Runtime smoke passed on temporary ports `18080/15095`: API `/health`, HMI/BFF `/readyz`, and workflow through create order, setpoints, release, plc status, dose record, and report. Windows `.exe` was not produced because available `7zCon.sfx` was Linux ELF; current Windows self-extracting option is `.ps1`. No commit was made.
- **Marketing/Sales docs skills:** topic `OFFICE:6242` reported 6 pending Skill Workshop proposals and package `/home/stanislav/agent-runs/2026-07-03-marketing-sales-docs/`; live skills not applied, explicit approval required.
- **Direct Synology printer:** Windows printing through Synology/Pantum is working; temporary non-admin DSM user `print-win` remains in use for printing.

### Cross-Session Snapshot — 2026-07-05 07:32 MSK
- **Alpha BPR productization:** topic `HOME:14` reported an uncommitted slice adding line clearance, live HMI prototype binding to `/api/batches/{id}/ebr`, QA exception disposition through backend, recipe lifecycle statuses/endpoints (`InReview`, `Approved`, `Superseded`; `submit-review`, `approve`, `make-effective`, `supersede`), report dataset schema v4, XLSX/PDF line-clearance evidence, OpenAPI snapshot, and state/task packet updates. Verification reported: `dotnet build AlphaBpr.sln`, focused unit 103 passed, focused integration/OpenAPI/migration/report 39 passed, OpenAPI contract passed, JS syntax OK, `git diff --check` clean, deprecated Alpha names scan clean. Working tree still uncommitted.
- **Alpha-HMI-DEV designer brief:** topic `HOME:30` produced a designer prompt for an Alpha.HMI Configurator engineering prototype. Required status truth: RC1/package gate passed, `confirmed_import_compile`, `runtime render: blocked_viewer_segfault`, and `ENGINEERING_GO_WITH_HUMAN_GATES`; do not imply final release.
- **Alpha Presale designer brief:** topic `HOME:85` produced a designer prompt for a dense presale workbench focused on readiness, missing data, risks, architecture/HMI/historian/security sections, and handoff; not a landing page, CRM, or automatic final TKP generator.
- **Local Claude Code CLI:** direct chat reported successful reauthorization as `integraleus50@gmail.com`; `claude -p` returned `CLAUDE_OK`, `/usage` works, OAuth codes not stored.
- **Marketing/Sales skills coordination:** topic `OFFICE:6242` audit found duplicated marketing/sales skill work across Home and Main/Mine. Recommended source of truth is Home/openclaw-home; useful RU guardrails from Main/Mine should be merged via `skill_workshop update`; Main/Mine should stop parallel marketing/sales skill creation.

### Cross-Session Snapshot — 2026-07-07 07:31 MSK
- **Alpha BPR regulated-candidate v3/audit export:** topic `HOME:14` is mid-closeout, not committed. Task `state/tasks/2026-07-06-alpha-bpr-regulated-candidate-v3/TODO.md` has every checklist item complete except `Commit(s) created`. Current `/home/stanislav/projects/alpha-bpr` tree is dirty with audit export/review API, docs, tests, migration, OpenAPI snapshot changes, plus untracked `regulated-candidate-validation-v3.md`, `test-results/v3/`, `AuditReviewRecord.cs`, and migration `20260706062500_AuditReviewRecords.cs`. Latest commits before the dirty work: `f7ee753 feat: enforce QA release regulated candidate reauth`, `96e0ae0 docs: define QA release operations boundary`, `034c77f feat: capture QA release reauth evidence`. Recorded verification: build passed; focused RegulatedCandidate 6/6; focused audit/migration 15/15; v3 focused integration TRX 12/12; full `dotnet test AlphaBpr.sln --no-build` passed with 333 unit / 165 integration / 3 skipped after OpenAPI snapshot refresh; `git diff --check` clean; deprecated Alpha names scan clean.
- **Telegram direct/Home operations:** recent direct chat accepted and logged Main-to-Home transfer statuses for Document Pipeline and archives; Home local model trial found `qwen3.5:9b` unsuitable as fallback because smoke timed out in verbose thinking, while `gemma4:e4b` was attempted; Synology/Pantum printer queue confirmed as `usbprinter1` with IPP URL `http://192.168.68.103:631/printers/usbprinter1`.

### Cross-Session Snapshot — 2026-07-09 07:31 MSK
- **Alpha BPR integrated HMI / live QA:** topic `HOME:14` ended with uncommitted tracked changes in `/home/stanislav/projects/alpha-bpr`: integrated HMI prototype, HMI prototype README, HMI/BFF demo route, and smoke script. QA tab now reads `/api/demo/reviewer`; live data updates release status, gates, dosing evidence, QA signature, and audit review row. Verification reported: `dotnet build src/AlphaBpr.Api -c Release` OK, `python3 -m py_compile scripts/demo/hmi_bff_demo_server.py` OK, `git diff --check` OK, HMI/BFF smoke OK, desktop/mobile screenshots OK, temporary API/BFF/Chromium processes stopped. No commit was made.
- **Alpha BPR integrated HMI tab smoke:** topic `HOME:1` confirmed in real Chromium that all 7 tabs select the expected screen: `Библиотека рецептов`, `Редактор процедур`, `Формулы`, `Партии`, `Ревью QA`, `Версии и аудит`, `Согласование`; result `ALL_OK=true`.
- **Telegram media delivery caveat:** first attempt to send Alpha BPR screenshots directly from project `state/tasks/...` failed because local media path was outside allowed directories. Workaround used in topic `HOME:14`: copy screenshot to `~/.openclaw/media/alpha-bpr/...` and send from there; this succeeded. Prefer OpenClaw-managed/allowed media paths for future Telegram attachments.
- **Direct GPU context:** latest direct-chat context remains Intelion GPU trial recommendation: first test should be RTX 3090 24GB + 64GB RAM + Ubuntu + SSH for about one day before buying local GPU/eGPU hardware.

### Cross-Session Snapshot — 2026-07-10 07:41 MSK
- **Alpha BPR customer guides:** topic `HOME:14` completed and committed `140e53e docs: finalize customer guide package` in `/home/stanislav/projects/alpha-bpr`. Package includes mobile UI pass for integrated HMI, hash-link fixes for `#formula`, `#procedure`, `#batches`, `#diff`, customer-safe screenshots embedded into role guides, HTML/DOCX/PDF exports, a 10-15 minute customer demo script, and reproducible exporter `export_customer_guides.py`.
- **Main customer guide artifact:** `/home/stanislav/projects/alpha-bpr/docs/customer/user-guides/exports/Alpha_BPR_Customer_User_Guides_RU.pdf`. Separate PDF/DOCX exports exist for Operator, Technologist, QA, Admin, and Demo Script. Reported verification: customer docs/exports contain no internal URLs/commands or deprecated Alpha names, HMI/BFF `/readyz` ready, BPR reachable, PDF A4, DOCX screenshots embedded, `git diff --check` clean, and repo `git status` clean.
- **Earlier HOME:1 context now partly superseded:** HOME:1 had stated the integrated HMI was demo-like and still needed scaling/material balance/yield/workflow persistence work. Later HOME:14 work completed customer guide packaging, but this does not by itself mean the BPR/MES implementation is production-complete.
- **Telegram media delivery caveat repeated:** gateway log at 2026-07-10 07:11 MSK shows a failed `message.action` attachment because `/home/stanislav/projects/alpha-bpr/docs/user-guide/alpha-bpr-user-guide-ru.md` was outside allowed media directories. Prefer `~/.openclaw/media/...` or other allowed transfer paths for Telegram file attachments.

### Cross-Session Snapshot — 2026-07-11 07:31 MSK
- **Alpha BPR customer show pack:** topic `HOME:14` completed and committed `afacf65 docs: add customer show pack` in `/home/stanislav/projects/alpha-bpr`.
- **Main show-pack artifact:** `/home/stanislav/projects/alpha-bpr/docs/customer/show-pack/Alpha_BPR_Customer_Show_Pack_v1.zip`.
- **ZIP contents:** README, customer presentation `PPTX + PDF` on 9 slides, overall guide `PDF + DOCX`, role guides `Operator / Technologist / QA / Admin` in `PDF + DOCX`, demo script `PDF + DOCX + MD`, and pilot plan `PDF + MD`.
- **Added support files:** `rehearsal-notes-ru.md`, `rehearsal-run-20260710.md`, `build_customer_presentation.py`, and `build_show_pack.py`.
- **Reported verification:** ZIP opens and contains 19 files; presentation converts to 9-slide PDF; README/Pilot Plan PDFs are A4; unpacked ZIP scan found no internal URLs/commands/deprecated Alpha names; `git diff --check` clean; repo `git status` clean.

### Cross-Session Snapshot — 2026-07-13 11:33 MSK
- **Alpha BPR controlled recipe workflow:** topic `HOME:14` recovered after the earlier Telegram timeout and committed `b9d3bef feat: add controlled recipe change workflow` plus `5b5dbcc fix: harden controlled recipe activation` in `/home/stanislav/projects/alpha-bpr`.
- **Alpha BPR productization roadmap:** same topic then committed `eada47e docs: add Alpha BPR productization roadmap`, adding `docs/product/alpha-bpr-productization-roadmap-20260713.md` and updating project `README.md`, `STATE.md`, and `TODO.md`.
- **Reported verification/status:** integration verification in the task artifact reached 170/173 passed with 3 skipped before closeout; current repo check at 11:33 MSK showed clean `git status`.
- **Спецтех topic lookup:** topic `HOME:990` answered read-only lookup for Спецтех/site-related Telegram topics and imported Discord-transfer references; no files changed.

### Cross-Session Snapshot — 2026-07-13 12:57 MSK
- **Alpha BPR sellable MVP productization:** topic `HOME:14` continued and committed `d4ea66b docs: add Alpha BPR sellable MVP productization plan`, `9c7f679 ops: add Alpha BPR sellable MVP gate`, and `61c0044 docs: record Alpha BPR sellable MVP batch report`.
- **Sellable MVP artifacts:** added backup automation plan/scripts, disabled systemd timer/service examples, UI hardening evidence, commercial pilot/reporting/security/validation/deployment/release docs, customer target preflight, sellable-MVP gate, and batch report.
- **Reported verification/status:** task artifact `state/tasks/2026-07-13-sellable-mvp-autonomous-batch/TODO.md` marks all nine productization points, Codex/Claude reviews, fixes, verification, and commit complete. Repo check at 12:57 MSK showed clean `git status`.
- **Open issue:** topic `HOME:14` exceeded 80% session context again and hit a second Telegram isolated polling timeout at 12:55 MSK; Telegram ingress restarted and deep status is OK, but further work in that topic should start from a fresh/compacted context to avoid another abort.

### Cross-Session Snapshot — 2026-07-13 14:32 MSK
- **Alpha BPR sellable MVP gate closeout:** topic `HOME:14` resolved the remaining sellable-MVP UI warning and committed `2eae22e fix: close Alpha BPR sellable MVP UI warning` plus `1ae1177 docs: record Alpha BPR sellable MVP gate pass`.
- **Gate status:** task `state/tasks/2026-07-13-sellable-mvp-ui-warn-closeout/TODO.md` is complete; strict sellable-MVP gate evidence `/tmp/alpha-bpr-sellable-mvp-gate/evidence-20260713105826/summary.md` recorded `PASS`, failures `0`, warnings `0`.
- **Context/Telegram status:** the earlier topic 14 over-80% context WARN cleared after compaction; topic 14 is now about 31% context, Telegram deep status is OK, and `/home/stanislav/projects/alpha-bpr` was clean at heartbeat.

### Cross-Session Snapshot — 2026-07-14 07:32 MSK
- **Alpha BPR owner baseline approved:** topic `HOME:14` recorded explicit owner approval: sellable-MVP candidate is allowed for pilot/commercial scoping only; production, Part 11/QMS, SLA, retention deletion, off-machine backup, live restore, customer plant integration, and root-level Synology changes remain not approved without separate explicit decision.
- **Alpha BPR decision artifacts:** owner baseline approval was recorded in Alpha BPR docs/decision layer and committed as `64a90a9 docs: approve Alpha BPR owner decision baseline`, with tag `alpha-bpr-owner-baseline-approved-2026-07-13`.
- **Controlled recipe hardening:** after approval, topic `HOME:14` completed recipe review queue/make-effective hardening and committed `c0ec0f4 fix: harden controlled recipe review queue`. Reported verification: focused recipe tests PASS, OpenAPI contract test PASS, full `dotnet test -c Release` PASS with unit `340/340`, integration `176 passed / 3 skipped / 179 total`, `git diff --check` clean, worktree clean.
- **Next safe Alpha BPR step:** checkpoint/tag hardening after `c0ec0f4`, then rerun strict sellable-MVP gate on top of that commit before pilot execution package / customer integration preflight / approval proposals / commercial pilot SOW.
- **Спецтех topic lookup:** topic `HOME:990` remained read-only and identified `HOME/topic:990` as current "Сайт Спецтех", with related HOME topics `6242`, `85`, `30` and Discord-transfer threads for Спецтех/Сайт/бот/UMOSS.
- **Server update status:** direct session reported no emergency: Ubuntu has about 46-47 upgradable lines, OpenClaw update `2026.6.11` is available while current app is `2026.6.10`, reboot not required, gateway/Telegram OK. Suggested update window: after Alpha BPR tests are idle.

### Cross-Session Snapshot — 2026-07-18 07:31 MSK
- **Alpha BPR external-check/user guide:** topic `HOME:14` reported commit `ea75837 docs: add single-file Alpha BPR user guide PDF` in `/home/stanislav/projects/alpha-bpr`. The output is one Russian PDF, 10 A4 pages, with all 8 screenshots embedded; service English words such as `Checklist/walkthrough/runtime/feedback` were removed except unavoidable product/UI labels like `Данные: trial`.
- **Alpha BPR delivery/evidence:** the PDF was sent to the Telegram topic as message `1392`; reported checks: PDF not encrypted, 10 A4 pages, problem-word scan clean, public monitor `PASS 2026-07-18T00:05:46+03:00`, repo clean at HEAD `ea75837`.
- **Alpha BPR earlier reviewer-fix context:** topic `HOME:1` had reported public HMI/BFF/reviewer fixes and checks; this is now partly superseded by the later topic `HOME:14` guide/public-monitor package. Current topic `HOME:14` context is over 80%, so further work there should start from a fresh/compacted context.

### Cross-Session Snapshot — 2026-07-23 07:31 MSK
- **Спецтех site/SEO:** topic `HOME:990` reported that 4 updated blog post URLs plus sitemap were sent to Yandex Webmaster recrawl; Yandex accepted 5 URLs, remaining quota 466. Later same-topic context showed `/sitemap.xml` accepted successfully with 41 pages found; GSC manual indexing limit is exhausted for 2026-07-23, and a one-shot cron reminder is set for 2026-07-24 10:00 MSK to continue with `specialtechnology.ru/dpp-dobycha.html` and `www.special-tech.ru` priority pages (`/alpha-platform/`, `/podbor-scada/`, `/raschet-licenziy-alpha-platform/`, `/raschet-licenziy-scada/`, `/news/`). SEO crawl-signal fixes were committed separately as `4c74e70 Improve Spectech site crawl signals`; old local Alpha-agent task packet committed separately as `bb46c3d Add local Alpha agent rules task packet`. Current GSC guidance: do not touch `/lk/`, optionally remove red erroneous sitemap rows, and pull fresh GSC indexing/effectiveness reports in 7-14 days. Evidence reports: `/home/stanislav/projects/spectech-sites/artifacts/yandex-webmaster-recrawl-blog-seo-20260722T2146.md`, `/home/stanislav/projects/spectech-sites/artifacts/specialtechnology-gsc-indexing-20260723T1020.md`.
- **Alpha BPR HMI catalogs/recipes:** topic `HOME:14` reported commits `da10f13 feat: add postgres-backed hmi catalogs`, `6ae6f82 feat: persist hmi master recipes`, `81ddef7 feat: link hmi batches to recipe versions`, and `e7c8f43 feat: split hmi workflow roles`. Latest state: HMI batch cards store structured recipe reference fields; API requires/returns normalized `recipeRef`; HMI BFF and live EBR preserve recipe references; UI shows recipe link markers. Workflow roles are split so technologist creates/edits/submits recipes, QA reviews/returns/approves/makes effective, and operator executes batches; `recipes:review` policy and role-scoped HMI BFF keys were added. Reported verification includes focused authorization/API/migration/production-order tests, HMI-style integration coverage, Python compile, inline JS `node --check`, Chromium DOM smoke, `git diff --check`, and deprecated Alpha names scan clean.
- **Agent workflow / Shared Memory:** Phase 1.5-4 prep path is documented through commits `4bee741`, `c5dbe0d`, `9366827`, `2607be5`, and `ff2690a`. At this snapshot, the pilot remained LAN-bound on `openclaw-home`, Synology remained a storage/backup candidate, real memory was not imported, and runtime/MCP wiring still required a separate approval gate.

### Cross-Session Snapshot — 2026-07-24 07:31 MSK
- **Agent workflow / Shared Memory:** Phase 4 read-only MCP runtime is configured and smoke-verified. It exposes only `search_memory`, `get_with_audit`, and `list_candidates`; the container remains LAN-bound at `192.168.68.125:55432`. Phase 5 prep/import decisions were recorded, but write MCP, bulk import, promotion, and source-of-truth migration remain separate approval gates.
- **Alpha BPR HMI:** topic `HOME:14` verified the public Home link and then completed the approved stabilization package. Public URL is now `https://alpha-bpr.31.10.95.23.sslip.io/alpha-bpr-hmi/`; HTTP redirects to HTTPS; Let's Encrypt certificate is valid until 2026-10-22; BFF `/readyz` reports the public HTTPS URL; public monitor is `PASS 2026-07-24T10:28:58+03:00`; nginx and BFF are active. Commit: `57604ee fix: stabilize Alpha BPR public HMI route`. The fix removed the public HTML `127.0.0.1` stop-string leak and kept curated public workbench limited to HMI recipe/batch cards instead of exposing full live `/api/recipes` sandbox/dev prefixes. R2 audit pack committed as `d015ffd docs: add Alpha BPR public audit pack r2`; initial R2 ZIP sent to the topic: `alpha-bpr-public-audit-r2-20260724073631.zip`, SHA-256 `6a172a081771d477f3263adaa74f80cd336300b1d8c66e94012e97d47daf2638`. Later polish commits `5f1e2b5 fix: polish Alpha BPR HMI audit leftovers` and `5a3a287 docs: add Alpha BPR polish r2 evidence` closed H5/H13/D4/H6, wording, and dosage-cell findings; new evidence tarball `alpha-bpr-public-audit-r2-20260724093630.tar.gz` was sent to the topic, SHA-256 `517d2db624155669248e4758cae2f258c2655cf01bdffbf6a0f9c77e03eb456b`; public monitor PASS at `2026-07-24T12:35:46+03:00`. Unrelated uncommitted Alpha BPR files remain outside the commits.
- **Спецтех site/SEO:** topic `HOME:990` completed the GSC URL work and cancelled the temporary follow-up cron. Later, mobile and service-URL fixes were deployed to `specialtechnology.ru`: removed mobile horizontal scroll in all 25 `blog/*.html`, increased small mobile text in `calculator.html`, added 301 from service URL with `check=` to clean `https://specialtechnology.ru/calculator.html`, and uploaded 27 files to production. Public verification passed at 390px viewport (`scrollWidth=390`, overflow `0`) for problematic blog URLs and `calculator.html`; service URL now returns `301`. Remaining: verify accepted indexing requests, continue tomorrow only if GSC daily limit appears again, do not touch `/lk/`, optionally remove red erroneous sitemap rows, and pull fresh GSC indexing/effectiveness reports in 7-14 days.

### Cross-Session Snapshot — 2026-07-25 07:31 MSK
- **Alpha BPR HMI / ontology-lite:** topic `HOME:14` had an interrupted/killed session while working around ontology checks in the HMI/BFF demo (`scripts/demo/hmi_bff_demo_server.py` and HMI prototype references were being inspected). Treat this as not completed and not committed until `/home/stanislav/projects/alpha-bpr` is inspected directly.
- **TRIZ knowledge base:** topic `HOME:1110` saved Petrov's `Основы ТРИЗ` into `/home/stanislav/.openclaw/workspace/data/knowledge_base/topics/triz/`, including raw source, summary, rules, FAQ, processed notes, final operating note, and KB index link. Working rule: use TRIZ as anti-brainstorm discipline through system/function/harmful effect, contradiction, IFR, resources, tool choice, risks, and cheap experiment.
- **Agent workflow / Shared Memory:** Phase 6.1 skill wording cleanup was accepted and recorded as `D-2026-07-24-07`; live `agent-workflow-v2` is current. No DB, runtime/MCP, import, promotion, or source-of-truth migration change occurred.
- **Спецтех site:** topic `HOME:990` fixed and deployed `wertsim.html` contact CTAs on `specialtechnology.ru`: `Связаться`, `Запросить демо`, and top `Консультация` now point to `https://specialtechnology.ru/#contact`. Public Chromium smoke confirmed clicking `Связаться` navigates to the contact anchor.
- **Ops:** Codex capacity remains degraded: active `openai:stasiintegraleus@gmail.com` around 12% 5-hour remaining and `openai:integraleus55@gmail.com` blocked; no active session is over 80% after main compaction. Telegram deep status is OK. Garden SSH timeout to `31.128.32.68:22` persists as the same active incident.

### OpenClaw Runtime State / Queue — 2026-07-25
- **Redis direction:** accepted as a docs-only architecture track in `D-2026-07-25-01`. Redis is temporary runtime state, not agent memory and not source of truth.
- **Artifacts:** `docs/ops/openclaw-runtime-state-queue.md` and `state/tasks/openclaw-runtime-state-queue/TODO.md`.
- **Current boundary:** Redis is not installed, no code was changed, and Gateway was not changed or restarted.
- **Next gate:** first spike should be heartbeat alert suppression. Later candidates are Telegram inbound dedupe and active run/task locks.

### Cross-Session Snapshot — 2026-08-09 07:33 MSK
- **Alpha-HMI-DEV:** reference-pattern catalog increment is implemented but not committed: 3585/3585 `.omobj` analyzed, 104 duplicate groups, 143 name conflicts, 146 UUID conflicts, 448 unresolved base-type dependencies, 658 quarantined objects, and zero automatic promotions into the canonical registry. Focused checks passed 29/29 and the report is deterministic.
- **Alpha Presale:** the approved existing-project migration intake decision was recorded in project `DECISIONS.md` and `STATE.md` and committed as `e123176 Record approved migration intake decision`.
- **Alpha BPR / memory search:** OpenClaw memory index was refreshed and verified clean: 573 files, 6093 chunks, Ollama `nomic-embed-text`, 768 dimensions, semantic search working; no gateway restart required.
- **Home printer:** Windows network printing through the Home/Synology IPP chain should use Microsoft IPP Class Driver. The Pantum PCL6 driver breaks that network queue and is reserved for temporary direct USB calibration.
- **Sites / Google:** Google Search Console still needs manual sitemap resubmission and URL-indexing requests for both sites; browser access is required.

### Cross-Session Snapshot — 2026-06-24 07:31 MSK
- **Alpha BPR / Home WebViewer stand:** topic `HOME:14` reported commit `d81dda8 Keep Home Postgres running after Docker restart`. After Docker restart at `2026-06-23 21:57`, `alpha-bpr-postgres` stayed down and caused real workflow HTTP 500 on `POST /api/demo/create-order` while `/healthz`/`/readyz` still returned 200. Fix: started `alpha-bpr-postgres`, waited for `healthy`, set runtime policy and compose `restart: unless-stopped`, recorded decision/memory, and reran full `hmi-bff-webviewer-stand-preflight.sh` with workflow smoke successfully. Current reported state: API active, HMI/BFF active, nginx active, Postgres running/healthy, `https://192.168.68.125/alpha-bpr-hmi/readyz` ready with `bpr.status=reachable`.
- **Alpha BPR / forwarded audit smoke:** later topic `HOME:14` reported new uncommitted increment `scripts/demo/hmi-bff-forwarded-audit-smoke.sh` plus docs/TODO/memory updates. It runs HMI/BFF workflow, reads `/api/audit`, and checks forwarded operator identity (`subject`, `role`, `workstation`, `POST`, `succeeded=true`). Verified: `bash -n`, run-from-other-directory guard without key, and `dotnet test AlphaBpr.sln --filter FullyQualifiedName~BprApiAuditTests` 8/8 OK. Final stand evidence not captured because `BPR_AUDIT_API_KEY` with `audit:read` was not explicitly provided/read; no commit made.
- **Codex quota status:** `openai:integraleus55@gmail.com` hit weekly `0%` and became blocked overnight. Active order moved to `openai:stasiintegraleus@gmail.com`, currently about `13%` weekly remaining and below healthy threshold. Claude auth OK and idle; Telegram/gateway OK.

### Cross-Session Snapshot — 2026-06-23 07:31 MSK
- **Alpha BPR:** topic `HOME:14` latest reported commit `6ee8acc Capture Home HMI BFF live WebViewer evidence`; Home route `https://192.168.68.125/alpha-bpr-hmi/` works through nginx HTTPS -> HMI/BFF `127.0.0.1:5095` -> Alpha BPR API `127.0.0.1:5088`. Health/ready checks and HMI/BFF flow passed; evidence screenshot and `REPORT.md`/`REVIEW.md`/`TODO.md` captured. Remaining caveats: WebViewer-facing route, not native Alpha.HMI screen; operator audit attribution not proven; self-signed cert; evidence not one atomic run.
- **Alpha Presale:** topic `HOME:85` latest reported commit `948f61c Cover pilot review flow replay`; added regression coverage for `iolist_declared_mismatch`, reviewer acceptance to `ready_for_calc`, no premature handoff, `draft_only` when current input differs from accepted input, blocked verdict authority, and reviewer-accepted `work_packages.*`. Full test suite and `scripts/verify.sh` passed; public deploy untouched.
- **Alpha-HMI-DEV:** topic `HOME:30` latest reported commits `baa6638`, `f783901`, `0a0dad0`, `5ea2dc1`; cleaned tracked `__pycache__`/`.pyc`, committed docs/policy inputs, ignored `backups/`, and recorded knowledge-base transfer/classification. Remaining tree is mostly `out/**`, plus generated reports, v2 visual generator change, video evidence helper, and `u-pipe` task artifact.

### Alpha BPR
- **Код:** `/home/stanislav/projects/alpha-bpr`
- **Home production-pilot closeout:** закрыт до человеческих/внешних границ коммитом `d479a68 Close Alpha BPR production pilot` после backup/restore drill, restart/reboot soak, реального host reboot gate, post-reboot readiness, HMI/BFF, Alpha.Reports, PS01/FILL Historian freshness. Оставшиеся границы: production sign-off, TLS/domain/CA/browser trust, будущие secrets/licenses, go-to-market/show/sell approval.
- **Home production-pilot release/show package:** baseline `d479a68` локально tagged as `home-production-pilot-2026-06-30`; docs-only package committed as `88ae13c Add Alpha BPR production pilot show package`. Пакет включает release handoff, show route, pre-show checks, boundaries и production-readiness backlog; Alpha BPR repo clean после commit.
- **Production-readiness docs pack:** committed as `423b12c Add Alpha BPR production readiness pack`; включает readiness checklist, monitoring/backup plan, TLS/sign-off decision sheet и standalone HTML diagrams/charts с architecture, readiness flow, backlog/backup cadence. Alpha BPR repo clean после commit.
- **Offline demo distribution:** built 2026-07-03 in `/home/stanislav/projects/alpha-bpr/dist/` as `alpha-bpr-offline-20260703-demo.tar.gz`, `.run`, `.ps1`, and unpacked folder. Smoke verified API `/health`, HMI/BFF `/readyz`, and workflow. No Windows `.exe` yet because available SFX module was Linux ELF; no commit was made for this distribution run.
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
- **Роль:** контентный и SEO-сайт (`D-2026-08-13-02`); полные статьи не дублировать на втором домене.
- **Деплой:** `curl -X POST "https://specialtechnology.ru/deploy.php?key=spt2026deploy&file=FILENAME" --data-binary @file`
- **Статус:** активен, 36+ страниц, 20 статей блога
- **SEO:** GSC + Яндекс.Вебмастер подключены, sitemap 39 URL
- **Последний деплой:** 2026-04-03 (перелинковка 79 ссылок)
- **TODO:** alt-тексты, PageSpeed, Product-микроразметка, Яндекс.Бизнес

### special-tech.ru
- **Canonical origin:** `https://www.special-tech.ru` (`D-2026-08-13-01`).
- **Роль:** коммерческий сайт для расчётов, консультаций и заявок (`D-2026-08-13-02`).
- **Redirects:** HTTP and non-www variants return permanent `301` redirects to the canonical origin with path/query preservation; production verified 2026-08-13.
- **Yandex Metrika:** dedicated active counter `110922935`.
- **Yandex Webmaster:** HTTPS www and non-www hosts are verified; www is the main mirror.
- **Cross-site analytics:** UTM campaign `cross_site_navigation`; goals `content_site_click` (`110922935`) and `commercial_site_click` (`107569860`).
- **Yandex Webmaster:** Metrika is linked and counter-based crawling is enabled. Yandex Business still requires organization selection/creation and owner confirmation by phone code.
- **Task evidence:** `state/tasks/2026-08-13-special-tech-yandex/TODO.md`.

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
## Local Alpha Reference Corpus — 2026-08-08

- Production example sets `12105`, `14443`, and `20167` are stored locally
  under `state/tasks/2026-08-08-shared-alpha-project-examples/`.
- Canonical analysis report:
  `state/tasks/2026-08-08-shared-alpha-project-examples/REPORT.md`.
- These files are static reference inputs, not confirmed import/compile/runtime
  evidence.
- Routed guidance exists in Alpha-HMI-DEV, Alpha-BPR, and Alpha-Presale; reuse
  the guidance selectively and keep raw installation-specific settings out of
  product repositories.

## Alpha NS1 native runtime — 2026-08-10

- Current gate: native Alpha.DevStudio compile/rebuild and direct runtime/OPC UA Start, Stop, LOCAL, FAULT, and NOT_READY scenarios are proven.
- Open acceptance item: Alpha.HMI reads/render live values, but TCPServer rejects button writes because the HMI client lacks write permission. Full HMI end-to-end remains unproven until ACL is corrected and command-to-feedback readback is repeated from the HMI buttons.
- Working PS01 stand was restored and checked by original configuration hashes, active services, expected ports, and stable exchange over the 95 nodes present in runtime; the source CSV currently lists 122 tags.
- Reusable execution rule is recorded as `D-2026-08-10-01`.
- Task pointer: `state/tasks/alpha-ns1/TODO.md`.

## Codex-Claude deterministic orchestration — 2026-08-11

- Approved architecture is recorded as `D-2026-08-11-01`.
- Reviewer contract and deterministic acceptance-state-machine slices are implemented and independently closed: final targeted/full Claude reviews passed, 84/84 tests and schema/fixture gates passed, and the mechanical policy run returned `ACCEPTED / R17_ACCEPT`.
- The state-machine task packet is `COMPLETED`. The local integration runner is also closed and committed as `9f00f70 feat(orchestrator): add local integration runner`; targeted Claude closure, 14/14 integration tests, 84/84 core regression tests, py_compile, and whitespace checks passed.
- `59d42a3` is the accepted local production-CLI baseline under `D-2026-08-12-02`; it includes the bounded managed cycle, fixed local agent launches, deterministic admission, fail-closed CLI validation, and a successful isolated canary ending `ACCEPTED / R17_ACCEPT` in one attempt. Verification: 58/58 integration tests, 84/84 core tests, py_compile/whitespace, and `PRODUCTION_CLI_CLOSURE_PASS`.
- `7fa0a0b` is the accepted trusted-input builder increment under `D-2026-08-13-03`. It derives and seals review inputs from observed Git/gate state, preserves authenticated findings across rework, and limits implementation to two Codex attempts plus one policy-triggered review-only final-full leg. Clean canary r17 ended `ACCEPTED / R17_ACCEPT`; verification passed 83/83 integration tests, 84/84 core tests, `py_compile`, and whitespace checks.
- `bb14bbc` and `a5a7e55` close the reviewer decoded-control-character transport edge under `D-2026-08-15-01`; `48c85c3` closes the follow-on evidence-reference discipline under `D-2026-08-15-02`. Dangling evidence IDs and unverified artifact digests remain fail-closed, while reviewer instructions now bind references to the supplied manifest on initial review and bounded retries. Initial transport-invalid verdicts receive a structured validator report through the existing bounded repair path without validator weakening. Real-project smoke r8 passed strict transport/schema/semantic validation with zero errors and ended terminal `ACCEPTED / R17_ACCEPT`; the final-full leg was review-only, without a third Codex implementation attempt. Source `/home/stanislav/projects/home-agent-factory` remains clean; smoke changes remain confined to detached worktrees.
- Release checkpoint `b300207` / tag `orchestrator-local-cli-r1-2026-08-15` is accepted under `D-2026-08-15-03`; post-release verification is recorded in `c35644b` and `state/tasks/2026-08-15-orchestrator-release-readiness/`. Current status is `READY FOR CONTROLLED MANUAL PILOT; NOT ACTIVATED`. The readiness packet enforces repository deny-by-default admission, explicit task packets, bounded attempts/timeouts, foreground kill/stop handling, retained digest-bound evidence, and fail-closed stop conditions. The AES-256 Synology bundle for `b300207` passed external/internal SHA-256, decryption, `git bundle verify`, complete-history/ref inspection, and exact commit verification. Gateway, cron, daemon/systemd, unattended execution, automatic commit/push/deploy, and source `home-agent-factory` changes remain unapproved.
- Controlled manual pilot is complete under `D-2026-08-15-04` with status `RETURN FOR REWORK; NOT ACTIVATED`. T01/T03/T04 reached `R17_ACCEPT`; T02 correctly escalated at `R12_FINDINGS_EXHAUSTED`; 86/86 integration tests passed and the clean source remained at `3d9c27e`. Blocking defects are lossy prior-finding carry-forward evidence and missing structured `INTERRUPTED` evidence on `Ctrl-C`. Next gate: fix both locally, add regression coverage, and repeat only T02 re-verification plus the live interruption drill. OpenClaw/Gateway/cron/systemd/daemon/unattended integration remains forbidden without a later explicit readiness decision. Evidence: `state/tasks/2026-08-15-orchestrator-manual-pilot/`.
- Pilot rework is complete under `D-2026-08-15-05` at local commit `9d43129`; current status is `READY FOR CONTROLLED MANUAL USE; NOT ACTIVATED`. Complete sealed prior-finding details now survive targeted re-verification, and operator interruption during both Codex and Claude legs produces terminal `INTERRUPTED`/130 evidence without continuation or orphan processes. Fresh T02 reached `R17_ACCEPT`; targeted replay carried all three original findings; 94/94 integration tests and 87/87 core contract tests passed; final independent review returned `ACCEPT`. Use remains foreground, manual, bounded, packet-driven, and supervised. OpenClaw integration, Gateway/runtime/config changes, cron, systemd/daemon, unattended execution, automatic commit, push, deploy, and source transfer remain unapproved. Evidence: `state/tasks/2026-08-15-orchestrator-pilot-rework/`.
- The separately approved `manual-004` transfer is complete under `D-2026-08-16-01`: local `home-agent-factory` commit `6e56761` contains exactly the accepted external-read schema, runtime policy, and tests. All three source files matched the accepted worktree byte-for-byte; repeated verification passed 12/12 tests and `git diff --check`, and the target repository was clean after commit. This is a one-task source-transfer approval only. The orchestrator remains `READY FOR CONTROLLED MANUAL USE; NOT ACTIVATED`; push, deploy, OpenClaw/Gateway integration, cron, systemd/daemon, unattended execution, and automatic future transfers remain unapproved. Evidence: `state/tasks/2026-08-15-orchestrator-manual-release-r2/manual-004/`.
- `manual-005` is closed under `D-2026-08-16-02` as `ESCALATED`; transfer is prohibited. One bounded Codex implementation changed only the model-class policy and tests; managed and repeated checks passed 18/18 tests and `git diff --check`. Claude reported no blocker or major and stated AC-1 through AC-5 were satisfied, but its bounded repaired verdict remained contract-invalid because `command_output` evidence lacked the required `command` block. The orchestrator stopped fail-closed with exit 4, launched no second implementation, left no orphan process, and kept source `home-agent-factory` clean at `6e56761`. A fresh bounded task is required for model-class/schema closure. Evidence: `state/tasks/2026-08-16-orchestrator-manual-005/` and commit `3932bf0`.
- `manual-006` is accepted and transferred under `D-2026-08-16-03`: local `home-agent-factory` commit `f25e001` contains exactly the accepted model-class schema, runtime policy, and tests. The managed cycle ended `R17_ACCEPT` after one Codex implementation plus review-only final-full; final review recorded 0 blocker, 0 major, and 4 nits. All three transferred files matched the accepted worktree byte-for-byte; repeated source checks passed 24/24 tests and `git diff --check`, and the target repository was clean after commit. Runtime and Schema now share one pinned `local`/`cloud` contract. This is a one-task transfer approval only; push, deploy, OpenClaw/Gateway integration, cron, systemd/daemon, unattended execution, and automatic future transfers remain unapproved. Evidence: `state/tasks/2026-08-16-orchestrator-manual-006/`, source commit `f25e001`, and evidence commit `d42f66d`.
- `manual-007` was accepted under `D-2026-08-16-04` and later transferred through a separate controlled step to local `home-agent-factory` commit `8985b8e`. The three source files matched the accepted worktree byte-for-byte; repeated verification passed 33/33 tests and staged `git diff --check`, including the new test file. Evidence: `state/tasks/2026-08-16-orchestrator-manual-007-review-retry/`, `state/tasks/2026-08-16-orchestrator-manual-007-transfer/`, acceptance commit `07997ea`, and transfer evidence commit `79ab132`.
- Extended controlled manual-use assessment is closed under `D-2026-08-16-05`: five of nine tasks reached `R17_ACCEPT`, four stopped fail-closed, and the status is `READY FOR A SEPARATELY APPROVED CONTROLLED MANUAL OPENCLAW PILOT; NOT ACTIVATED; NOT READY FOR UNATTENDED USE`. Manual-008 is accepted with 44/44 tests but remains untransferred; manual-009 is escalated and transfer-prohibited after a real major runtime/schema mismatch plus invalid bounded reviewer repair. Safety is strong, while reviewer reliability and operator efficiency remain limited. Any OpenClaw runtime/config/Gateway integration is still a separate approval gate and must remain foreground, one-task-at-a-time, with no automatic transfer/commit/push/deploy or background continuation. Evidence: `state/tasks/2026-08-16-orchestrator-manual-use-assessment/` and commit `057c812`.
- Under `D-2026-08-17-01`, the local administrator and current OpenClaw are trusted for controlled manual use because Stanislav is the only person with access and the host is local to the home network. The uninstalled OS guard/plugin is frozen as a research prototype; Gateway and systemd remain unchanged. `manual-pilot-001` was launched from Telegram as one foreground proof-chain task and stopped fail-closed as `ESCALATED`: exactly three allowed files, 46/46 tests and `git diff --check` pass, but the repaired Claude verdict was contract-invalid, so transfer is prohibited. Continue only packetized, supervised, one-task manual runs with no automatic commit/transfer/push/deploy; revisit OS isolation before external/multi-user, unattended, or high-impact automation. Evidence: `state/tasks/2026-08-17-orchestrator-manual-pilot-001/`.
- No GitHub/push is used. A verified GPG AES-256 backup for `59d42a3` exists on Synology inside the home network.
- Track F release-audit orchestrator pilot is closed under `D-2026-08-20-01`. R1 exposed missing absolute path binding; R2 exposed nondeterministic shell membership checks under `pipefail`. The corrected closure harness passed 10/10, the frozen three-file audit digest remained `97349e91b94762f384a924555c2022841854b625f4eadbd991744860e8739912`, and independent closure review returned `ACCEPTED` with 0 blocker and 0 major. The audit itself remains `DEFER`; no product transfer, commit, push, deploy, VM, service, Gateway, system, or network change was authorized. Future sealed runs require repeated deterministic harness preflight and absolute path binding. Evidence: `state/tasks/2026-08-20-alpha-bpr-track-f-release-audit-closure/`.
- Under `D-2026-08-21-01`, the orchestrator .NET profile requires a Trusted Test Broker execution adapter, typed gate failures, deterministic project/fixture execution-context paths, and at most one authenticated builder-repair attempt inside the existing sealed-cycle budget. The broker is not an OS security boundary: under the trusted local-administrator threat model it runs only operator-sealed commands, which may execute agent-authored tests. Agent-writable external artifacts are cleared before trusted gates and blind acceptance, and gate processes receive a scrubbed minimal environment. Infrastructure, safety, scope, test-count, and ignored-state failures remain fail-closed. Runtime nondeterminism detection remains a PREPARE-time repeated-run requirement. No Alpha BPR product run, transfer, commit, push, deploy, Gateway/runtime activation, or unattended use was authorized. Evidence: `state/tasks/2026-08-21-orchestrator-test-broker-repair/`.
- The encrypted Synology backup for `7fa0a0b` was created after explicit approval and verified by external SHA-256, decryption, relative internal SHA-256, `git bundle verify`, and exact `refs/heads/main` commit match. Runtime/config changes, unattended activation, cron, deploy, and automatic commit/push remain separate approval gates.
## Alpha BPR TRIZ P3 — 2026-08-22

- Current verified local baseline: `061fcc8 feat: add P3 recipe approval proof summary`.
- TRIZ P3 is closed: the recipe approval screen exposes lifecycle, audit, ontology, diff, report readiness, and mode/source in one reviewer proof-summary, protected by fail-closed UI/BFF guards.
- Acceptance evidence: P3 27/27, full suite 367/367, build 0 errors / 0 warnings, Chromium smoke PASS, independent review PASS with 0 blocker / 0 major.
- Push and deploy were not performed.
- Next stage: Track E read-first plan/fact and deviation lane.

## Alpha BPR read-only Integration Wizard — 2026-08-22

- Roadmap stage 5 is accepted under `D-2026-08-22-02` at local commit `f21247a feat: add read-only integration wizard`.
- The visible path covers connection, bounded OPC UA browse, mapping, compiled validation, compiled gateway dry-run, and one-use exact-profile activation. Only readable Variables are selectable; curated/public remains isolated and NO WRITE / NO METHODS is preserved.
- Final focused gates passed 52/52; Python compilation and `git diff --check` passed; independent final review reported 0 blocker / 0 major after fixes.
- Alpha BPR worktree was clean after commit. Push and deploy were not performed.
- Next vertical: stage 6 browse-assisted generation of Customer Integration Profile drafts with engineer confirmation and mandatory validate/dry-run gates.

## Automatic orchestrator RUN_EVIDENCE — 2026-08-22

- Accepted under `D-2026-08-22-03`; evidence: `state/tasks/2026-08-22-orchestrator-run-evidence/EVIDENCE.md`.
- Admitted production runs automatically write schema `1.0.0` events for start, agent launch, changed paths, gates, review, and terminal outcome.
- The stream is append-only, monotonically sequenced, SHA-256 hash-chained, symlink-safe, and fail-closed on malformed/external modification or post-terminal writes.
- Final verification: focused 57/57, full orchestrator 186/186, `git diff --check` PASS, independent closure review `ACCEPTED` with 0 blocker / 0 major.
- Final evidence commit: `e0b7b9de`. Push/deploy and product-repository changes were not performed.
- Next orchestrator increment: programmatically constrained `review-only`, `safe-fix`, and `sealed-pilot` profiles.

## Alpha BPR Universal Recipe Testbed — 2026-08-23

- Accepted under `D-2026-08-23-01` as a separate project at `/home/stanislav/projects/alpha-bpr-universal-testbed`.
- First demonstration process: universal reactor/mixer with dosing, heating, holding, and discharge.
- Bootstrap contains configurable signal and recipe schemas, one 13-signal reactor catalog, three distinct recipes, and a generator for native Alpha.Server and Alpha.Imitator projects.
- Model and generated-source checks pass; both native units compile and rebuild successfully in Alpha.DevStudio.
- No live deployment, service restart, license/system change, or real PLC write has been performed. These remain separate explicit approval gates.
- Next implementation slice: native Alpha.HMI tracer screen and local `HMI -> command -> Alpha.Imitator -> readback` proof.
## Spectech WordPress MVP — 2026-08-24

- Release preparation was accepted under `D-2026-08-24-01` at local `spectech-sites` commit `7b6cc55`.
- The first production release is accepted under `D-2026-08-24-02`; production evidence and pinned curl/FTPS pipeline are committed as `5446b59`.
- First vertical material: «Чек-лист исходных данных для обследования и модернизации SCADA».
- Both site indexes and sitemaps are prepared; seven-file release manifest and guarded backup/deploy/smoke/rollback pipeline are ready.
- Verification passed: contract tests 2/2, release validation 0 failures, Astro build 18 pages, clean repository.
- Exactly seven manifest files were published after backup; FTPS SHA-256 matched 7/7 and all target/control checks passed HTTP 200. Rollback was not required.
- `/lk/**`, forms, PHP/MySQL, uploads, DNS and Synology were not changed.
- Next stage: operate the workflow with a second material or separately design hosted CMS/preview infrastructure.

## Alpha BPR Universal Recipe Testbed Phase 3 — 2026-08-24

- Accepted under `D-2026-08-24-03` as a compile-only baseline; project source remains `/home/stanislav/projects/alpha-bpr-universal-testbed`.
- Alpha.Server and Alpha.Imitator now generate 21 configurable signals with fail-closed command validation, correlation IDs, batch identity, TTL metadata, duplicate protection, explicit ACK/reject/completed/reset states and running readback.
- Native Alpha.HMI exposes separate START/RESET controls and visible ACK, rejection reason, READY, interlock, readback and compile-only quality state.
- Four focused checks, Alpha.DevStudio compile/rebuild, Alpha.HMI compile/BINOM export, 1440x900 Viewer render and `git diff --check` passed.
- No deployment, service restart, license/system mutation, PLC connection or live write occurred.
- Next gate: dynamic per-request ID generation and actual local `HMI -> Alpha.Server -> Alpha.Imitator -> readback` proof, only after explicit deploy approval.

## Spectech WordPress MVP second vertical — 2026-08-25

- Accepted under `D-2026-08-25-01` at local `spectech-sites` commit `174ec8a`.
- Material: «Типовые ошибки при составлении ТЗ на SCADA».
- Two `noindex` previews, a PNG infographic, and a two-page PDF checklist were created; the generator supports multiple materials.
- Verification passed 3/3 tests, Astro build with 19 pages, and 6/6 local HTTP checks; the repository was clean.
- Production and Reg.ru were not changed. Publication remains a separate explicit approval gate.
- Release preparation is accepted under `D-2026-08-25-03` at commit `24648b2`: both indexes/sitemaps are wired, pages are `index, follow`, and the guarded manifest contains 11 files including PNG/PDF assets for both sites.
- Verification passed 5/5 tests, release validation, Astro build of 19 pages, manifest check 11/11, local HTTP smoke 6/6, and `git diff --check`; production backup/publication remains a separate explicit gate.
- Production release is accepted under `D-2026-08-25-04`: source commit `24648b2`, evidence commit `892ccb1`, backup complete, exactly 11 files published, FTPS SHA-256 11/11, and all target/control checks passed. Rollback was not required.
- REG.RU CMS/preview architecture is accepted under `D-2026-08-25-05` at audit commit `222290e`: isolate WordPress at proposed `cms.specialtechnology.ru`, reuse `test.special-tech.ru` as authenticated/noindex static preview, and keep both public sites static behind the guarded manifest release path.
- Deployment remains blocked pending panel-owner confirmation of free site/database/disk/cron capacity, PHP 8.3 and Let's Encrypt. No hosting, DNS or production mutation was authorized by the architecture decision.

## Alpha BPR Universal Recipe Testbed native transport — 2026-08-25

- Accepted under `D-2026-08-25-02` as a compile/rebuild baseline; project source is `/home/stanislav/projects/alpha-bpr-universal-testbed`.
- One typed `BPR_Process` is hosted by Alpha.Imitator; Alpha.Server exposes `BPR_ServerView` through 21 directed bindings and its native OPC UA client link to `Alpha.Imitator.UaServer`.
- Command execution exists only in Alpha.Imitator; Alpha.HMI addresses the Alpha.Server representation at `Application.ReactorMixer`.
- Four focused validators, native runtime compile/rebuild `0.1.0.d6`, Alpha.HMI compile/BINOM export, and `git diff --check` passed.
- Live deploy remains open: DevStudio has no Alpha.Domain central-node connection. No runtime service or tag was changed, and the transport increment is not yet committed.

## Alpha BPR Universal Recipe Testbed online runtime correction — 2026-08-25

- Accepted under `D-2026-08-25-06` after an isolated local runtime probe.
- Native Alpha.Link was proven live between Alpha.Server HUB and Alpha.Imitator TCP Server, but Alpha.Imitator returned `BadWaitingForInitialData` outside a configured history simulation session.
- The live command architecture now uses a second isolated Alpha.Server as the online process simulator; the HMI-facing Alpha.Server remains the only HMI endpoint.
- Alpha.Imitator is retained for history replay/recalculation scenarios, not the always-online command handshake.
- Production, PLC, customer systems and pre-existing Alpha services remain outside the test scope.

## Alpha BPR Universal Recipe Testbed Phase 4 — 2026-08-25

- Accepted under `D-2026-08-25-07` at local testbed commit `8a32d3a feat: execute data-driven recipe batches`.
- One compiled two-Alpha.Server runtime executes all three canonical recipes from data through native Alpha.Link without rebuilds between recipes.
- Pause/resume, operator approval, abort/reset, audit sequencing, invalid recipe/version/operation/parameter handling, and the complete Phase 3 regression matrix pass.
- Real Alpha.HMI Viewer START/RESET clicks and independent OPC UA readback pass; the complete proof is repeatable with `./scripts/run_live_gate.sh`.
- Isolated runtimes are stopped after verification; `alpha.server`, `alpha.imitator`, and `alpha.domain` remain active. Push, PLC, customer, and production changes were not performed.
- Next stage: Phase 5 native Alpha.HMI hierarchy and rendered-screen verification.

## Alpha BPR Universal Recipe Testbed Phase 5 — 2026-08-25

- Accepted under `D-2026-08-25-08` at local testbed commit `9da2c84 feat: add native hmi screen hierarchy`.
- Native Alpha.HMI now has four real Viewer-navigable levels: L1 overview, L2 control, L3 detail and L4 diagnostics.
- L1 has no process commands; L2 START/RESET retains independent OPC UA readback through the two-Alpha.Server native Alpha.Link runtime.
- The complete `./scripts/run_live_gate.sh` proof passes generation, validators, native compile/rebuild, BINOM export, three recipes, negative scenarios, Viewer navigation/clicks and rollback.
- Screenshot review at 1280x900 passed after correcting right-edge clipping. Isolated runtimes are stopped, test ports are closed, and standard Alpha services remain active.
- Phase 6 remains open for actual Alpha.HMI.Alarms, alpha.hmi.charts/Alpha.Historian, Alpha.Security and Alpha.Reports integration. Push, PLC, customer and production systems remain untouched.
