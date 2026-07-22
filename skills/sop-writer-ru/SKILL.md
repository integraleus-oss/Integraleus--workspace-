---
name: "sop-writer-ru"
description: "RU SOP drafts with scope, roles, gates, stop conditions, and approval boundaries."
---

# SOP Writer RU

Use this skill to draft internal Russian-language SOPs, operating instructions, working procedures, governance drafts, and repeatable task instructions.

Default posture: internal draft-only. Do not present a SOP as an approved company regulation unless the user explicitly confirms approval. Do not publish, enforce, send externally, change live systems, assign binding responsibility to people, or alter access/config/automation.

## Quick Workflow

1. Classify the SOP type:
   - working instruction;
   - process SOP;
   - approval workflow;
   - handoff procedure;
   - preflight checklist;
   - governance operating rule.
2. Define scope:
   - what task or process the SOP covers;
   - where it applies;
   - where it does not apply;
   - whether pricing, customer data, contracts, legal wording, production systems, or external communication are involved.
3. Identify sources:
   - existing process docs;
   - task state;
   - prior decisions;
   - approved skills;
   - user-provided policy.
4. Separate facts, assumptions, and decisions requiring confirmation.
5. Draft the SOP in Russian by default.
6. Add review gates, stop conditions, and approval boundaries.
7. Mark output as a draft unless official approval is explicitly confirmed.

## Required SOP Structure

For substantial SOPs, include:

1. Title and draft status.
2. Purpose / зачем нужен SOP.
3. Scope and exclusions.
4. Roles and responsibilities.
5. Inputs and source-of-truth materials.
6. Step-by-step procedure.
7. Review gates and quality checks.
8. Stop conditions and escalation.
9. Privacy, pricing, legal, security, and external-action boundaries.
10. Outputs and storage locations.
11. Change control / revision notes.
12. Open questions and next review date.

For short SOPs, use compact sections:

1. When to use.
2. Required inputs.
3. Steps.
4. Checks before completion.
5. Stop conditions.
6. Owner/reviewer placeholders.

## Source Discipline

Do not invent company policy, legal authority, customer commitments, approval rights, pricing rules, or system behavior.

Use explicit labels:

```text
Основано на:
- ...

Предположения:
- ...

Требует подтверждения:
- ...
```

If sources are weak, create a skeleton and list missing inputs.

## Routing Rules

Route specialized content instead of guessing:

- КП/ТКП/SOW business text -> `proposal-writer-ru`.
- Process docs and generic review gates -> `process-documentation-ru`.
- Alpha licensing, SKU, tags, SLA, WEB, Terminal/RDP, Historian, Reports -> `alpha-licensing-qa` and, for presale sizing, `alpha-platform-presale`.
- Uploaded PDF/DOCX/XLSX -> `document-pipeline` before relying on content.
- Contracts, NDA, SLA, legal terms -> `contract-risk-review-ru` for risk triage only.
- Compliance readiness -> a compliance readiness checklist skill when available.

## Approval And External Action Boundaries

Do not:

- send a SOP externally;
- publish it as official;
- enforce it as a company policy;
- change CRM, repository, runtime, config, access rights, cron, or automation;
- assign binding responsibilities to named people unless confirmed;
- expose customer data, prices, contract text, credentials, or personal data.

Use cautious labels:

- `черновик SOP`;
- `предварительная рабочая инструкция`;
- `требует утверждения владельцем процесса`;
- `не является юридическим заключением`.

## Quality Checklist

Before presenting a SOP, verify:

- draft status is visible;
- scope and exclusions are clear;
- roles are not invented;
- sources and assumptions are listed;
- stop conditions are explicit;
- external actions require separate approval;
- pricing/customer/legal/security content is routed or redacted;
- there is no official approval claim unless confirmed;
- open questions are visible.

## Stop Signals

Stop and ask for approval or missing context when:

- the user asks to make the SOP official, publish it, send it, or enforce it;
- production systems, access rights, config, cron, CRM, or repository policy would change;
- exact prices, discounts, customer details, contract text, secrets, credentials, or personal data would appear in a group chat;
- legal status, compliance certification, or signing authority is asserted;
- source materials are missing and drafting would create false authority.

## Examples

Good requests:

- `Сделай SOP подготовки КП перед отправкой`.
- `Оформи рабочую инструкцию для handoff между main и Home`.
- `Опиши SOP проверки документа перед внешней отправкой`.
- `Собери внутренний регламент triage входящих договоров`.

Bad behavior to avoid:

- presenting a draft as an approved regulation;
- inventing official process owners;
- bypassing specialized licensing/legal/document retrieval checks;
- publishing customer-facing instructions without approval;
- embedding prices or raw contract text in group-visible output.
