# Evidence: Local Alpha Agent Rules

Status: draft
Date: 2026-07-22
Task note: `state/tasks/2026-07-22-local-alpha-agent-rules/TODO.md`

## Summary

- Created draft rules for a local weak model agent working with Alpha Platform product names, tariffs, licensing, presale intake, and handoff boundaries.
- Rules are intentionally conservative: the local agent may draft and collect inputs, but must not invent SKU/prices or produce final financial answers without all required sources.

## Files Created Or Changed

- `state/tasks/2026-07-22-local-alpha-agent-rules/TODO.md` - task note and checklist.
- `state/tasks/2026-07-22-local-alpha-agent-rules/LOCAL_ALPHA_AGENT_RULES.md` - draft local-agent rules.
- `state/tasks/2026-07-22-local-alpha-agent-rules/LOCAL_ALPHA_AGENT_RULES_RU.md` - Russian canonical draft after user feedback.
- `state/tasks/2026-07-22-local-alpha-agent-rules/EVIDENCE.md` - evidence and verification record.

## Sources Read

```bash
sed -n '1,260p' docs/alpha_platform/PRODUCT_CHEATSHEET.md
sed -n '1,260p' playbooks/PRESELL_FASTLANE.md
sed -n '1,300p' playbooks/EDGE_CASES.md
sed -n '1,280p' /home/stanislav/.openclaw/workspace/data/licensing_automiq/rules_hard_checks.md
```

Result:

- Product names, forbidden deprecated names, family selection, tag calculation, edge cases, financial output format, and hard checks were incorporated.

## Checks

- [x] Skill Workshop proposal created: `local-alpha-agent-rules-20260722-ff2d621a7b`.
- [x] `git diff --check` run.

## Review

- Reviewer: none yet
- Review artifact: none
- Verdict: not run

## Approval Evidence

- Not required. No external send, production change, customer-facing answer, root-level action, or Synology data action was performed.

## Residual Risks

- The rules are a draft and should be tested on one or two old non-sensitive licensing examples before being treated as operational.
- Exact tariff/SKU access path for the local agent still needs to be decided.

## Handoff

- Next step: decide whether to apply this as a live reusable skill or keep it as a local prompt/checklist.
- Pending Skill Workshop proposal: `local-alpha-agent-rules-20260722-ff2d621a7b`.
- Russian file should be treated as canonical for the local Qwen agent.
