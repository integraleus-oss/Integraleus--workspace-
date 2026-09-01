# Task Packet: Global execution-truth gates

Status: complete
Risk: MEDIUM
Owner: main agent
Date: 2026-09-01

## Goal

- Make truthful execution status mandatory for all old, current, new, and future work.
- Audit existing `RUNNING` records and remove unsupported status claims.

## Authorization

- Stanislav Pavlovskiy, Telegram `HOME:2922`, message `4623`, 2026-09-01 15:25 MSK.

## Scope

Allowed:

- `AGENTS.md`, `DECISIONS.md`, `STATE.md`, `HEARTBEAT.md`;
- `state/tasks/**` status/evidence records;
- local scripts and tests that enforce execution-status truth.

Forbidden:

- Gateway/runtime/config changes;
- cron/systemd/daemon activation;
- external sends other than the normal reply in the source topic;
- project implementation changes, commit, push, deploy, or destructive cleanup.

## Source Of Truth

- Telegram messages `4614`-`4623` in topic `HOME:2922`.
- `AGENTS.md` Deliverable Execution Protocol.
- `skills/agent-workflow-v2/SKILL.md`.

## Plan

- [x] Create durable task packet before rule changes.
- [x] Add non-overridable execution-truth rules to `AGENTS.md`.
- [x] Record the approved decision and current state.
- [x] Audit all currently recorded `RUNNING` work.
- [x] Add automated checker/watcher and four synthetic tests.
- [x] Run checks and record evidence.

## Done Means

- [x] No unsupported `RUNNING` record remains.
- [x] Rules apply explicitly to legacy, current, queued, and future work.
- [x] Checker detects missing artifact, dead process/job, stale evidence, and terminal outcomes.
- [x] Four synthetic tests pass.
- [x] Evidence records files, commands, checks, and residual risks.
