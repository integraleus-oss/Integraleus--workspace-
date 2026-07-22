---
name: "proposal-writer-ru"
description: "RU КП/ТКП/SOW drafts with pricing, Alpha, source, and approval guardrails."
---

# Proposal Writer RU

Use this skill to draft internal Russian-language commercial proposal materials: КП, ТКП, SOW-style scope drafts, follow-up proposal letters, partner proposal drafts, and reusable proposal sections.

Default posture: draft-only, source-bounded, internal. Do not send, publish, commit to a customer, or write to CRM/shared systems without separate explicit approval.

## Quick Workflow

1. Classify the proposal type:
   - КП / ТКП;
   - SOW or scope of work;
   - follow-up letter after discovery;
   - partner/reseller proposal;
   - reusable section for a larger document.
2. Identify context and risk class:
   - customer/prospect context;
   - product or service scope;
   - whether Alpha Platform / Alpha.SCADA / Alpha.One+ / Automiq licensing is involved;
   - whether prices, discounts, contract terms, personal data, or confidential material are present.
3. Gather only missing inputs needed for a useful draft. If the user has not provided enough context, ask one concise question or draft a clearly marked skeleton with assumptions.
4. Route regulated/domain-specific content:
   - Alpha Platform licensing, SKU, tariff, tag sizing, SLA, WEB, Terminal/RDP, Historian, Reports, redundancy, client counts -> `alpha-licensing-qa`.
   - Alpha customer presale/TKP/customer sizing/readiness -> `alpha-platform-presale`.
   - Uploaded contracts, ТЗ, КП, PDFs/DOCX/XLSX -> `document-pipeline` retrieval before relying on their contents.
5. Draft in Russian by default, unless the user asks otherwise or source/customer context requires English.
6. Label facts and uncertainty:
   - confirmed facts;
   - source data;
   - assumptions;
   - open questions;
   - exclusions / not included.
7. Run the preflight check before presenting the draft.

## Required Output Structure

For substantial КП/ТКП drafts, include:

1. Working title and draft status.
2. Customer situation / исходная задача.
3. Proposed approach / предлагаемое решение.
4. Scope / состав работ or поставки.
5. Expected outcomes / результат для заказчика.
6. Assumptions and dependencies.
7. Exclusions / что не входит.
8. Commercial section only when allowed by context.
9. Timeline / этапы.
10. Next steps.
11. Open questions.

For short follow-up letters, use a shorter structure:

1. Context line.
2. Proposed next step or offer summary.
3. Key value points.
4. Attachments or missing inputs, if any.
5. Clear call to action.

## Commercial And Pricing Rules

- In Telegram/Discord group chats, do not include exact prices, discounts, private commercial terms, or negotiation position unless a more specific workspace rule explicitly permits it.
- Prices for Alpha/Automiq must be handled only in Stanislav direct chat and only through the current Alpha licensing/presale guardrails.
- Never invent prices, discounts, SKUs, product packages, license rights, SLA, support terms, web/RDP/Terminal rights, redundancy rights, client counts, or usage rights.
- If pricing is needed but not available, write `[цены уточняются]` or a similar placeholder and list the exact missing input.
- Distinguish a commercial proposal from a legally binding offer. Do not call a draft an оферта unless the user explicitly asks and required legal/business terms are supplied.

## Legal And Commitment Boundaries

This skill drafts business text. It does not provide legal advice.

Do not state that:

- a contract is signed, concluded, enforceable, or legally valid;
- an offer has been accepted;
- a party has authority to sign;
- electronic document exchange or electronic signature is valid;
- the organization complies with a legal or regulatory framework.

Use cautious language for commitments:

- `проект предложения`;
- `предварительный вариант`;
- `требует проверки ответственным лицом`;
- `условия подлежат уточнению`.

## Source Discipline

For any factual claim about product capabilities, customer requirements, deadlines, regulations, competitors, tariffs, or prior discussions, identify the source or mark it as an assumption.

Use this block for substantial drafts:

```text
Основано на:
- ...

Предположения:
- ...

Открытые вопросы:
- ...
```

If source material is weak, say so directly and provide the cheapest next check.

## Confidentiality And Privacy

Treat customer names, contacts, contracts, pricing, discounts, roadmap details, unreleased product plans, implementation details, and negotiation context as confidential by default.

Do not place confidential raw details into durable memory. If a memory note would help, propose a sanitized summary and wait for approval.

Before sharing drafts in group chats, redact:

- personal data;
- exact pricing/discounts;
- customer-specific sensitive details;
- contract clause text unless sharing is explicitly approved;
- internal negotiation strategy.

## Preflight Check

Before finalizing a draft, verify:

- scope matches the user's request;
- Alpha licensing/presale content was routed through the proper skill when relevant;
- pricing is absent or explicitly allowed for the current chat context;
- unsupported claims are marked as assumptions;
- open questions are visible;
- external sending/publishing is not performed without separate approval;
- legal/compliance claims are not presented as legal advice or certification;
- the draft is clearly marked as draft when it could be mistaken for a commitment.

## Stop Signals

Stop and ask for approval or missing context when:

- the user asks to send/publish/email/message the proposal externally;
- exact prices, discounts, or confidential commercial terms would be exposed in a group chat;
- Alpha licensing numbers are needed but `alpha-licensing-qa`/`alpha-platform-presale` context is missing;
- the proposal requires legal status, оферта, contract validity, or compliance claims;
- current market/competitor/pricing facts are needed and web research has not been approved;
- source material contains personal data or confidential contract text and the sharing channel is unclear.

## Examples

Good requests for this skill:

- `Сделай черновик КП по внедрению системы, без цен, на основе этих вводных.`
- `Подготовь follow-up письмо после discovery call.`
- `Собери SOW-структуру: этапы, результаты, exclusions, открытые вопросы.`
- `Сделай skeleton ТКП для Alpha Platform, но цены и лицензирование не выдумывай.`

Bad behavior to avoid:

- inventing exact pricing or SKU;
- presenting Alpha licensing assumptions as facts;
- sending a customer-ready message without approval;
- writing legal conclusions;
- using generic marketing fluff instead of customer-specific outcomes.
