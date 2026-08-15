# Orchestrator pilot rework

Status: TECHNICALLY COMPLETE; AWAITING READINESS DECISION; NOT ACTIVATED

## Goal

Close the two blocking defects recorded by `D-2026-08-15-04` without expanding
the orchestrator's activation or operational authority.

## Fixed baseline

- Workspace commit: `aeeb316`
- Release subject under rework: `b300207`
- Pilot evidence: `state/tasks/2026-08-15-orchestrator-manual-pilot/`

## Allowed files

- `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/managed_one_cycle.py`
- `state/tasks/2026-08-12-orchestrator-integration/trusted_review_builder.py`
- focused tests under
  `state/tasks/2026-08-12-orchestrator-integration/tests/`
- `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py`
- focused validator tests under that implementation directory
- this task directory and final state/decision artifacts after approval

## Required behavior

1. Targeted re-review receives sufficient sealed prior-finding content to
   identify and honestly re-verify each carried finding, not only ID/status.
2. Foreground `Ctrl-C` terminates the active child process group, writes a
   structured terminal `INTERRUPTED` result with available evidence, exits
   predictably, and never continues automatically.

## Checks

- Red tests reproduce both defects before fixes.
- Focused tests pass after fixes.
- Full integration suite passes.
- `python3 -m py_compile` passes for changed Python files.
- `git diff --check` passes.
- Repeat T02 re-verification in a fresh detached worktree/run root.
- Repeat live operator-interruption drill and verify no orphan process, no
  source change, no automatic continuation, and structured terminal evidence.

## Boundaries

- No push, deploy, Gateway, OpenClaw runtime/config, cron, systemd, daemon,
  unattended execution, package, firewall, auth, or Synology changes.
- No source-project commit or transfer of pilot task implementations.
- Local scoped commit is permitted only after all checks and evidence pass.
- Stop on scope breach, unknown failure, incomplete evidence, or regression.

## Checklist

- [x] Task packet created before implementation.
- [x] Red tests captured.
- [x] Prior-finding carry fixed and tested.
- [x] Structured interruption fixed and tested.
- [x] Focused and full suites passed.
- [x] T02 re-verification passed and targeted replay completed fail-closed.
- [x] Live interruption drill passed.
- [x] Final report completed.
- [x] Scoped commit prepared and created as the closing action.
