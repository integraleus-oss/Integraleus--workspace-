# Product Plan: Home AI Office

Date: 2026-07-05
Status: Draft for review

Review status:

- Codex sidecar: agrees with private MVP direction.
- Claude local review: `pass_with_notes`; required corrections integrated below.

## One-Line Product

Home AI Office is a private, owner-controlled agent factory on the Home server: a catalogue of ready business roles, a simple setup wizard, scheduled/background execution, explicit approvals, and full run history over OpenClaw primitives.

## Product Thesis

Aizor's strongest idea is not "another chatbot". It is the packaging of AI agents for non-technical users:

- Role catalogue instead of scripts.
- Setup guides instead of DevOps.
- Marketplace cards instead of raw prompts.
- Integrations and actions instead of chat only.
- Token/plan limits instead of API keys.
- Desktop/local context as a familiar mental model.

Home should not copy the public SaaS layer first. Home should build a private "AI back office" that turns OpenClaw's existing capabilities into installable, inspectable, safe work roles.

## Target Users

### Primary

Stanislav / owner-operator:

- wants real tasks completed across Telegram, files, projects, docs, websites, bots, presentations, servers;
- values privacy, control, local data, SSH, Synology, and custom pipelines;
- can tolerate a technical admin screen but needs fast role-level launch.

### Later

Friendly non-technical users:

- need Russian-language business agents;
- do not want VPS/API/model configuration;
- need Telegram-first UX and clear approvals.

## MVP Name

Working name: `Home Agent Factory`

Avoid "Aizor clone" internally. The differentiator is private-by-default local execution.

## MVP Architecture

```text
Telegram / Web UI / Canvas
        |
        v
Agent Catalog + Wizard
        |
        v
Agent Package Registry
        |
        v
Runner / Orchestrator
        |
        v
Policy / Capability Grant Enforcement
        |
        +--> OpenClaw skills
        +--> message tools
        +--> cron
        +--> sessions/subagents
        +--> memory
        +--> local files / approved project folders
        +--> models: Codex, Claude, OpenAI, Ollama
        |
        v
Run Log + Approval Inbox + Evidence
```

## Core Modules

### 1. Agent Catalogue

User-facing list of role packages.

Each card should contain:

- name;
- short business outcome;
- who it is for;
- required inputs;
- required integrations;
- permissions;
- privacy level;
- approval gates;
- example commands;
- setup difficulty;
- last updated;
- version;
- owner/author;
- install status.

MVP storage:

- `agent-packs/*.yaml` for metadata.
- `agent-packs/<slug>/README.md` for setup guide.
- optional `agent-packs/<slug>/prompt.md`.
- optional `agent-packs/<slug>/workflow.md`.

Separate package definition from package instance:

- Package definition: versioned reusable role, safe defaults, declared tools.
- Package instance: this Home server's folder scopes, schedules, channel bindings, granted permissions, and owner-specific settings.
- Package updates must not overwrite local grants or schedules.

### 2. Agent Runner

Thin execution layer that maps a package to an OpenClaw turn/session/task.

Responsibilities:

- validate input;
- load only declared context;
- enforce permissions;
- choose model/profile;
- call tools;
- request approvals;
- write run log;
- return concise result.

MVP implementation options:

- CLI: `home-agent run <slug> --input ...`
- Telegram command: `/agent <slug> ...`

Non-MVP:

- HTTP endpoint `POST /agent-runs`; this adds auth and attack surface before there is a real need.

### 2a. Policy / Capability Grant Enforcement

This is the real MVP spine. Package permissions are not trusted just because they are declared in YAML.

Every run must compile a capability grant before tools execute:

- allowed tools;
- allowed filesystem roots;
- allowed output channels;
- allowed external domains and HTTP methods;
- allowed model classes;
- approval gates;
- maximum runtime/cost;
- whether private data was touched.

The runner must check every tool call against the grant. A prompt or package author cannot expand its own grant at runtime.

Hard gates:

- `private/local-read + cloud model` is denied unless explicitly approved for that run.
- `private/local-read + external-send` is denied unless explicitly approved for that run.
- `private/local-read + group-chat output` is denied by default.
- `external-read` is GET-only and domain allowlisted where practical.
- timeout on approval means deny and log.

### 3. Setup Wizard

Start simple:

- Telegram guided flow or local HTML page.
- Select role.
- Select project folder/data scope.
- Select channels.
- Select schedule.
- Confirm permissions.
- Run first test.

The wizard should generate/update the agent package instance config, not hand-edit core OpenClaw config.

### 4. Permission and Approval Layer

Permission levels:

- `chat-only`: can answer in the current chat only.
- `local-read`: can read explicitly selected folders.
- `local-write`: can create/update files in selected folders.
- `external-read`: can fetch public internet/API data.
- `external-send`: can send messages, email, publish, update CRM/tasks.
- `destructive`: can delete/move/overwrite important data or change system services.

