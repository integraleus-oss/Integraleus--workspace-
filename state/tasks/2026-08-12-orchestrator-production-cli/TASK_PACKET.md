# Production CLI for bounded orchestrator

Status: CANARY_ACCEPTED_AWAITING_SCOPED_COMMIT
Risk: MEDIUM
Owner: main agent
Date: 2026-08-12

## Goal

Add one local command-line entrypoint that consumes an explicit task packet and
runs the already accepted bounded Codex -> Claude -> deterministic policy cycle.

## Boundaries

Allowed:

- `state/tasks/2026-08-12-orchestrator-integration/` CLI code and tests;
- this task directory;
- local isolated fixtures and test processes.

Forbidden:

- automatic commit, push, deploy, Gateway/config/systemd/cron changes;
- secrets or `.env` access;
- Synology writes;
- arbitrary shell commands or caller-selected executable paths;
- more than two Codex attempts or one REWORK transition.

## Source of truth

- commit `1da5c7c`;
- `managed_one_cycle.py`, `agent_launcher.py`, `live_review_cycle.py`, and
  `managed_policy_review.py`;
- user approval in Telegram message `2815`.

## Input contract

- JSON task packet with explicit project root, task note, run root, timeouts,
  and one review prompt/bundle pair per possible attempt;
- all referenced files must be regular files below the packet directory;
- run root must be new and must not be inside the project tree.

## Checklist

- [x] Artifact/task packet created.
- [x] Implement strict packet validation and CLI entrypoint.
- [x] Connect fixed-argv Codex launch and live Claude policy admission.
- [x] Add success and fail-closed tests.
- [x] Run integration/core/syntax/whitespace checks.
- [x] Independent two-axis review.
- [x] Canary on a small real task in a separate worktree.
- [ ] Scoped local commit after all gates.

## Acceptance criteria

- one command produces durable `cycle-result.json`;
- malformed paths/packet, launch failure, bad review JSON, digest mismatch,
  repeated REWORK, or exceptions cannot produce `ACCEPTED`;
- rework text comes only from admitted deterministic policy output;
- no automatic VCS, deploy, runtime, network-service, or Synology mutation.

## Blocker behavior

Fail closed to a non-zero CLI exit and preserve a terminal audit artifact where
the accepted controller contract permits it. Do not weaken validation to make a
trial pass.

## Commit rule

No commit until tests, independent review, and canary pass. Never push.
