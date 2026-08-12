# Fresh Claude Review: Local Orchestrator Integration

Reviewer: fresh Claude session, read-only
Coordinator: OpenClaw main
Decision authority: deterministic coordinator only

## Goal

Review the new adapter and runner that connect the already accepted reviewer
contract to the already accepted deterministic policy core.

## Allowed files

- `state/tasks/2026-08-12-orchestrator-integration/TASK_PACKET.md`
- `state/tasks/2026-08-12-orchestrator-integration/README.md`
- `state/tasks/2026-08-12-orchestrator-integration/EVIDENCE.md`
- `state/tasks/2026-08-12-orchestrator-integration/review_projection.py`
- `state/tasks/2026-08-12-orchestrator-integration/local_orchestrator_runner.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_integration.py`
- read-only API/contract inspection under
  `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`

Do not inspect unrelated workspace files, memory, config, secrets, Synology, or
the broader dirty worktree. Do not edit files or run network commands.

## Review questions

1. Can an invalid reviewer document or binding mismatch reach a policy decision?
2. Can the adapter falsely close a prior finding, downgrade severity, or invent
   acceptance authority?
3. Can path resolution escape the intended local input boundary or overwrite
   existing audit artifacts?
4. Are input snapshots genuinely immutable enough for the stated local threat
   model, and are failure paths auditable?
5. Does deterministic replay hold for projection and decision output?
6. Are `ACCEPTED`, `REWORK`, `FAILED_INFRA`, and `ESCALATED` exercised without
   weakening the accepted core?
7. Are there missing tests or mismatches against TASK_PACKET acceptance criteria?

## Output

Return findings ordered by severity. Each blocker/major must include exact file
and line, failure scenario, and bounded remediation. Separate spec findings from
standards findings. End with exactly one advisory token:

- `INTEGRATION_PASS`
- `INTEGRATION_REWORK`

The token is reviewer advice only, not task acceptance.
