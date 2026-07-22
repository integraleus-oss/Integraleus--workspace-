# Codex Sidecar Review

Date: 2026-07-05

## Summary

Codex sidecar recommended a Home-native MVP rather than an Aizor SaaS clone.

## Recommended Modules

1. Agent Marketplace / Catalog.
2. Agent Runner.
3. No-Code Agent Builder.
4. Workspace Memory & Files.
5. Channels & Inbox.
6. Scheduler / Automations.
7. Admin, usage and safety console.

## OpenClaw Primitives to Reuse

- Gateway.
- Telegram/message tools.
- Cron.
- Sessions.
- Skills.
- Memory.
- Nodes/canvas later.
- Local files and Synology.
- Codex/Claude/OpenAI/Ollama.
- Tool permissions and approvals.

## Main Risks

- Local file/Synology data leakage.
- Context mixing between private memory, project files, and group chats.
- Unapproved external actions.
- Marketplace supply-chain risk.
- Secrets in memory and logs.
- Overbroad tool permissions.
- Unclear responsibility between autonomous actions, drafts, and approvals.

## MVP Shape

2-4 week MVP:

- Week 1: catalogue and runner.
- Week 2: private workspace and local RAG.
- Week 3: Markdown/YAML packaging lite.
- Week 4: admin, reliability, approval inbox, demos.

## Explicit Non-Goals

- No public SaaS, registration, tariffs, or billing.
- No visual canvas builder first.
- No open marketplace with untrusted agents.
- No default full-disk/Synology access.
- No external sends without approval.
- No attempt to cover hundreds of agents.
- No multi-tenant architecture in the first Home version.
