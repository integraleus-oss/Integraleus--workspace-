---
name: "sales-docs-pipeline"
description: "Orchestrate sales docs package with shared input, privacy, approval, and quality gates."
---

# Sales Docs Pipeline

Use when the user needs a connected sales, marketing, contract, process, SOP, or readiness document package rather than one standalone document.

This is the package-level orchestrator. It owns shared context, routing, privacy/product/approval boundaries, and final quality gates. Individual document skills own only their document-specific structure and risks.

## Related Skills

Use this skill to choose and sequence:

- `proposal-writer`
- `contract-review`
- `process-documentation`
- `sop-writer`
- `compliance-checklist`

## Core Rules

- Start with a shared input packet before drafting documents.
- Do not invent prices, dates, terms, owners, product capabilities, regulatory duties, legal interpretations, or acceptance criteria.
- Mark missing facts as `[уточнить]` in Russian-first business documents.
- Mark estimates explicitly.
- Respect privacy boundaries, especially in group chats and when source files are private.
- Never expose raw private source text in a shared/group context unless Stanislav explicitly allowed that exact disclosure.
- For Alpha-related product claims, read the current product cheatsheet before naming products/modules and use only current components.
- Keep approval state visible: draft, review-needed, ready-to-send, approved, or internal-only.
- Do not send, publish, apply, sign, approve, or externally share generated documents unless the user explicitly asks for that action.

## Shared Input Packet

Collect or create this once and pass it to selected document skills:

- Customer/project: `[уточнить]`
- Document goal: proposal, contract review, process doc, SOP, checklist, or combined package
- Audience: decision maker, lawyer, buyer, engineer, operator, support, internal team
- Source materials: files, messages, notes, requirements, templates
- Hard facts: quantities, dates, systems, names, constraints
- Missing facts: `[уточнить]`
- Approval boundary: draft only, human review needed, ready to send after approval, approved, or internal-only
- Privacy boundary: public, internal, confidential, local-only, Synology/home-only, or group-safe summary only
- Product boundary: Alpha-related or not; if Alpha-related, use the product guardrail
- External-action boundary: no external action unless explicitly requested

## Routing

- Need a commercial offer or response to request: use `proposal-writer`.
- Need to review terms, obligations, risks, or signing readiness: use `contract-review`.
- Need to document how work happens: use `process-documentation`.
- Need executable repeatable instructions: use `sop-writer`.
- Need evidence-backed readiness, acceptance, audit, or go/no-go status: use `compliance-checklist`.

## Pipeline Order

1. Proposal: scope, value, exclusions, assumptions, open questions.
2. Contract review: terms, risks, obligations, negotiation questions.
3. Process documentation: actors, systems, inputs, steps, outputs, controls.
4. SOP: executable steps, checks, rollback, escalation.
5. Checklist: requirements, evidence, owners, status, gaps, sign-off.

Skip steps that do not match the user's goal, but keep dependencies clear.

## Output Shape

```markdown
# Sales/Docs Package: [name]

Status: [draft / review-needed / ready-to-send-after-approval / approved / internal-only]
Date: [YYYY-MM-DD]
Privacy boundary: [public / internal / confidential / local-only / group-safe summary only]

## Shared Input Packet

[Filled packet]

## Selected Documents

- [document/skill]: [why included]

## Draft Outputs

### Proposal

[summary or link]

### Contract Review

[summary or link]

### Process

[summary or link]

### SOP

[summary or link]

### Checklist

[summary or link]

## Open Questions

- [question]

## Approval / Next Action

[concrete action and who must approve it]
```

## Quality Gate

Before final response, check:

- The package has a clear audience, privacy boundary, and approval state.
- Missing facts are visible.
- No numbers, legal duties, regulatory obligations, or product claims were invented.
- Risky/legal/commercial assumptions are marked.
- Private source text is not leaked into shared contexts.
- Alpha product claims, if any, were checked against the product guardrail.
- Next action is specific and does not imply approval where none was given.

## Handoff Notes

When handing to another agent, include the shared input packet, selected skill sequence, generated artifacts, unresolved facts, privacy boundary, approval state, and external-action boundary.
