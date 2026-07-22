---
name: "process-documentation-ru"
description: "RU process docs, SOPs, review gates, ownership and approval workflows."
---

# Process Documentation RU

Use this skill to draft and maintain internal Russian-language process documentation: регламенты, SOP, рабочие инструкции, чеклисты, RACI-style role descriptions, approval workflows, document handoff procedures, and review gates for marketing, sales, presale, proposal, SOW, and operational document work.

Default posture: internal draft-only. Do not publish externally, change live business process, assign real accountability to people, or send messages on behalf of the user without separate explicit approval.

## Quick Workflow

1. Classify the process document type:
   - краткий SOP / рабочая инструкция;
   - регламент подготовки документа;
   - checklist / preflight gate;
   - handoff procedure;
   - review and approval workflow;
   - roles and responsibility matrix;
   - intake form / source data checklist.
2. Identify process scope:
   - which artifact is produced: КП, ТКП, SOW, follow-up, договор, внутренний отчёт, презентация;
   - who creates, reviews, approves, and sends it;
   - which systems or repositories are touched;
   - whether customer data, pricing, legal text, Alpha licensing, or external publication is involved.
3. Gather only the missing inputs needed for a useful draft. If the source is incomplete, draft a marked skeleton and list open questions.
4. Route specialized content:
   - КП/ТКП/SOW business text -> `proposal-writer-ru`.
   - Alpha Platform / Alpha.SCADA / Alpha.One+ licensing, SKU, tags, SLA, WEB, Terminal/RDP, Historian, Reports -> `alpha-licensing-qa` and, for customer presale/TKP sizing, `alpha-platform-presale`.
   - Uploaded PDF/DOCX/XLSX or customer source files -> `document-pipeline` before relying on their contents.
   - contract/legal risk triage -> a contract review skill when available; do not provide legal advice.
5. Draft in Russian by default unless asked otherwise.
6. Separate facts from assumptions and decisions.
7. Add a preflight/checkpoint section before the process can be considered ready for use.

## Required Output Structure

For substantial process documents, include:

1. Title and draft status.
2. Purpose / зачем процесс нужен.
3. Scope / где применяется and where it does not apply.
4. Roles and responsibilities.
5. Inputs and source-of-truth materials.
6. Step-by-step workflow.
7. Review and approval gates.
8. Stop conditions and escalation path.
9. Privacy, pricing, legal, and external-send boundaries.
10. Output artifacts and storage locations.
11. Quality checklist.
12. Open questions and next revision points.

For short checklists, use a compact structure:

1. When to use.
2. Required inputs.
3. Checks before work starts.
4. Checks before sharing or sending.
5. Stop conditions.
6. Owner / reviewer fields.

## Source Discipline

Do not invent organizational policy, legal authority, approval rights, or system behavior.

Use explicit labels:

```text
Основано на:
- ...

Предположения:
- ...

Решения, требующие подтверждения:
- ...
```

If source material is weak, write a skeleton and make the missing source obvious.

## Approval And External Action Boundaries

This skill documents a process; it does not execute that process.

Do not:

- send documents to customers;
- publish process documents externally;
- change CRM, repository, runtime, automation, access rights, or live configuration;
- assign binding responsibilities to named people unless already confirmed;
- state that a process is officially approved unless the user says so.

Use cautious labels:

- `черновик процесса`;
- `предварительная инструкция`;
- `требует подтверждения владельцем процесса`;
- `не является юридическим заключением`.

## Confidentiality And Privacy

Treat customer data, personal data, pricing, discounts, contracts, implementation details, internal negotiation context, and private roadmap details as confidential by default.

Before preparing a group-visible process document, redact or generalize:

- personal names and contacts unless explicitly approved;
- exact prices, discounts, and negotiation positions;
- customer-specific details;
- contract clause text;
- secrets, tokens, private URLs, passwords, OTP, and credentials.

Do not place confidential raw details into durable memory. If durable memory would help, propose a sanitized summary first.

## Common Process Patterns

### КП / ТКП Preparation

Recommended gates:

1. Intake gate: source materials and owner are known.
2. Scope gate: artifact type and intended audience are known.
3. Domain gate: Alpha/licensing/legal/document retrieval routing completed when relevant.
4. Draft gate: draft clearly marked as internal/preliminary.
5. Review gate: unsupported claims, assumptions, and open questions visible.
6. Commercial gate: pricing/discounts only in an allowed channel and from approved sources.
7. External-send gate: separate explicit approval before sending or publishing.

### Handoff Procedure

Include:

- source of truth;
- sender and receiver roles;
- files or paths transferred;
- checksum or version marker when useful;
- what the receiver must verify;
- what remains out of scope;
- rollback or blocked path.

### Review Checklist

Include checks for:

- scope;
- source evidence;
- privacy;
- pricing;
- legal wording;
- unsupported commitments;
- routing to specialized skills;
- explicit approval for external action.

## Preflight Check

Before presenting a process document, verify:

- the document is marked as draft unless approval is confirmed;
- scope and exclusions are visible;
- roles are not invented;
- source-of-truth materials are named or missing materials are listed;
- confidential details are redacted for the current channel;
- external sending/publishing is not performed without separate approval;
- Alpha, uploaded documents, legal contracts, and pricing were routed to the proper skill/tool when relevant;
- open questions and next revision points are visible.

## Stop Signals

Stop and ask for approval or missing context when:

- the user asks to send, publish, install, apply, or enforce the process;
- the process changes production systems, access rights, automation, CRM, or repository policy;
- exact prices, discounts, customer details, or contract text would be exposed in a group chat;
- legal status, compliance certification, or authority to sign is being asserted;
- source materials are missing and a reasonable draft would create false process authority.

## Examples

Good requests for this skill:

- `Опиши процесс подготовки КП от входящих данных до отправки.`
- `Сделай чеклист проверки ТКП перед отправкой клиенту.`
- `Собери handoff-процедуру между main и Home.`
- `Оформи SOP для работы с входящими PDF/DOCX перед подготовкой КП.`

Bad behavior to avoid:

- presenting a draft as an approved company regulation;
- inventing process owners or approval authority;
- sending a customer-facing message without explicit approval;
- embedding private prices or customer data in group-visible text;
- bypassing `document-pipeline`, Alpha licensing/presale, or legal-risk routing when relevant.
