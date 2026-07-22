# Claude Review Prompt

Review the Home AI Office product plan below.

Context:

- Goal: build an Aizor-like but private/Home-native product on OpenClaw Home.
- Aizor benchmark: desktop AI agent, web cabinet, marketplace, subscription/tokens, public API, 426 marketplace cards, role-oriented Russian business use cases.
- Home primitives: OpenClaw gateway, Telegram, cron, sessions, skills, memory, nodes/canvas, local files, Synology, Codex/Claude/OpenAI/Ollama, approvals.
- Important security: Synology/raw private files must not leave the home network without explicit permission. Group chats must not receive private data.

Please return concise Markdown:

1. Verdict: pass / pass_with_notes / needs_rework.
2. Top 5 risks or missing pieces.
3. MVP scope corrections.
4. Architecture corrections.
5. Security/privacy corrections.
6. First-sprint recommendation.

Do not invent external facts. Review only the supplied plan.

--- PRODUCT PLAN ---
# Product Plan: Home AI Office

Date: 2026-07-05
Status: Draft for review

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
- Later web endpoint: `POST /agent-runs`.

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

## First 15 Agent Packs

Pick packs that reuse existing Home strengths and demonstrate business value.

1. **Voice Task Dispatcher**
   Telegram voice/text -> structured tasks + approval -> task tracker or Markdown TODO.

2. **Private Archive RAG**
   Ask over selected local folder, with citations and no raw exfiltration.

3. **Meeting/Call to Actions**
   Transcript -> decisions, tasks, risks, follow-up draft.

4. **Proposal Draft Builder**
   Uses existing `sales-docs-pipeline` / `proposal-writer`.

5. **Contract Risk Reviewer**
   Uses `contract-review`; produces risks, obligations, questions.

6. **SOP Generator**
   Uses `sop-writer`; outputs runnable procedure with rollback/checks.

7. **Compliance Checklist**
   Uses `compliance-checklist`; tracks owners/evidence/gaps.

8. **Presentation Builder**
   Uses `presentation-designer`; creates `.pptx` from brief.

9. **SEO Article Assistant**
   Research -> outline -> draft -> publish-ready Markdown, approval before publish.

10. **Website Health Monitor**
    Checks uptime, links, titles/meta, indexation notes, obvious regressions.

11. **Telegram Support Triage**
    Classifies inbound messages, drafts replies, asks approval before send.

12. **Finance Receipt Capture**
    Photo/text receipt -> extracted fields -> local spreadsheet draft.

13. **Project Status Digest**
    Reads selected project state/TODO/git status -> concise status.

14. **Code Review Sidecar**
    Runs Codex/Claude review wrappers on diffs and writes findings.

15. **Server Health Sentinel**
    Uses existing healthcheck patterns; status, warnings, safe remediation suggestions.

## Data Model Draft

```yaml
slug: voice-task-dispatcher
name: Voice Task Dispatcher
version: 0.1.0
