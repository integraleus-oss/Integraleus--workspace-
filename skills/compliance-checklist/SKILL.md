---
name: "compliance-checklist"
description: "Build evidence-backed readiness checklists with owners, gaps, approval, and sign-off state."
---

# Compliance Checklist

Use when creating or reviewing compliance, readiness, acceptance, audit, security, delivery, or go/no-go checklists.

When this is part of a package, receive the shared input packet from `sales-docs-pipeline` and preserve its privacy, product, approval, and external-action boundaries.

## Core Rules

- Do not mark an item complete without evidence.
- Use explicit statuses: `pass`, `fail`, `blocked`, `not checked`, `not applicable`.
- Separate requirement, evidence, owner, gap, risk, and next action.
- Do not invent regulatory obligations, certifications, legal requirements, customer requirements, owners, or sign-offs.
- Mark legal/regulatory uncertainty as `needs specialist review`.
- In shared contexts, avoid exposing sensitive raw evidence unless explicitly allowed.
- Do not imply approval, acceptance, readiness, compliance, or sign-off without explicit evidence and user confirmation.

## Workflow

1. Identify checklist purpose: compliance, delivery readiness, security, acceptance, audit, release, or procurement.
2. Identify source of requirements: contract, policy, law, standard, SOP, project DoD, customer request, or user-provided criteria.
3. Capture privacy boundary, approval state, and whether the checklist is a draft or decision artifact.
4. Create categories and checklist items.
5. For each item, capture status, evidence, owner, due date, risk, and next action.
6. Flag missing evidence and unclear responsibility.
7. Produce a summary: ready, ready with exceptions, blocked, not checked, or needs review.
8. Add approval/sign-off fields when the checklist is used for a decision, but leave them empty unless confirmed.

## Output Shape

```markdown
# Checklist: [name]

Purpose: [readiness / compliance / acceptance / audit]
Source requirements: [document/source]
Date: [YYYY-MM-DD]
Owner: [уточнить]
Status: [draft / needs review / decision-ready after approval]
Privacy boundary: [уточнить]
Approval state: [not approved / approved by name/date]

## Summary

- Overall status: [ready / ready with exceptions / blocked / not checked]
- High-risk gaps: [count/list]
- Pending approvals: [list]

## Checklist

### [Category]

| Item | Status | Evidence | Owner | Risk | Next action |
| --- | --- | --- | --- | --- | --- |
| [requirement] | [pass/fail/blocked/not checked/N/A] | [file/link/observation] | [owner] | [risk] | [action] |

## Gaps

- [Gap]: [impact] -> [next action]

## Sign-off

- Prepared by: [name]
- Reviewed by: [name]
- Approved by: [name]
- Approval date: [YYYY-MM-DD]
```

If the target platform does not render tables well, convert the checklist to bullets with the same fields.

## Quality Checklist

- Every `pass` has evidence.
- Every `fail` or `blocked` has next action and owner.
- Requirements are traceable to a source or marked `[уточнить]`.
- Legal/regulatory uncertainty is marked for specialist review.
- Summary matches item statuses.
- Privacy boundary and approval state are explicit.
- Sign-off is not implied without explicit approval.

## Handoff Notes

Include source requirements, evidence paths, unresolved gaps, owner decisions needed, privacy boundary, approval state, and whether the checklist is decision-ready or only a draft.
