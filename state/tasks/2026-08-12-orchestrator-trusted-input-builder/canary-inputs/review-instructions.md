# Independent closure review: automatic trusted review-input builder

Review the uncommitted scoped changes against `TASK_PACKET.md` on two axes:

1. Standards: security, fail-closed behavior, provenance, TOCTOU, Git edge
   cases, subprocess safety, immutable evidence, test quality, compatibility.
2. Spec: whether the builder actually derives manifest/binding/evidence from
   observed Codex changes and gates and safely connects them to production CLI.

Allowed read-only scope:

- `state/tasks/2026-08-12-orchestrator-integration/trusted_review_builder.py`
- `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_trusted_review_builder.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-trusted-input-builder/`
- relevant accepted core contracts under
  `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`

Do not edit files. Report concrete findings with severity and location. End with
exactly one verdict token: `TRUSTED_BUILDER_PASS` or `TRUSTED_BUILDER_REWORK`.
