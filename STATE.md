# STATE.md — Текущее состояние проектов и серверов

_Обновляется из любой сессии после значимых действий. Main session читает при старте._

## Текущий рабочий режим

- **Подтверждение:** явный запрос Станислава считается подтверждением только на указанную область; расширение объёма, внешние действия, конфиги, зависимости, БД, API/auth/security, бизнес-логика, destructive/root-level изменения требуют отдельного подтверждения.
- **Критические изменения:** маленькие атомарные патчи, предварительное описание действия/риска, `git diff`, релевантные тесты/линтеры/type checks при наличии, фактический статус по файлам/проверкам/git/commit.
- **Deliverable:** сначала артефакт/checklist на диске, затем рассуждения; готовность подтверждать реальной проверкой. Для PPTX/визуальных файлов не считать достаточными только `unzip`/XML-проверки.
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
- **Спецтех site/SEO:** topic `HOME:990` reported that 4 updated blog post URLs plus sitemap were sent to Yandex Webmaster recrawl; Yandex accepted 5 URLs, remaining quota 466. Later same-topic context showed `/sitemap.xml` accepted successfully with 41 pages found; GSC manual indexing limit is exhausted for 2026-07-23, and a one-shot cron reminder is set for 2026-07-24 10:00 MSK to continue with `specialtechnology.ru/dpp-dobycha.html` and `www.special-tech.ru` priority pages (`/alpha-platform/`, `/podbor-scada/`, `/raschet-licenziy-alpha-platform/`, `/raschet-licenziy-scada/`, `/news/`). Evidence report: `/home/stanislav/projects/spectech-sites/artifacts/yandex-webmaster-recrawl-blog-seo-20260722T2146.md`.
- **Alpha BPR HMI catalogs:** topic `HOME:14` reported commit `da10f13 feat: add postgres-backed hmi catalogs`; later the same session was interrupted by context/timeout, so future Alpha BPR work should start from a fresh context and verify current repo state first.
- **Agent workflow / Shared Memory:** topic `HOME:1` pushed `5e9a434 docs: add unified agent workflow shared memory plan` and `6c1dddb docs: address unified plan claude review`. Topic `HOME:1751` completed Phase 1.5 and committed `4bee741 docs: complete shared memory phase 1.5 workflow pilot`: project-specific Agent Workflow artifacts, Phase 2 task/security/audit/evidence packet, sample Memory Candidate, explicit backup LOGIN `BYPASSRLS` runbook step, typed negative-test assertions, and automated local pilot runner. Phase 2 prep package was then committed as `c5dbe0d docs: prepare shared memory synology deploy package`, adding reproducible Synology package/archive/checksum, rollback, evidence, and draft Phase 3 approval request. Synology migration remains Phase 3 and requires explicit approval; no Synology/runtime/real-memory/external-review action was performed.

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
