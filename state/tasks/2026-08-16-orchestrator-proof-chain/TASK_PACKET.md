# Task Packet: Orchestrator proof chain and controlled OpenClaw pilot adapter

Status: owner-authorized trusted-boundary implementation and pilot
Risk: HIGH
Owner: main agent
Date: 2026-08-16

## Goal

Extend the local Codex/Claude orchestrator with a machine-verifiable proof chain
from the owner's original brief through requirements, specification, tasks,
observed implementation, tests, review, and blind final acceptance. Add a
read-only dashboard and a foreground-only OpenClaw adapter, then exercise the
whole path as a controlled local pilot.

## Source Of Truth

- Stanislav's Telegram brief in topic `2922`, messages `3290` and `3293`.
- Durable pilot boundary `D-2026-08-16-05`.
- Existing sealed-evidence runtime under
  `state/tasks/2026-08-12-orchestrator-integration/`.
- `skills/agent-workflow-v2/SKILL.md`.

## Immutable Boundaries

Allowed:

- local code, schemas, fixtures, tests, task packets, evidence, and commits;
- local foreground dry-runs and controlled pilot runs;
- a static HTML dashboard generated from sealed evidence JSON;
- modes `manual + strict` and `manual + normal` only.

Forbidden without a new explicit approval:

- OpenClaw/Gateway/config/runtime changes beyond the narrowly approved
  foreground authorization plugin and its activation;
- cron, heartbeat automation, unattended execution, or background drift;
- automatic commit, accepted-diff transfer, push, deploy, or rollback;
- third-party Autopilot installation;
- external sends beyond the already approved local Codex/Claude workflow;
- unrelated files, especially the existing hozblok worktree artifacts.

## Increments

- [ ] I1: immutable requirements manifest, generator, schema, and three hard validators.
- [ ] I1: integrate validation into task-packet admission and add negative tests.
- [ ] I2: blind final acceptance packet, sealed verdict, and mismatch blocker.
- [ ] I3: static dashboard generated only from hashed evidence JSON.
- [ ] I4: enforce independent control/depth settings; pilot allowlist is manual + strict/normal.
- [ ] I5: foreground OpenClaw adapter with one packet per invocation and interrupt propagation.
- [ ] I6: run a controlled local pilot, independent review, and final readiness report.

## Hard Acceptance Criteria

1. The exact original brief is retained with a verified SHA-256 digest.
2. Requirement IDs are stable `R01..Rnn`; active requirements cannot disappear
   or change state without recorded owner disposition.
3. Every active requirement has specification coverage.
4. Every task links to at least one requirement and every implementing
   requirement is linked by at least one task.
5. Final internal and blind acceptance both report every active requirement;
   disagreement blocks `ACCEPTED`.
6. Blind acceptance receives no internal specification, task tracker, prior
   review prose, or orchestrator rationale.
7. Dashboard is display-only and verifies/labels evidence digest state.
8. Adapter rejects unsafe paths/modes and never performs commit, transfer,
   push, deploy, Gateway changes, or activation.
9. Relevant unit/integration tests and `git diff --check` pass.

## Blocker Behavior

Fail closed. Record a deterministic error/evidence artifact and stop the
current increment. Do not weaken a hard gate merely to reach `ACCEPTED`.

Current blocker: a local user-writable adapter cannot prove that its manual
authorization registry/ledger was not authored, altered, or replay-enabled by
the same agent it constrains. Closing this requires a separately approved
owner-controlled signer or trusted OpenClaw/Gateway invocation nonce. No pilot
through the adapter may run until that boundary exists.

Owner approval received in Telegram topic `2922`, message `3296`, on
2026-08-17: create a Gateway-owned one-time nonce bound to trusted inbound
metadata and the task-packet digest, finish the adapter, and run one controlled
pilot. This authorizes only that boundary, plugin activation/restart needed to
load it, and one foreground pilot. Cron, unattended execution, automatic
commit/transfer/push/deploy, and broader Gateway/config changes remain forbidden.

## Trusted Boundary Increment

- [ ] Gateway plugin captures owner/channel/conversation/thread/message/sender/run metadata before the model.
- [ ] A tool may mint exactly one opaque authorization for the same owner turn and exact packet digest.
- [ ] A Gateway RPC atomically validates and consumes the authorization.
- [ ] Authorizations are short-lived, in-memory, single-use, and invalidated by Gateway restart.
- [ ] Adapter re-hashes the packet immediately before consume and immediately before execution.
- [ ] Negative tests cover wrong owner, run, metadata, digest, expiry, replay, and restart state.
- [ ] Independent read-only review passes before activation.
- [ ] One controlled foreground pilot runs; no accepted diff is transferred automatically.

## Commit Rule

Create one scoped local commit per completed increment when the workspace is
clean apart from unrelated pre-existing files. Never stage unrelated files.

## Review

Run an independent Claude read-only review for each material code increment,
with separate Standards and Spec findings. The final pilot requires a fresh
review and a blind acceptance run.
