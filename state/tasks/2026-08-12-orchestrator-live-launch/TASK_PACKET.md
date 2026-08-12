# Orchestrator live-launch slice

Status: COMPLETED
Owner: Stanislav
Risk: MEDIUM — local code and bounded external model calls
Baseline: `9f00f70`; decision record `b707d78`

## Goal

Connect the accepted local orchestrator runner to the existing local Codex and
Claude wrappers, preserve complete run evidence, feed reviewer output through
the trusted projection and deterministic policy, and prove one bounded dry run.

## Boundaries

Allowed:

- this task folder;
- `state/tasks/2026-08-12-orchestrator-integration/` implementation and tests;
- existing Claude wrappers under `/home/stanislav/agent-runs/_bin/` and
  `scripts/codex-local-run.sh` as read-only dependencies.

Forbidden:

- Gateway, OpenClaw config, systemd, cron, unattended activation;
- GitHub or push;
- Synology changes or copying Synology data;
- unrelated dirty-worktree files;
- secrets, `.env`, private chats, or raw Synology data in model prompts.

## Checklist

- [x] Create task packet before implementation.
- [x] Inventory runner contracts and wrapper behavior.
- [x] Add deterministic launch adapter and prompt/input construction.
- [x] Persist stdout, stderr, exit status, command metadata, manifest, and digests.
- [x] Validate/project Claude verdict and run deterministic state transition.
- [x] Add unit/integration tests including failures and budget limits.
- [x] Run bounded dry run on synthetic, non-private fixture.
- [x] Record evidence and residual risks.
- [x] Independent closure review (returned `LIVE_LAUNCH_REWORK`).
- [x] Fresh targeted closure after rework (`TARGETED_PASS`).
- [x] Scoped local commit after gates pass.

## Acceptance criteria

- No shell-string execution from task content; argv is fixed/allowlisted.
- Each invocation uses a single-use run directory and immutable input snapshot.
- Timeout/nonzero/malformed output fails closed and remains auditable.
- Reviewer findings cannot be silently dropped or reduced in severity.
- The dry run demonstrates a deterministic terminal/intermediate decision.
- Existing 14 integration and 84 core tests remain green.

## Blocker behavior

Known allowlisted tool/auth/capacity failures may map to `FAILED_INFRA` only
within the accepted policy. Unknown or repeated failures must become
`ESCALATED`. No acceptance is inferred from missing output.

## Commit rule

Do not commit until tests and independent closure review pass. Commit only the
new slice and its intentional integration files; leave unrelated changes alone.
