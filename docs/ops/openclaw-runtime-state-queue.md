# OpenClaw Runtime State & Queue Layer MVP

Status: canonical architecture note integrated with Shared Memory policy; code
not started.

## Purpose

Use Redis as a local runtime state and queue layer for OpenClaw operations:
dedupe, short-lived locks, active run status, retry/suppression metadata, and
rate-limit bookkeeping. Redis is not agent memory and not a durable knowledge
store.

## Source of Truth

- Markdown remains the source of truth for plans, task packets, decisions,
  state notes, and human-readable checkpoints.
- Postgres remains the source of truth for durable structured application
  state when a service already uses it.
- OpenClaw Shared Memory uses Postgres + pgvector for durable semantic memory.
  Qdrant is not part of the current architecture; any Qdrant-inspired material
  may be adapted only as a policy pattern.
- Redis may be lost without losing important facts. Losing Redis can cause
  duplicated work or weaker suppression, but must not erase decisions, records,
  task packets, or evidence.

## Relationship To OpenClaw Shared Memory

The runtime-state layer must remain separate from durable agent memory:

- `autoCapture=false`: runtime observations must not become durable memory
  automatically.
- `autoRecall=true`: significant work should use approved memory recall where
  relevant, with markdown fallback when the DB/MCP path is unavailable.
- Durable memory writes stay behind the existing gate:
  `daily note / candidate -> approval -> candidate record -> promotion`.
- Shared Memory DB is not the only source of truth until a separate migration
  decision explicitly changes that status.
- Redis keys may contain stable identifiers, status buckets, timestamps,
  counters, and hashes. They must not contain raw chat text, raw memory content,
  secrets, command dumps, stack traces, or private file contents.
- Runtime-state work must not expose Shared Memory write/promote/import tools.
  Read-only recall tools are enough for this track unless a later task packet is
  explicitly approved.

## First Spike

Start with heartbeat alert suppression. It is the lowest-risk spike because it
can store only alert fingerprints and timestamps, does not need raw private
message content, and has obvious before/after value for repeated heartbeat
warnings.

Do not start with Telegram dedupe, full active-run registry, or generic queue
migration. Those remain later steps after the wrapper and operational behavior
are proven.

## Later MVP Candidates

After the heartbeat-suppression spike, consider:

1. Telegram inbound event/message dedupe.
2. Task lock / active run registry for long agent runs.

Everything else stays out of scope until a spike proves the layer simplifies
operations.

## Hard Rules

- Redis is local-only at first: bind to localhost or trusted local interface,
  with no public exposure.
- All temporary keys must have TTL.
- Store identifiers and small status metadata, not raw private content.
- Prefer hashes/sets with bounded fields over unbounded append-only logs.
- Postgres/Markdown remain source of truth.
- Runtime code must tolerate Redis unavailable: degrade to current behavior
  where practical, or fail closed for locks if concurrent execution is risky.

## Candidate Keyspace

| Function | Key pattern | Value | TTL |
| --- | --- | --- | --- |
| Telegram dedupe | `dedupe:telegram:<chat_id>:<topic_id>:<message_id>` | `1` or event id | 1-7 days |
| Generic inbound dedupe | `dedupe:event:<provider>:<event_id>` | `1` | 1-7 days |
| Task lock | `lock:task:<scope>` | owner/run id | 10-60 minutes, refreshed by owner |
| Chat/project lock | `lock:<kind>:<scope>` | owner/run id | 10-60 minutes |
| Active run | `run:<run_id>:state` | status hash | until done + 24h |
| Run heartbeat | `run:<run_id>:heartbeat` | unix timestamp | 2x expected heartbeat interval |
| Alert suppression | `alert:suppress:<kind>:<target>` | last alert metadata | rule-specific, usually 30m-24h |
| LLM account rate bookkeeping | `ratelimit:llm:<provider>:<profile>` | window counters/status | window TTL |

## Integration Audit

### Current OpenClaw Runtime Findings

- Inbound dedupe already exists, but it is process-local:
  `/usr/lib/node_modules/openclaw/dist/inbound-dedupe-RBmH1Bj7.js`.
  It uses a global singleton cache with a 20 minute TTL and an in-flight set.
  This protects against duplicate entry inside the current process, but it does
  not survive a gateway restart or coordinate across processes.
- Telegram ingress polling lives in
  `/usr/lib/node_modules/openclaw/dist/telegram-ingress-worker.runtime.js`.
  The worker polls `getUpdates`, posts each update to the parent as `type:
  "update"`, waits for `spool-ack`, then advances `lastUpdateId`. Redis dedupe
  should be placed after update identity is known and before side effects in the
  parent spool/dispatch path, not inside the raw polling loop as the first spike.
