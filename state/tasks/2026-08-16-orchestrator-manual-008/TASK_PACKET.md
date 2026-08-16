# Manual-008 — safe project JSON loading

Status: COMPLETE — ACCEPTED / R17_ACCEPT; TRANSFER NOT PERFORMED

## Goal

Exercise the orchestrator on a filesystem/input-boundary task by replacing
raw CLI JSON reads with one bounded fail-closed loader for project-owned pack
and instance files.

## Fixed point

- Source: `/home/stanislav/projects/home-agent-factory`.
- Baseline: `8985b8e95427c471662562afa1b89a9e5b17a6a0`.
- Detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-008-json-instance`.
- Managed run root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-008-json-instance-run`.

## Allowed paths

- `src/cli/factory.js`
- `src/core/json-file.js` (new)
- `test/json-file.test.js` (new)

## Boundaries

- Maximum two Codex implementations plus policy-required review-only
  final-full.
- No source transfer or commit in this task.
- No dependency, network, push, deploy, Gateway/runtime/config, cron,
  systemd/daemon, unattended, Synology, or external-system change.
- Stop fail-closed on scope drift, failed gates, invalid review contract,
  unresolved blocker/major, timeout, interruption, or unknown failure.

## Checks

- `npm test`
- `git diff --check`
- sealed changed-path, evidence, and policy admission
