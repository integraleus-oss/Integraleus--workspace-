---
name: "process-documentation"
description: "Document processes with actors, evidence, gaps, boundaries, and verification checks."
---

# Process Documentation

Use when documenting business, sales, marketing, operational, technical, or cross-team processes.

When this is part of a package, receive the shared input packet from `sales-docs-pipeline` and preserve its privacy, product, approval, and external-action boundaries.

## Core Rules

- Describe the process as it actually works, not as it ideally should work, unless the user asks for a target process.
- Separate current state, target state, gaps, and decisions.
- Do not invent owners, SLAs, systems, forms, approvals, metrics, or evidence.
- Use `[уточнить]` for missing actors, inputs, outputs, controls, owners, or approval points.
- Capture evidence: source files, interviews, logs, screenshots, tickets, or chat decisions when available.
- Mark risks and assumptions explicitly.
- Preserve privacy boundaries. In group/shared contexts, summarize private evidence rather than exposing raw source text unless explicitly allowed.
- Do not declare a process approved or operationally adopted without explicit confirmation.

## Workflow

1. Identify process name, purpose, owner, scope, start trigger, end state, privacy boundary, and approval state.
2. List actors and systems.
3. Capture inputs, outputs, documents, and data stores.
4. Write the current-state flow step by step.
5. Mark decisions, branches, approvals, handoffs, controls, and exception paths.
6. Identify gaps, risks, unclear ownership, duplicate work, and missing evidence.
7. If requested, propose a target-state flow and migration plan.
8. Add a verification checklist: who must confirm the process and what evidence proves it works.

## Output Shape

```markdown
# Process: [name]

Status: [current-state / target-state / draft / needs review]
Owner: [уточнить]
Version/date: [YYYY-MM-DD]
Privacy boundary: [уточнить]
Approval state: [draft / review-needed / approved]

## Purpose

[Why this process exists.]

## Scope

In scope:
- [item]

Out of scope:
- [item]

## Actors and Systems

- [Actor/system]: [role]

## Inputs and Outputs

Inputs:
- [input]

Outputs:
- [output]

## Current Flow

1. [Trigger]
2. [Step, actor, system]
3. [Decision/branch]
4. [End state]

## Exceptions

- [Condition] -> [handling]

## Controls and Evidence

- [Control]: [evidence/source]

## Gaps and Risks

- [Gap/risk]

## Open Questions

- [Question]

## Verification Checklist

- [ ] Owner confirmed.
- [ ] Inputs/outputs confirmed.
- [ ] Exception paths confirmed.
- [ ] Evidence attached or referenced.
- [ ] Approval state confirmed.
```

## Quality Checklist

- Trigger and end state are clear.
- Every step has an actor or system.
- Handoffs and approvals are visible.
- Missing facts are marked `[уточнить]`.
- Current state and target state are not mixed.
- Verification owner and evidence are listed.
- Privacy boundary and approval state are explicit.
- Private source evidence is summarized safely for the target context.

## Handoff Notes

Include source materials, unresolved questions, process owner, privacy boundary, approval state, and whether the document is ready for team review or still a discovery draft.