- Heartbeat run gating and alert delivery live in
  `/usr/lib/node_modules/openclaw/dist/heartbeat-runner-Df4cCdpO.js`.
  Relevant paths include busy skips, active reply run checks, visibility
  resolution, `sendDurableMessageBatch`, and `emitHeartbeatEvent`.
- Follow-up queues already exist in
  `/usr/lib/node_modules/openclaw/dist/queue-Ctw9J5BS.js`. Recent queued
  message id dedupe is also process-local with a 5 minute TTL. This is useful
  context, but the first Redis MVP should not replace this queue.
- Reply active-run state is process-local in
  `/usr/lib/node_modules/openclaw/dist/run-state-B31lb2Ak.js`. This is a good
  later candidate for an active run registry, especially for "killed run" and
  restart visibility, but it has more behavioral risk than alert suppression.
- Session write locks already exist as file locks in
  `/usr/lib/node_modules/openclaw/dist/session-write-lock-81JXiIgr.js`.
  Redis task locks should not replace those file locks in the MVP. Treat Redis
  locks as coarse operational locks for project/chat/task work, not as session
  persistence locks.
- Cron failure alerts already have persisted cooldown state in
  `/usr/lib/node_modules/openclaw/dist/server-cron-FMtfxqjb.js`, including
  `lastFailureAlertAtMs` and configurable cooldown. Redis alert suppression
  should target heartbeat and repeated operational alerts first; do not
  duplicate cron failure-alert policy.

### Local Runtime Check

- `redis-server` and `redis-cli` were not found in PATH.
- No local `:6379` listener was visible through `ss -ltnp`.
- `openclaw cron list --json` returned an empty job list at the time of audit.

Installing or enabling Redis is a separate system-change step and should be
confirmed before execution.

## Spike Shape

Add a narrow wrapper such as `runtimeState` with operations shaped like:

```text
claimOnce(key, ttlMs) -> claimed | duplicate | unavailable
getHash(key) / setHash(key, fields, ttlMs)
refreshTtl(key, ttlMs)
delete(key)
```

For the first heartbeat-suppression spike, only `claimOnce` is required. The
wrapper should normalize unavailable Redis as a typed result so callers can
choose between current behavior and fail-closed behavior.

Candidate suppression key:

```text
alert:suppress:heartbeat:<agent_id>:<channel>:<target_hash>:<fingerprint_hash>
```

Candidate fingerprint inputs:

- alert kind, for example `codex-account-limit`, `gateway-telegram-conflict`,
  `garden-ssh-timeout`;
- stable target, for example account id, host, session key, or cron job id;
- severity bucket;
- normalized short reason.

Do not include raw chat text, command output, tokens, stack traces, or private
file paths in the key or value.

## Acceptance Checks

- Local Redis is not reachable from public interfaces.
- New wrapper has a single narrow API such as `runtimeState`.
- Every key written by the wrapper has a TTL.
- Redis outage behavior is documented and tested manually or with a focused
  unit test.
- One real operational path uses the wrapper.
- No raw Telegram body, private file content, token, or secret is stored.
- Repeated equivalent heartbeat alerts are suppressed within the configured TTL.
- A changed alert fingerprint is still delivered.
- Redis unavailable falls back to current heartbeat behavior and logs a concise
  diagnostic.

## Shared Memory Health Checks

If a runtime-state task relies on durable memory recall or policy lookup, check
the existing OpenClaw Shared Memory path before making code changes:

- Postgres is reachable only on the approved local/LAN boundary.
- `pgvector` extension is installed and usable.
- The read-only MCP surface exposes exactly the approved recall tools needed for
  this track: `search_memory`, `get_with_audit`, and `list_candidates`.
- A scoped semantic search returns an expected approved or smoke record.
- Audit retrieval works for the returned record.
- Candidate listing respects status/privacy filters.
- Write, promote, import, delete, and migration tools remain unexposed unless a
  separate approval explicitly changes that boundary.

## Open Questions

- Exact OpenClaw source package path to patch if working from source instead of
  the installed `/usr/lib/node_modules/openclaw` bundle.
- Whether Redis should be installed as a local system service, container, or
  OpenClaw-managed optional dependency.
- Whether alert-suppression fingerprints should live in core heartbeat code or
  in the local heartbeat script/check layer first.
- Whether `agent-workflow-v2` needs a small Skill Workshop update after the
  heartbeat-suppression spike, or whether the current live skill already covers
  the memory gates well enough.