Default:

- read-only for new packages;
- any `external-send` needs approval;
- any Synology raw-file access must obey the existing local privacy rule;
- destructive/system/root changes require explicit approval.

Approval loop:

- paused run is persisted;
- owner receives approve/deny prompt in Telegram first;
- approval records approver, time, exact action, data scope, destination, and expiry;
- default on timeout is deny;
- denied runs still write full evidence.

### 5. Run Log and Evidence

Every run should produce:

- run id;
- package slug/version;
- user/channel;
- input summary;
- data scopes touched;
- tools used;
- model used;
- approvals requested/granted/denied;
- files created/changed;
- external actions;
- result summary;
- errors/blockers.

MVP storage:

- `state/agent-runs/YYYY-MM-DD/<run-id>.json`
- `state/agent-runs/YYYY-MM-DD/<run-id>.md`

Run logs must be append-first: create the run record before reading data, append events as they happen, and write denied/failed runs too. The audit trail is part of the product, not a nice-to-have.

### 6. Scheduler

Use OpenClaw cron first.

Scheduled package examples:

- morning project digest;
- unread/urgent inbox triage;
- daily website/SEO monitor;
- weekly content plan;
- monthly finance/check summary;
- server/security heartbeat.

### 7. Admin Console

MVP can be text/Markdown plus a small local HTML dashboard.

Must show:

- installed agents;
- enabled schedules;
- recent runs;
- pending approvals;
- errors;
- model/token usage;
- risky permissions;
- integration health.

## Agent Pack Backlog

Pick packs that reuse existing Home strengths and demonstrate business value.

MVP ships only 3 packs. The rest are backlog.

### MVP Packs

1. **Private Archive RAG**
   Ask over a selected local folder, with citations and no raw exfiltration. Exercises local-read, model/privacy policy, run logs, and group-chat guard.

2. **Project Status Digest**
   Reads selected project state/TODO/git status and produces a concise status. Exercises local-read over non-Synology project folders and scheduled runs.

3. **Telegram Support Triage**
   Classifies inbound messages and drafts replies. Exercises external-send approval without private local-read.

### Backlog Packs

4. **Voice Task Dispatcher**
   Telegram voice/text -> structured tasks + approval -> task tracker or Markdown TODO.

5. **Meeting/Call to Actions**
   Transcript -> decisions, tasks, risks, follow-up draft.

6. **Proposal Draft Builder**
   Uses existing `sales-docs-pipeline` / `proposal-writer`.

7. **Contract Risk Reviewer**
   Uses `contract-review`; produces risks, obligations, questions.

8. **SOP Generator**
   Uses `sop-writer`; outputs runnable procedure with rollback/checks.

9. **Compliance Checklist**
   Uses `compliance-checklist`; tracks owners/evidence/gaps.

10. **Presentation Builder**
   Uses `presentation-designer`; creates `.pptx` from brief.

11. **SEO Article Assistant**
   Research -> outline -> draft -> publish-ready Markdown, approval before publish.

12. **Website Health Monitor**
    Checks uptime, links, titles/meta, indexation notes, obvious regressions.

13. **Finance Receipt Capture**
    Photo/text receipt -> extracted fields -> local spreadsheet draft.

14. **Code Review Sidecar**
    Runs Codex/Claude review wrappers on diffs and writes findings.

15. **Server Health Sentinel**
    Uses existing healthcheck patterns; status, warnings, safe remediation suggestions.

## Data Model Draft

```yaml
slug: voice-task-dispatcher
name: Voice Task Dispatcher
version: 0.1.0
category: productivity
summary: Turns Telegram voice/text into confirmed tasks.
inputs:
  - telegram_message
  - voice_transcript
outputs:
  - task_draft
  - task_created
integrations:
  required:
    - telegram
  optional:
    - yougile
    - markdown_todo
permissions:
  local_read:
    - scope_id: selected_archive
      path: /home/stanislav/example/archive
  local_write:
    - state/agent-factory/tasks
  external_read:
    domains: []
    methods: []
  external_send:
    - telegram_reply
tool_allowlist:
  - memory_search
  - memory_get
  - local_rag_search
data_scopes:
  private: true
  synology: false
model_policy:
  default: local_or_owner_approved_cloud
  allow_cloud_without_private_data: true
  allow_cloud_with_private_data: approval_required
approval:
  before_external_send: true
  before_cloud_with_private_data: true
  before_group_output_with_private_data: true
  before_local_write: false
privacy:
  level: private
runner:
  model_policy: balanced
  skill_refs:
    - process-documentation
schedule:
  enabled: false
```

## Implementation Roadmap

### Phase 0: Hardening Before Product Work

Duration: 1-2 days.

Tasks:

