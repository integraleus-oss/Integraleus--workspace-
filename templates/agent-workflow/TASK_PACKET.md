# Task Packet: <short name>

Status: draft
Risk: <LOW / MEDIUM / HIGH>
Owner: <main agent / human / job>
Date: <YYYY-MM-DD>

## Goal

- <specific outcome>

## Why Now

- <reason this work matters>

## Risk Tier

Selected tier: <LOW / MEDIUM / HIGH>

Rationale:

- <why this tier fits>

Auto-escalate to MEDIUM/HIGH if the task touches private data, customer data, personal messages, secrets, production systems, access rights, Synology root/DSM settings, destructive actions, or external send.

## Scope

Allowed:

- <files, directories, systems, commands, actions>

Forbidden:

- secrets/tokens/passwords/API keys;
- `.env` contents unless explicitly needed and kept local;
- production deploys or access changes without explicit approval;
- direct writes to `/opt` unless explicitly approved;
- root-level changes without explicit approval;
- Synology root-level or DSM changes without explicit approval;
- external send without explicit approval and `SECURITY_PRECHECK.md`;
- customer/public messages without explicit approval;
- destructive operations without explicit approval;
- unrelated refactors.

## Source Of Truth

- <docs, files, tickets, user messages, specs>

## Inputs

- <provided or discovered inputs>

## Assumptions

- <assumption>

## Open Questions

- [ ] <question>

## Plan

- [ ] Research/source review
- [ ] Implementation or draft
- [ ] Evidence capture
- [ ] Review gate if required
- [ ] Handoff/final report

## Required Evidence

- commands run;
- files changed;
- tests/smoke checks;
- screenshots for UI;
- logs/health checks for services;
- counts/checksums for data migration;
- unresolved risks.

## Review Gate

Mandatory review if:

- risk is HIGH;
- project is privacy-sensitive;
- task prepares external/customer-facing material;
- task changes templates, process rules, migrations, schemas, cron/background automation, or access boundaries;
- main agent is uncertain about regressions or privacy.

Reviewer:

- <Claude / Codex / main self-review / human>

## Approval Gate

Explicit approval required before:

- HIGH-risk step;
- production deploy;
- external send;
- public/customer-facing send;
- root-level/system changes;
- Synology root-level/DSM changes;
- destructive operation;
- migration switchover/IP swap/storage pool change.

Approval record:

- <who approved, where, timestamp/message id>

## Done Means

- [ ] Goal achieved or blocker documented
- [ ] Evidence captured
- [ ] Review findings resolved or accepted as residual risk
- [ ] User-facing report sent if needed
- [ ] Commit/handoff state recorded when relevant
