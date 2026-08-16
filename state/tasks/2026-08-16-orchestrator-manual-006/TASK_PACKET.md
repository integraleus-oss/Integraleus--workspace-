# Manual-006 — model-class runtime/schema closure

Status: ACCEPTED / R17_ACCEPT; INSPECTION ONLY; NOT TRANSFERRED

## Goal

Create a fresh implementation from source `6e56761` that closes the
requested-model-class runtime and JSON Schema contract without reusing the
unaccepted `manual-005` diff.

## Fixed point and scope

- Risk: MEDIUM local code change; independent review required.
- Source: `/home/stanislav/projects/home-agent-factory`.
- Fixed commit: `6e56761030812f0387dbbe570a199b37c3088ca5`.
- Detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-006-model-class-schema`.
- Run evidence:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-006-model-class-schema-run`.
- Allowed files: `src/core/policy.js`, `test/policy.test.js`, and
  `schemas/agent-pack.schema.json`.
- Forbidden: every other source path, reuse/copy of the manual-005 diff,
  dependencies, network, source transfer, commit, push, deploy, Gateway, cron,
  systemd, daemon, unattended execution, and system changes.

## Acceptance criteria

- [ ] One exported deeply frozen grammar defines exactly `local` and `cloud`.
- [ ] Runtime selection accepts only primitive exact strings from request
  context or pack default; all other consulted values fail with controlled
  `PolicyError` before approval logic.
- [ ] Precedence remains request context, then pack default, then `local`;
  explicit valid request class short-circuits an invalid unconsulted default.
- [ ] Agent-pack schema pins `modelPolicy.default` to the exported class list,
  and an exact schema-subtree test prevents runtime/schema drift.
- [ ] One shared invalid-value corpus covers both runtime sources without
  duplicated lists; undefined-as-absent semantics are documented and tested.
- [ ] Existing approval, externalRead, immutability, and path tests remain green.
- [ ] `npm test` and `git diff --check` pass; exactly three allowed files change.

## Budgets and stop conditions

- Maximum two Codex implementations and one review-only final-full Claude leg.
- Standard single format repair and single contract-only repair.
- Gate timeout 60 seconds; agent timeout 600 seconds.
- Unknown failure, forbidden path, unresolved major, exhausted budget,
  invalid verdict, or interruption means STOP without transfer.

## Checklist

- [x] Task packet and boundaries created before autonomous work.
- [x] Clean detached worktree created at the fixed commit.
- [x] Managed production cycle completed with `R17_ACCEPT`.
- [x] Evidence, paths, tests, and source state independently verified.
- [x] Result recorded; transfer remains a separate decision.
