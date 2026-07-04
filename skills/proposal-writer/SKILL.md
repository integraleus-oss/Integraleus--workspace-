---
name: "proposal-writer"
description: "Draft B2B proposals with sourced facts, privacy boundaries, approvals, and open questions."
---

# Proposal Writer

Use when drafting or revising B2B proposals, commercial offers, pitch documents, cover letters, or sales-response packages.

When this is part of a package, receive the shared input packet from `sales-docs-pipeline` and preserve its privacy, product, approval, and external-action boundaries.

## Core Rules

- Do not invent prices, quantities, deadlines, discounts, product capabilities, references, acceptance criteria, or legal terms.
- Mark estimates explicitly: `оценка автора`, `примерно`, `предварительно`, or `уточнить после аудита`.
- Use `[уточнить]` placeholders where facts are missing and guessing would be risky.
- Keep proposal language concrete: customer problem, proposed scope, deliverables, timeline, assumptions, exclusions, next step.
- Separate factual claims from recommendations and commercial positioning.
- For Alpha platform/product questions, read the current product cheatsheet first and use only listed current components.
- Do not mention deprecated Alpha product names in generated proposal text.
- Preserve privacy boundaries. In group chats, provide a group-safe summary unless raw source details were explicitly cleared for that chat.
- Treat drafts as drafts. Do not send, publish, or mark ready-to-send unless the user explicitly asks and approval state is clear.

## Workflow

1. Identify the customer, decision maker, context, requested outcome, deadline, delivery format, privacy boundary, and approval state.
2. Extract hard facts from provided material: requirements, constraints, current systems, quantities, integrations, budget signals, dates, and stakeholders.
3. Create a fact gap list before drafting. Use placeholders instead of invented details.
4. Choose the proposal type:
   - short email offer;
   - formal commercial proposal;
   - technical-commercial proposal;
   - pilot proposal;
   - renewal/upsell proposal;
   - response to RFP/TKP request.
5. Draft in this order:
   - title and version/date;
   - customer situation;
   - proposed solution and scope;
   - deliverables;
   - project stages and responsibilities;
   - assumptions and exclusions;
   - commercial section with placeholders if numbers are missing;
   - risks and open questions;
   - next step.
6. Review for unsupported claims, hidden assumptions, deprecated product names, privacy leaks, unclear approval state, and missing acceptance criteria.
7. Return the proposal plus a short `Open Questions` block when facts are missing.

## Output Shape

For Russian business proposals, prefer concise professional Russian.

```markdown
# Коммерческое предложение: [тема]

Дата: [YYYY-MM-DD]
Версия: [v0.1]
Статус: [черновик / требуется проверка / готово к отправке после подтверждения]
Граница приватности: [уточнить]
Заказчик: [уточнить]

## Ситуация

[Факты о задаче заказчика. Без выдуманных цифр.]

## Предлагаемое решение

[Что делаем и зачем.]

## Состав работ

- [Работа 1]
- [Работа 2]
- [Работа 3]

## Результаты и приемка

- [Артефакт/результат]: [критерий приемки]

## Сроки

Предварительно: [уточнить / оценка автора].

## Коммерческие условия

Стоимость: [уточнить]
Условия оплаты: [уточнить]
Срок действия предложения: [уточнить]

## Предпосылки и ограничения

- [Что должно быть предоставлено заказчиком]
- [Что не входит в объем]

## Риски и открытые вопросы

- [Вопрос]
- [Риск]

## Следующий шаг

[Конкретное действие: созвон, аудит, согласование состава работ, подготовка TKP.]
```

## Quality Checklist

- Every number is sourced, explicitly estimated, or marked `[уточнить]`.
- The customer can see what they get, what is excluded, and what happens next.
- The document does not promise unavailable product capabilities.
- Alpha product names, when present, match the current product cheatsheet.
- The proposal has acceptance criteria or a clear way to confirm completion.
- Risks and assumptions are visible rather than hidden in sales copy.
- Privacy boundary and approval state are explicit.
- The response does not expose private raw source text in a shared context.

## Handoff Notes

When handing the draft to another agent or reviewer, include:

- source materials used;
- unresolved facts;
- places where estimates were used;
- requested tone and format;
- privacy boundary;
- whether the text is a draft, needs human approval, or is ready only after explicit approval.
