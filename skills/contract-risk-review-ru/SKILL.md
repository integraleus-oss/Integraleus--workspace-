---
name: "contract-risk-review-ru"
description: "RU contract risk triage, red flags, questions, non-legal advice guardrails."
---

# Contract Risk Review RU

Use this skill for first-pass Russian-language contract and legal-document risk triage: договоры, приложения, NDA, SLA, акты, спецификации, SOW with legal terms, procurement terms, reseller/partner terms, and incoming customer contract drafts.

Default posture: internal risk triage only. This skill does not provide legal advice, does not confirm contract validity, does not certify compliance, and does not replace review by a qualified lawyer or authorized company signatory.

## Quick Workflow

1. Classify the document or request:
   - договор;
   - приложение / спецификация;
   - NDA;
   - SLA / support terms;
   - SOW with legal or acceptance terms;
   - закупочные условия;
   - partner/reseller terms;
   - checklist request without a source document.
2. Confirm source handling:
   - uploaded PDF/DOCX/XLSX must go through `document-pipeline` before content-based review;
   - pasted excerpts may be reviewed only as excerpts, with missing-context caveat;
   - do not rely on memory for exact clause text.
3. Identify channel and confidentiality:
   - in group chats, do not expose raw contract text, prices, personal data, negotiation details, signatures, addresses, bank details, or confidential terms;
   - prefer sanitized summaries and local file outputs.
4. Produce risk triage, not legal conclusion.
5. Separate:
   - observed text / source excerpt reference;
   - risk interpretation;
   - business question;
   - legal-review escalation.
6. End with open questions and suggested next checks.

## Required Output Structure

For substantial reviews, include:

1. Draft status and non-legal-advice notice.
2. Source materials reviewed.
3. Scope and limitations.
4. Executive risk summary.
5. Risk table:
   - topic;
   - observed issue;
   - risk level: low / medium / high / blocker;
   - why it matters commercially or operationally;
   - suggested question or negotiation point;
   - requires lawyer: yes / no / likely.
6. Missing information.
7. Recommended next steps.
8. External-send / signing stop conditions.

For short checklist-only requests, include:

1. When to use.
2. Red flags.
3. Questions to ask.
4. What requires legal review.
5. What not to conclude without counsel.

## Source Discipline

Never quote or summarize a contract as if the full source was reviewed when only an excerpt was supplied.

Use labels:

```text
Источник:
- ...

Ограничения проверки:
- ...

Не является юридическим заключением:
- ...
```

If exact wording matters, cite the document/page/section from retrieval output instead of paraphrasing from memory.

## Risk Areas To Check

Common risk areas:

- parties, authority, signatories, and реквизиты;
- subject matter and scope;
- deliverables and acceptance criteria;
- deadlines and dependency on customer inputs;
- payment terms, taxes, currency, penalties;
- unilateral changes or termination;
- liability caps and uncapped liability;
- warranties, guarantees, service levels, SLA;
- IP rights, source code, licenses, third-party components;
- confidentiality and data protection;
- personal data handling;
- sanctions/export/public-sector/procurement restrictions when relevant;
- dispute resolution and governing law;
- force majeure;
- document hierarchy and conflict between contract, appendix, SOW, PO, SLA;
- auto-renewal and survival clauses;
- customer audit rights or intrusive reporting obligations;
- obligations that conflict with product/licensing guardrails.

Do not present this list as exhaustive legal coverage.

## Alpha / Proposal Routing

If the document contains Alpha Platform / Alpha.SCADA / Alpha.One+ licensing, SKU, tags, SLA, WEB, Terminal/RDP, Historian, Reports, or commercial proposal material:

- licensing and SKU questions -> `alpha-licensing-qa`;
- Alpha presale / ТКП sizing -> `alpha-platform-presale`;
- proposal wording / КП / SOW business text -> `proposal-writer-ru`;
- process/gates -> `process-documentation-ru`.

This skill only flags contract risk around those materials; it does not calculate licenses or create prices.

## Confidentiality And Privacy

Do not place raw contract terms, personal data, prices, signatures, bank details, credentials, or private negotiation details into durable memory.

For group-visible output:

- use sanitized summaries;
- omit exact clause text unless explicitly approved and safe;
- omit prices and bank details;
- omit personal data;
- do not infer negotiation strategy.

## Stop Conditions

Stop and request explicit approval or specialist review when:

- the user asks whether a contract is legally valid, enforceable, compliant, or safe to sign;
- the user asks to sign, approve, accept, send, or reject a contract externally;
- exact clause text must be shared in a group chat;
- the source document has not been ingested but exact review is requested;
- the result would affect legal rights, financial obligations, employment, sanctions, public procurement, personal data, or IP ownership;
- a legal deadline or court/regulatory matter is involved.

## Preflight Check

Before presenting a review:

- draft status is clear;
- non-legal-advice notice is present;
- source and limitations are visible;
- confidential details are redacted for the current channel;
- raw uploaded documents were routed through `document-pipeline`;
- risk levels are framed as triage, not legal certainty;
- signature/send/approval actions are not performed without separate explicit approval;
- open questions and next checks are visible.

## Example Requests

Good requests:

- `Сделай первичный risk review этого договора после ingest.`
- `Выдели красные флаги в NDA, без юридического заключения.`
- `Собери список вопросов юристу по этому SOW.`
- `Сделай чеклист проверки договора перед отправкой юристу.`

Bad behavior to avoid:

- saying the contract is valid or invalid;
- saying it is safe to sign;
- providing legal advice as final answer;
- exposing raw contract text in a group;
- reviewing uploaded files without `document-pipeline`;
- inventing law, court practice, authority, or compliance status.
