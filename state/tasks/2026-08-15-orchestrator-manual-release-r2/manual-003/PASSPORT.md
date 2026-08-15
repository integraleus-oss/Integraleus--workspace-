# Manual-003 — close external-read validator divergence

Status: ESCALATED; REVIEW/REPAIR EXHAUSTED; NOT TRANSFERABLE

- Source: `/home/stanislav/projects/home-agent-factory` at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- Isolated worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-003-external-read-agreement`.
- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-003-external-read-agreement-run`.
- Allowed files: `src/core/policy.js`, `test/policy.test.js`,
  `schemas/agent-pack.schema.json`.
- Every other source path is forbidden.

## Required result

- Runtime and JSON Schema accept and reject the same documented external-read
  domain forms, including an explicit decision for IPv4-embedded IPv6.
- A shared executable test corpus proves runtime/schema agreement.
- DNS names and supported IP literals are canonicalized deterministically.
- `domains` and `methods` fail closed with controlled `PolicyError` values.
- Compiled grant containers and their arrays are defensive immutable copies.
- Missing external-read fields remain backward compatible as empty arrays.

## Limits and stop conditions

- Maximum two Codex implementation attempts and one final review-only Claude
  leg, using the existing bounded-repair policy.
- Gates: `npm test` and `git diff --check`, 60 seconds each.
- Any path expansion, unknown failure, unresolved major finding, invalid final
  verdict after bounded repair, or exhausted attempt budget means STOP.
- No commit inside the target project and no source transfer, push, deploy,
  Gateway, cron, systemd, daemon, unattended, network, dependency, or system
  changes.
- `R17_ACCEPT` authorizes inspection only. Transfer requires a separate
  explicit decision.

## Checklist

- [x] Passport and boundaries recorded.
- [x] Clean detached worktree created from the exact source commit.
- [x] Managed implementation/review cycle completed.
- [x] Independent tests and changed-path audit completed.
- [x] Result and transfer recommendation recorded.
