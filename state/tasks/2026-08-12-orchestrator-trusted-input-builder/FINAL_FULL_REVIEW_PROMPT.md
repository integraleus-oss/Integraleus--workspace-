# Final full closure review

Perform an independent final-full Standards + Spec review of the complete current uncommitted trusted-input-builder slice.

Review scope:

- `state/tasks/2026-08-12-orchestrator-trusted-input-builder/TASK_PACKET.md`
- all review/evidence files in that task folder, especially `CLAUDE_FINAL_CLOSURE.md`, `TARGETED_REWORK_REVIEW.md`, and `TARGETED_REWORK_R2_REVIEW.md`
- current diffs for:
  - `state/tasks/2026-08-12-orchestrator-integration/trusted_review_builder.py`
  - `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
  - `state/tasks/2026-08-12-orchestrator-integration/local_orchestrator_runner.py`
  - `state/tasks/2026-08-12-orchestrator-integration/managed_one_cycle.py`
  - corresponding changed tests
- accepted core policy/contracts under `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`

Acceptance focus:

1. Observed Git changes and required gates are provenance-bound and fail closed.
2. Generated manifest/binding/evidence/policy inputs actually reach contract validation, trusted projection, deterministic policy, and admission.
3. The bounded lifecycle supports:
   - correct first Codex attempt -> review-only final-full -> `R17_ACCEPT`;
   - first review blocking finding -> one Codex rework -> targeted verification -> review-only final-full -> `R17_ACCEPT`;
   - no third Codex implementation attempt.
4. Prior decisions, counters, nonces, registry, prior findings, and digests are not reset or accepted unauthenticated.
5. Unknown, malformed, stale, mutated, out-of-scope, or exhausted cases stop closed.

Do not edit files. Separate blocker/major/minor findings and Standards/Spec. Treat test counts as independently reported unless you can run them. End with exactly one token on its own line: `TRUSTED_BUILDER_FINAL_FULL_PASS` or `TRUSTED_BUILDER_FINAL_FULL_REWORK`.
