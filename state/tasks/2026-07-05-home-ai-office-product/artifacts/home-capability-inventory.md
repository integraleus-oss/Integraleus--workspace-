# Home/OpenClaw Capability Inventory

Checked: 2026-07-05

## Current Home Surface

Observed via `openclaw --help`, `openclaw status --deep`, workspace tools, and active skills.

### Runtime and Control Plane

- Gateway running locally on `ws://127.0.0.1:18789`, dashboard on `http://127.0.0.1:18789/`.
- Systemd user gateway service installed, enabled, running.
- Telegram channel enabled and OK.
- Default agent model: `openai/gpt-5.5` with fallback `ollama/phi3:instruct`.
- Memory plugin enabled.
- Cron/background tasks available.
- Sessions/transcripts available.
- Local CLI exposes commands for agents, channels, cron, gateway, memory, message, models, nodes, plugins, skills, tasks, transcripts, dashboard, security.

### Agent Building Blocks

- `skills/`: reusable task instructions and workflows.
- `skill_workshop`: proposal/apply lifecycle for durable skills.
- `cron`: scheduled background jobs and alerts.
- `message`: send/read/manage channel messages.
- `sessions`: active conversation/session state.
- `subagents` / Codex subagents: sidecar agent work and review.
- Local Claude CLI wrappers for review/ideation.
- `memory_search` / `memory_get`: durable memory lookup.
- `nodes` / `canvas`: paired node surfaces and hosted HTML experiences.
- Local filesystem and shell for internal automation.
- OpenClaw taskflow skills for durable multi-step work.

### Existing Skills Useful for MVP

Home-local:

- `sales-docs-pipeline`
- `proposal-writer`
- `contract-review`
- `process-documentation`
- `sop-writer`
- `compliance-checklist`
- `presentation-designer`
- `product-calculator`

System/OpenClaw:

- `canvas`
- `github`
- `gh-issues`
- `taskflow`
- `tmux`
- `weather`
- `diagram-maker`
- `meme-maker`
- `node-connect`
- `notion`
- `discord`

Also visible in system skills:

- Google/Gmail/Calendar/Drive-style skill (`gog`) is present in `/usr/lib/node_modules/openclaw/skills`, but auth/status must be checked before productizing it.
- WhatsApp helper skill (`wacli`) exists, but outbound messaging requires explicit confirmation.
- Apple reminders, voice call, 1Password and other skills exist as optional integrations.

### Strengths Versus Aizor

- More control over runtime, files, SSH, local services, and private network.
- Can work with Synology and local infrastructure without sending raw data outside the home network, subject to the explicit Synology privacy rule.
- Can mix Codex, Claude, OpenAI, OpenRouter, Ollama and local scripts.
- Has durable memory, transcripts, taskflow, cron, and channel routing already.
- Strong for owner-operated private automation and technical workflows.

### Gaps Versus Aizor

- No polished non-technical catalogue of roles.
- No single "create agent" wizard that compiles role + integrations + permissions + schedule.
- Skills are currently developer-facing Markdown, not marketplace cards.
- No first-class install/update/version UI for role packages.
- Permission model exists operationally, but not as product UX per role.
- Logs/transcripts exist, but no simplified run history for non-technical review.
- Integrations are uneven: many are possible through CLI/scripts, but not packaged as clean connectors.
- No billing/quotas needed for private Home MVP, but role-level budgets and limits would still be useful.

### Security Baseline Issues to Address Before Exposing Beyond Stanislav

Current `openclaw status --deep` warns:

- `tools.fs.workspaceOnly=false`.
- exec security is full for `main` and `home-monitor`.
- state dir `/home/stanislav/.openclaw` is group-writable.
- shared/group chat context creates multi-user trust-boundary concerns.
- reverse proxy headers are not trusted if Control UI is exposed later.

For a private Home prototype, this is manageable. For anything resembling a product used by other people, it must be split into a dedicated low-privilege agent/runtime with strict workspace-only filesystem, connector scopes, and explicit approvals.

## Product Implication

Home already has the hard primitives. The missing layer is a product shell:

- Role catalogue.
- Agent package schema.
- Wizard.
- Permissions and approvals.
- Run log.
- Integration health.
- Schedule/background control.
- Review/publish flow for new role packages.
