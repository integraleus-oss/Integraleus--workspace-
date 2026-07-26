# OpenClaw Runtime State & Queue Layer MVP

Status: compact task packet; canonical ops doc updated; code not started.

## Goal

Design a narrow Redis-backed runtime state layer for OpenClaw tasks. Redis is
temporary operational state only: not agent memory and not a source of truth.

Canonical architecture note:
`docs/ops/openclaw-runtime-state-queue.md`

## Checklist

- [x] Create task artifact.
- [x] Audit current OpenClaw integration points.
- [x] Define MVP boundaries and explicit prohibitions.
- [x] Design Redis keyspace and TTL rules.
- [x] Pick one spike target.
- [x] Define acceptance checks for spike.
- [x] Integrate OpenClaw Shared Memory policy boundaries into this plan.
- [x] Draft Shared Memory health-check requirements for runtime-state work.
- [ ] Make executable health-check/smoke.
- [ ] Decide whether `agent-workflow-v2` needs a Skill Workshop update proposal
      after the runtime-state spike is clearer.
- [ ] Decide after spike whether to expand to locks and active runs.

## Next Increment

First spike: heartbeat alert suppression.

Why first:

- low sensitivity;
- clear user-visible value;
- can store only fingerprints and timestamps;
- does not disturb existing inbound dedupe, queues, cron cooldown, or file
  locks.

Later MVP candidates:

- Telegram inbound event/message dedupe.
- Task lock / active run registry for long agent runs.

## Boundaries

- Long-term agent memory.
- Replacing Markdown or Postgres sources of truth.
- Replacing OpenClaw Shared Memory Postgres/pgvector with Qdrant.
- Making Shared Memory DB the only source of truth without a separate approved
  migration decision.
- Auto-capturing memory without Memory Candidate / approval / promotion gates.
- Queueing all OpenClaw work in the first iteration.
- Storing raw private message bodies or sensitive file contents.
- Exposing Redis outside local trusted hosts.

## Current Audit Notes

- OpenClaw already has process-local inbound dedupe in
  `/usr/lib/node_modules/openclaw/dist/inbound-dedupe-RBmH1Bj7.js`.
- Telegram polling runs through
  `/usr/lib/node_modules/openclaw/dist/telegram-ingress-worker.runtime.js`,
  which spools `getUpdates` results to the parent process.
- Heartbeat scheduling and visible alert delivery live in
  `/usr/lib/node_modules/openclaw/dist/heartbeat-runner-Df4cCdpO.js`.
- Follow-up queues already dedupe recent message ids in process-local state in
  `/usr/lib/node_modules/openclaw/dist/queue-Ctw9J5BS.js`.
- Reply run registry is process-local in
  `/usr/lib/node_modules/openclaw/dist/run-state-B31lb2Ak.js`.
- Session write locking already uses file locks in
  `/usr/lib/node_modules/openclaw/dist/session-write-lock-81JXiIgr.js`.
- Cron failure alerts already have persisted cooldown fields in
  `/usr/lib/node_modules/openclaw/dist/server-cron-FMtfxqjb.js`.
- `redis-server` and `redis-cli` were not found in PATH, and no local listener
  on `:6379` was visible during the read-only check.