- Create separate product folder: `projects/home-agent-factory/`.
- Define package schema.
- Define package instance schema.
- Define run log schema.
- Define capability grant schema.
- Create first 3 static agent cards.
- Create security policy document.
- Decide dev stack: simplest likely Node/TypeScript because OpenClaw CLI/runtime is Node-oriented.
- Do not expose to LAN/public yet.

Acceptance:

- Static catalogue can be rendered from YAML.
- Policy validator catches risky package permissions.
- Run log format exists.
- Private-read plus cloud/send/group output combinations are denied by policy tests.

### Phase 1: Runner Spine + One Pack

Duration: 1 week.

Tasks:

- Implement `home-agent list`.
- Implement `home-agent show <slug>`.
- Implement `home-agent run <slug> --input-file`.
- Implement capability-grant enforcement.
- Create run log writer.
- Add approval state file.
- Add Telegram approve/deny for one paused-run path.
- Implement 1 agent pack: private archive RAG.
- Add negative tests for:
  - read outside folder scope;
  - private-read + cloud model without approval;
  - private-read + group-chat output;
  - external POST not allowlisted.

Acceptance:

- A package can run end-to-end.
- Logs show tools, data scope, approvals.
- External send is blocked unless approved.
- Deliberate exfiltration attempts are denied and logged.

### Phase 2: Telegram Launch + Two More Packs

Duration: 1 week.

Tasks:

- Telegram command mapping.
- Persisted paused-run state.
- Default-deny approval timeout.
- Add project status digest.
- Add Telegram support triage.
- Enable one scheduled digest through cron.

Acceptance:

- Non-technical user can run one agent from Telegram.
- Folder scope is explicit.
- Risky permissions are visible before install.
- Scheduled run creates evidence.
- Approval flow works from Telegram.

### Phase 3: Wizard Lite

Duration: 1 week.

Tasks:

- HTML/canvas or local web page listing packages.
- Install/configure package instance.
- Select folder scopes.
- Select channel.
- Test run.
- Enable/disable schedules.
- Show recent run log.
- Model/usage summary.
- Error retries and blocked-run states.

Acceptance:

- User can inspect what the agent touched.
- User can install/configure one agent without editing YAML.

### Phase 4: Demo Pack and Productization

Duration: 1 week.

Tasks:

- Create 2-3 polished end-to-end demos.
- Write landing/product page for internal sharing.
- Create import/export pack format.
- Add package review checklist.
- Add more packs only after runner enforcement is stable.
- Run Claude and Codex review over code/product docs.
- Decide whether to expose on LAN or keep local-only.

Acceptance:

- Demo can be shown live.
- Product can be installed/restarted.
- Clear list of safe capabilities and non-goals.

## Recommended First Sprint

Build the foundation with three files/classes of things:

1. `agent-pack.schema.json`
2. `agent-instance.schema.json`
3. `capability-grant.schema.json`
4. `agent-runs/` append-first log writer and CLI runner
5. `agent-packs/private-archive-rag/`

Then add `project-status-digest` and `telegram-support-triage`. Defer `proposal-draft-builder` until the private-read/cloud/send gates are proven.

## Safety Rules for MVP

- No Synology global search by default; only selected folders.
- No raw Synology content in group chats.
- No outbound message/email/publish without explicit approval.
- No package can request unrestricted shell by default.
- Every package declares data scopes and tools.
- Every run writes evidence before reporting success.
- Marketplace packages start as local curated packs only.
- Any package update goes through review before enablement.
- Package definitions and local package instances are separate.
- Tool calls are enforced by capability grants, not by prompt instructions.

## What Not to Build Yet

- Public SaaS registration.
- Payment/billing.
- Multi-tenant account model.
- Open marketplace with user submissions.
- Full visual workflow builder.
- Desktop automation agent with screen control.
- Wide CRM/1C/WhatsApp integrations before approval and audit UX exist.

## Success Metrics

MVP success is not number of agents. It is:

- 3 curated packs.
- 2 repeatable demos.
- 0 uncontrolled external sends.
- 100% runs logged.
- clear install/run/approval path.
- one real weekly workflow Stanislav keeps using.
- negative exfiltration tests pass.

## Key Open Questions

- Should the first UI be Telegram-first, web/canvas-first, or both?
- Should packages live inside OpenClaw `skills/` or in a separate `agent-packs/` registry that references skills?
- Which tracker/integration should be first for tasks: Markdown TODO, YouGile, GitHub Issues, or something else?
- Which local RAG scope is safe for first demo: workspace docs, a project folder, or a synthetic sample folder?
- Should Home Agent Factory stay private forever, or become a distributable OpenClaw plugin later?

## Verdict

Build a local private agent-factory first. Use Aizor as UX/packaging benchmark, not as architecture benchmark.

The first shippable product is:

> Telegram-first catalogue of safe, installable Home agents with explicit permissions, local data scopes, scheduled runs, approval inbox, and run logs.
