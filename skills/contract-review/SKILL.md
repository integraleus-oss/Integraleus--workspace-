---
name: "contract-review"
description: "Review contracts for sourced risks, obligations, negotiation questions, and legal caveats."
---

# Contract Review

Use when reviewing contracts, draft agreements, annexes, statements of work, NDAs, service terms, acceptance terms, payment clauses, or commercial/legal correspondence.

This skill helps structure review. It is not legal advice and does not replace a qualified lawyer.

When this is part of a package, receive the shared input packet from `sales-docs-pipeline` and preserve its privacy, product, approval, and external-action boundaries.

## Core Rules

- Do not invent missing clauses or assume local law details without source text.
- Separate `Found in text`, `Inference`, `Risk`, and `Question`.
- Quote only short fragments when needed; otherwise paraphrase and reference section numbers if present.
- Flag business, operational, payment, liability, IP, confidentiality, data/security, acceptance, termination, and dispute risks.
- Mark uncertain legal interpretation as `needs legal review`.
- Do not recommend signing unless the user explicitly asks for a business judgment and risks are clearly listed.
- Preserve confidential content. In group chats, summarize risks without exposing sensitive raw contract text unless Stanislav explicitly provided it for that chat.
- Do not send redlines, accept terms, approve signing, or contact counterparties unless explicitly asked.

## Workflow

1. Identify document type, parties, jurisdiction if stated, version/date, review objective, privacy boundary, and approval state.
2. Build a clause map:
   - scope and deliverables;
   - price and payment;
   - timeline and acceptance;
   - obligations of each party;
   - change control;
   - liability, penalties, indemnity;
   - IP and licensing;
   - confidentiality and data;
   - termination;
   - governing law and disputes;
   - attachments and precedence.
3. Extract hard obligations and deadlines into a compact checklist.
4. Identify missing or ambiguous clauses. Use `[not found]` instead of guessing.
5. Rate issues by severity:
   - `High`: could block signing, create major liability, payment loss, IP loss, impossible obligation, or compliance exposure.
   - `Medium`: negotiable risk, operational ambiguity, acceptance/payment friction.
   - `Low`: wording cleanup, formatting, minor ambiguity.
6. Draft negotiation questions and proposed redlines at business-language level.
7. End with a clear `Decision Support` block: acceptable as-is, acceptable with changes, blocked, or needs legal/business review.

## Output Shape

```markdown
# Contract Review: [document name]

Date: [YYYY-MM-DD]
Version reviewed: [document version/date or unknown]
Review objective: [signing / negotiation / risk scan / compare versions]
Status: [draft / needs business review / needs legal review]
Privacy boundary: [public / internal / confidential / group-safe summary only]

## Executive Summary

- Overall status: [acceptable with changes / needs review / blocked]
- Main risks: [short list]
- Missing information: [short list]

## High-Risk Issues

### [Issue title]

- Found in text: [section / short paraphrase]
- Risk: [why it matters]
- Suggested position: [business-language recommendation]
- Question/redline: [what to ask or change]

## Medium-Risk Issues

[Same shape]

## Low-Risk Issues

[Same shape]

## Obligation Checklist

- [Party] must [action] by [deadline or trigger].
- [Party] must provide [artifact/access/payment].

## Missing / Ambiguous Clauses

- [Clause]: [not found / ambiguous / needs legal review]

## Negotiation Questions

- [Question]

## Decision Support

[Concise recommendation with caveat: business review / legal review / finance review needed.]
```

## Review Checklist

- Parties, dates, attachments, and precedence are identified or marked unknown.
- Payment, acceptance, scope, liability, IP, confidentiality, termination, and dispute clauses were checked.
- Risks are tied to text, not vague impressions.
- Missing clauses are marked `[not found]`.
- Legal uncertainty is marked `needs legal review`.
- Privacy boundary and approval state are explicit.
- Output avoids exposing sensitive raw contract text in shared contexts.

## Handoff Notes

When handing to another reviewer, include:

- document path/source and version;
- review objective;
- high-risk issues;
- clauses needing lawyer review;
- business decisions needed from Stanislav;
- privacy boundary;
- whether raw text can be shared in the target context.
