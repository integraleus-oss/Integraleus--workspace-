# Task Packet: Orchestrator proof chain and controlled OpenClaw pilot adapter

Status: FROZEN RESEARCH PROTOTYPE; installation no longer required for manual use
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

### Two-phase closure

- [x] PREPARE and RUN are separate fresh owner messages.
- [x] PREPARE snapshots the bounded packet directory using descriptor-relative
  no-follow reads, file/depth/byte limits, and a whole-tree digest.
- [x] RUN accepts no packet path and consumes only the prepared snapshot id
  whose digest appears verbatim in the owner command.
- [x] Snapshot files are root-owned and group-readable by the demoted runner.
- [x] Replay is consumed atomically before snapshot side effects.
- [x] Timeout terminates the complete runner process group.
- [x] Python guard review: ACCEPT, 0 blocker / 0 major.
- [ ] Combined plugin/systemd review: REJECT, 1 blocker / 3 major.
- [ ] Root install and controlled pilot.

Current blocker: the Gateway and model-spawned commands both run as
`stanislav` inside `openclaw-gateway.service`. Unix socket permissions and the
current `/proc` peer check therefore cannot distinguish them. A real boundary
requires a distinct, non-assumable OS/LSM identity for the trusted Gateway side
and separate execution identity for model tools. That is a broader OpenClaw
runtime isolation change and is not installed or assumed by this packet.

Owner disposition, Telegram message `3321` on 2026-08-17: the machine is local
to the home network and accessible only by Stanislav, so the administrator and
current OpenClaw are trusted for controlled manual use. OS-level authorization
is deferred unless external/multi-user access, unattended operation, or
automatic high-impact actions are introduced.

## Commit Rule

Create one scoped local commit per completed increment when the workspace is
clean apart from unrelated pre-existing files. Never stage unrelated files.

## Review

Run an independent Claude read-only review for each material code increment,
with separate Standards and Spec findings. The final pilot requires a fresh
review and a blind acceptance run.
