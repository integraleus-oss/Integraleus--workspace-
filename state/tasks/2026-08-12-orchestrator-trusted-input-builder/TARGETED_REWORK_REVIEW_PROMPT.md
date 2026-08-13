# Targeted rework review

Review only the current uncommitted orchestrator trusted-builder slice in:

- `state/tasks/2026-08-12-orchestrator-integration/managed_one_cycle.py`
- `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/trusted_review_builder.py`
- `state/tasks/2026-08-12-orchestrator-integration/local_orchestrator_runner.py`
- the corresponding changed tests under `state/tasks/2026-08-12-orchestrator-integration/tests/`

Source of truth:

- `state/tasks/2026-08-12-orchestrator-trusted-input-builder/TASK_PACKET.md`
- prior blocker report `state/tasks/2026-08-12-orchestrator-trusted-input-builder/CLAUDE_FINAL_CLOSURE.md`
- accepted policy contracts under `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`

Targeted questions:

1. Is every carried `prior_attempts` record schema-valid and complete across attempts 2 and 3?
2. Can an attempt-1 blocking finding flow through attempt-2 targeted verification, become `resolved_verified`, then reach a bounded attempt-3 review-only final-full decision without a third Codex launch?
3. Are finding registry, counters, nonces, decision digests, and prior finding evidence preserved rather than reset?
4. Does any malformed/missing state fail closed?
5. Do the new tests materially exercise these paths?

Run read-only checks if available. Do not edit files. Separate Standards and Spec findings. End with exactly one token on its own line: `TRUSTED_BUILDER_REWORK_TARGETED_PASS` or `TRUSTED_BUILDER_REWORK_TARGETED_REWORK`.
