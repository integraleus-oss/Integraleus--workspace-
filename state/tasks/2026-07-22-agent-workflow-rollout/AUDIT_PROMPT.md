# Claude Audit Prompt: Agent Workflow Rollout Plan

Review mode: read-only. Do not edit files. Do not run commands that change the workspace, runtime, config, services, network, Synology, or external systems.

You are auditing this internal Russian-language process plan:

- `state/tasks/2026-07-22-agent-workflow-rollout/PLAN.md`

Context:

- The plan is intended to implement Claude Code / Codex / OpenClaw agent-workflow ideas across existing projects and internal/external agent work.
- It must fit an existing workspace where serious deliverables require an artifact-first workflow, task packets, evidence, review, and clear handoff.
- It must preserve privacy boundaries. In particular, Synology raw data must not leave the home network without explicit user approval, and root-level Synology changes require explicit user approval.
- It must not silently rewrite canonical workspace identity/reference files such as `AGENTS.md`, `TOOLS.md`, `SOUL.md`, or `MEMORY.md`.
- It must distinguish internal drafts from approved/enforced process.

Audit goals:

1. Find missing gates, unclear boundaries, overbroad scope, or implementation risks.
2. Check whether the plan is realistically adoptable across many projects without creating excessive bureaucracy.
3. Check whether the project-by-project rollout order is sensible.
4. Check whether the plan handles external agents safely: Claude Code, Codex CLI, subagents, web/tools, cron/background work.
5. Check whether privacy, Synology, production/deploy, and external-send boundaries are strong enough.
6. Identify specific additions or edits that would make the plan stronger.

Output format:

- Verdict: GO / GO_WITH_FIXES / NO_GO.
- Findings first, severity ordered.
- For each finding include: severity, issue, why it matters, suggested fix.
- Then list missing questions for Stanislav.
- Then list recommended next implementation steps.
- Keep the output concise but actionable.

