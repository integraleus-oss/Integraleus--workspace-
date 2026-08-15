# Manual-001 — fail-closed external-read domain validation

Status: PREPARED; NOT STARTED

- Source repository: `/home/stanislav/projects/home-agent-factory`.
- Exact source commit: `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- Detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-001-external-domains`.
- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-001-external-domains-run`.
- Allowed files: `src/core/policy.js`, `test/policy.test.js`.
- Forbidden: every other project file; dependencies; source-repository edits;
  commit, merge, push, deploy, network, Gateway, cron, systemd, daemon, and
  external/system state.

## Required result

`externalRead.domains` must fail closed with a controlled `PolicyError` when it
is not an array or contains invalid/non-string domain entries. A valid array of
domain names must retain existing grant behavior. Tests must cover valid and
invalid shapes without network access.

## Gates and budgets

- `npm test` — timeout 60 seconds.
- `git diff --check` — timeout 60 seconds.
- Codex implementation attempts: maximum 2, 600 seconds each.
- Claude final/full review: maximum 1 review-only leg, 600 seconds.
- Reviewer repair and infrastructure handling remain bounded by policy.

## Stop conditions

Stop without continuation on any path-scope breach, unknown/repeated failure,
missing or invalid evidence, seal/digest mismatch, operator interruption,
timeout, need for a dependency, source-project change, commit/push/deploy need,
or any OpenClaw/system integration requirement.

`ACCEPTED / R17_ACCEPT` will authorize only inspection of the isolated diff. It
will not authorize transfer or commit into the source repository.
