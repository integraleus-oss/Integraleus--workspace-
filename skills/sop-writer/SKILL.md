---
name: "sop-writer"
description: "Write SOPs with prerequisites, checks, rollback, approvals, and evidence capture."
---

# SOP Writer

Use when writing standard operating procedures, repeatable work instructions, checklists, runbooks, or operator-facing procedures.

When this is part of a package, receive the shared input packet from `sales-docs-pipeline` and preserve its privacy, product, approval, and external-action boundaries.

## Core Rules

- Write procedures for execution, not for explanation only.
- Every SOP needs owner, scope, prerequisites, steps, checks, expected result, and escalation path.
- Do not invent credentials, commands, paths, systems, approvals, responsibility owners, or access rights.
- Mark destructive, external, production, root-level, irreversible, or privacy-sensitive actions as requiring explicit approval.
- Prefer short numbered steps with observable results.
- Include rollback or stop conditions when the action can change state.
- Preserve privacy boundaries. Do not include secrets, credentials, private raw data, or confidential evidence in shared outputs.
- Do not mark an SOP approved, adopted, or executed unless the user explicitly confirms that state.

## Workflow

1. Identify audience: operator, sales, engineer, manager, support, or agent.
2. Define purpose, scope, prerequisites, access, tools, safety limits, privacy boundary, and approval state.
3. Write the procedure as executable steps.
4. After each risky or important step, add expected result or verification.
5. Add exception handling, rollback, escalation, and evidence to capture.
6. Add completion criteria and review cadence.
7. Run a clarity pass: remove vague verbs, hidden prerequisites, missing owners, unsafe assumptions, and unclear approvals.

## Output Shape

```markdown
# SOP: [name]

Owner: [уточнить]
Audience: [уточнить]
Status: [draft / needs review / approved]
Version/date: [YYYY-MM-DD]
Privacy boundary: [уточнить]
Approval boundary: [уточнить]

## Purpose

[What this SOP achieves.]

## Scope

Included:
- [item]

Excluded:
- [item]

## Prerequisites

- [Access/tool/input]

## Safety Notes

- [Approval boundary / data boundary / production boundary]

## Procedure

1. [Action]
   Expected result: [observable result]
2. [Action]
   Check: [command, file, screenshot, or human confirmation]
3. [Action]
   Stop if: [condition]

## Rollback / Recovery

- [Recovery action]

## Escalation

- Contact/owner: [уточнить]
- Escalate when: [condition]

## Completion Criteria

- [ ] [Check]
- [ ] [Evidence captured]
- [ ] Approval state confirmed.

## Revision Notes

- [YYYY-MM-DD]: [change]
```

## Quality Checklist

- The SOP can be followed by the target audience without hidden context.
- Steps are numbered and observable.
- Risky actions have approval boundaries and stop conditions.
- Completion criteria are testable.
- Owners and escalation paths are explicit or marked `[уточнить]`.
- Privacy boundary and approval state are explicit.
- The SOP does not expose secrets or private raw data.

## Handoff Notes

Include target audience, source process, required approvals, unresolved facts, privacy boundary, approval state, and whether the SOP has been dry-run or only drafted.
