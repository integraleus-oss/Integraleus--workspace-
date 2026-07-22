# Claude Review Summary: Unified Agent Workflow / Shared Memory Plan

Date: 2026-07-22
Review output: `/home/stanislav/agent-runs/2026-07-22-openclaw-shared-memory-unified-plan-review/logs/claude-unified-plan-review.json`

## Verdict

`GO_WITH_FIXES`

## Findings

- The unified direction is sound: Shared Memory as canon, Agent Workflow as admission/operating layer.
- Phase order is generally correct: local workflow proof before Synology, Synology pilot before runtime gateway, read-only before controlled writes, migration last.
- The review root was `projects/openclaw-shared-memory`, so Claude did not see workspace-level templates under `/home/stanislav/.openclaw/workspace/agents/main/templates/agent-workflow/`. This exposed a real documentation ambiguity: the unified plan must name the workspace-root template path explicitly.
- `MCP_TOOLS.md` was stale relative to Phase 0/1 implementation and omitted `reject_candidate`, `archive_record`, `list_candidates`, and promotion confirmation fields.
- Plaintext mirror policy should be stated as a positive allowlist, not a denylist. Current production-like default is `shared_safe` only.
- The three pre-Phase2 follow-ups must belong to Phase 1.5 or be explicit blockers:
  - backup LOGIN `BYPASSRLS` provisioning in deploy docs;
  - expected error types in negative tests;
  - automated mirror/backup/restore/container-stop checks.
- Phase 1.5 should include a sample redacted Memory Candidate derived only from evidence.

## Fixes Applied

- Updated `docs/UNIFIED_AGENT_WORKFLOW_SHARED_MEMORY_PLAN.md` to use the explicit workspace-root template path.
- Updated mirror boundary wording to `shared_safe` allowlist by default.
- Assigned pre-Phase2 follow-ups to Phase 1.5.
- Added sample Memory Candidate to Phase 1.5 deliverables.
- Added phase labels to open questions.
- Updated `docs/MCP_TOOLS.md` to match current hardened workflow.

## Residual Risks

- External-review redaction is still procedural until Phase 1.5 creates a concrete security precheck and audit packet instance.
- The pending Skill Workshop proposal remains unapplied until explicit approval.
- Synology, OpenClaw runtime config, and real memory import remain blocked until later explicit approvals.
