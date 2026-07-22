# Claude Review Prompt: Unified Agent Workflow / Shared Memory Plan

Date: 2026-07-22
Mode: read-only review

## Goal

Review the unified development plan for `OpenClaw Shared Memory / Agent Workflow`.

The plan combines:

- shared memory canon backed by Postgres/pgvector;
- privacy/RLS/audit/mirror/backup controls;
- agent workflow templates for task packets, redaction, evidence, and review gates;
- future Synology, MCP/API gateway, and controlled write phases.

## Files To Review

- `docs/UNIFIED_AGENT_WORKFLOW_SHARED_MEMORY_PLAN.md`
- `TODO.md`
- `docs/PHASE0_HARDENING_EVIDENCE.md`
- `docs/PHASE1_LOCAL_PILOT_EVIDENCE.md`
- `docs/RFC-001-shared-memory-canon.md`
- `docs/MCP_TOOLS.md`

You may also inspect:

- `templates/agent-workflow/*.md`
- `migrations/001_initial_schema.sql`
- `migrations/002_hardening.sql`
- `scripts/run_phase1_local_pilot.py`
- `src/openclaw_shared_memory/`

## Security Boundary

Do not request or inspect secrets, `.env` files, dumps, backups, raw Synology file contents, personal chats, or unrelated local memory files.

This review packet should be safe for external model review because it contains project docs, code, and redacted evidence only.

## Review Questions

1. Does the unified plan correctly merge Shared Memory and Agent Workflow, or does it create ambiguous ownership/authority?
2. Are any phase boundaries wrong, especially around Synology, MCP/runtime, external review, Skill Workshop, and real memory import?
3. Is Phase 1.5 the right next step before Synology preparation?
4. Are privacy classes and external-review boundaries strong enough?
5. Are any required artifacts missing from the immediate next work package?
6. Are there contradictions with Phase 0/Phase 1 evidence or current implementation?
7. What must be fixed before Phase 2 preparation?

## Expected Output

Use this structure:

- Verdict: GO / GO_WITH_FIXES / NO_GO
- Blockers
- Important findings
- Nice-to-have improvements
- Residual risks
- Recommended next step
