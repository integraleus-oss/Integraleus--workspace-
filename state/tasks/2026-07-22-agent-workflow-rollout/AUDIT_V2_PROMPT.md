# Claude Audit Prompt: Agent Workflow Rollout Plan v2

You are doing a read-only process, safety, and operational audit.

File to audit:

- `state/tasks/2026-07-22-agent-workflow-rollout/PLAN_V2.md`

Context:

- v1 was audited and returned `GO_WITH_FIXES`.
- v2 is intended to incorporate the first audit findings before any canonical rule changes.
- This is still a draft, not an enforced policy.

Please review whether v2 is ready to use as the basis for Phase 0 template creation.

Focus on:

1. Whether the first audit findings are actually addressed.
2. Whether risk tiers are concrete enough to guide agents.
3. Whether external review / packet data minimization prevents privacy leaks.
4. Whether cron, heartbeat, and background agents are constrained enough.
5. Whether protected canonical files and existing rules are handled safely.
6. Whether rollout phases are practical and not too broad.
7. Whether there are contradictions, missing approvals, or ambiguous stop conditions.
8. Whether anything should block Phase 0.

Return a concise structured review:

- Verdict: GO / GO_WITH_FIXES / NO_GO
- Blockers
- Important fixes before Phase 0
- Nice-to-have improvements
- Residual risks
- Recommended next step

Do not edit files. Do not run write commands. Do not inspect private files beyond what is necessary to evaluate the listed plan and nearby audit context.
