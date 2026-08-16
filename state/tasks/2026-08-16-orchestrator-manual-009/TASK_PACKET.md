# Manual-009 — capability-grant runtime/schema contract

Status: COMPLETE — ESCALATED; TRANSFER PROHIBITED

## Goal

Run the final varied manual-use task: align the capability grant emitted by
runtime with its JSON Schema and prove the contract using shared exported
grammar and representative grants.

## Fixed point

- Source baseline: `8985b8e95427c471662562afa1b89a9e5b17a6a0`.
- Detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-009-capability-grant`.
- Managed run root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-009-capability-grant-run`.

## Allowed paths

- `src/core/policy.js`
- `schemas/capability-grant.schema.json`
- `test/policy.test.js`

## Boundaries

- Maximum two Codex implementations plus one policy-required review-only
  final-full leg.
- No source transfer or commit in this task.
- No dependency, network, push, deploy, Gateway/runtime/config, cron,
  systemd/daemon, unattended, Synology, or external-system change.
- Stop fail-closed on scope drift, failed gates, invalid review contract,
  unresolved blocker/major, timeout, interruption, or unknown failure.
