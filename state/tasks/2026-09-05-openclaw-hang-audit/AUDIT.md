# Аудит зависаний OpenClaw — 2026-09-05

Owner: main
Start: 2026-09-05T11:03:19+03:00
Execution: foreground diagnostic audit in current Telegram session
Expected output: evidence-backed root-cause report; no remediation changes

## Checklist

- [x] Reconstruct gateway restart and interruption timeline
- [x] Inspect service journal and OpenClaw logs for hangs/timeouts/errors
- [x] Inspect session/tool delivery failures and supervisor state
- [x] Separate confirmed causes from contributing factors
- [x] Record recommendations and verification boundaries

## Verdict

The repeated apparent hangs were primarily self-inflicted by an unsafe update
workflow and then amplified by restart recovery. They were not caused by CPU,
RAM exhaustion, Telegram connectivity, or a currently hung Gateway.

## Confirmed causes

### 1. Unsafe stop-first update script left Gateway offline

`run-update.sh` executes `openclaw gateway stop` before the package update and
uses `set -euo pipefail`, but has no EXIT trap or guaranteed restart path.
Gateway stopped cleanly at 10:27:07 and did not start again until 10:52:20: an
outage of 25m13s. Once the controlling Telegram session was stopped, it could
not complete or report the remaining work.

### 2. Repeated restarts killed active Codex turns

Restarts at 10:22, 10:53, and 10:58 closed the Codex app-server before active
turns completed. The logs explicitly record `codex app-server client closed
before turn completed`. Restart recovery then replayed/resumed the same main
session, producing repeated status messages and stale conversational context.

### 3. Shutdown retry loop prevented clean termination

At 10:58:34 the Gateway entered drain mode. A queued follow-up retried every
~500 ms while admission was closed (`GatewayDrainingError`), 58 times. The
process failed to exit within systemd's 30-second stop timeout and was killed
with SIGKILL at 10:59:04. This is a product defect in shutdown/follow-up drain
coordination, not normal model latency.

### 4. Update introduced two temporary startup blockers

At 10:55 the new binary required the `audit-events-v2` SQLite migration and
rejected two obsolete MCP config keys (`connectTimeout`, `timeout`). The first
startup failed with status 78/CONFIG. These blockers extended downtime but are
now cleared.

### 5. Fallback could not handle the recovered session

After Codex was closed at 10:53, fallback to `ollama/phi3:instruct` failed
preflight: estimated prompt 296,171 tokens versus a 111,072-token budget.
Thus fallback existed nominally but was unusable for this large recovered
session.

### 6. New inbound messages cancelled still-active response turns

Telegram delivery itself succeeded for messages 3073-3076. The local tool
calls were then reported as aborted when subsequent inbound messages arrived.
This explains the rapid repeated replies after recovery: it was cancellation
and queued-turn churn, not a failed Telegram send.

## Contributing conditions (not primary causes)

- Main `AGENTS.md` is 25,492 chars and is truncated to 19,183 chars; this adds
  prompt weight and can omit late instructions, but did not stop the Gateway.
- Two invalid skills are skipped at startup.
- `memory-core` repeatedly reports an agent-less cron job; noisy but not the
  cause of the observed hangs.
- Delivery queue contains old dead letters (115 outbound, 20 inbound); current
  Telegram probes are healthy.
- Swap is 3.8/4.0 GiB used, but 46 GiB RAM is available and the current event
  loop is healthy; no evidence of resource starvation during this incident.

## Current state

- OpenClaw 2026.9.1; Gateway active since 11:01:00, PID 1427460.
- Event loop healthy; Telegram accounts 2/2 OK.
- 0 active, 0 queued, 0 running tasks.
- No current hang was observed during the audit.

## Recommended remediation order

1. Replace stop-first update scripts with one externally managed transactional
   updater: durable log, failure trap, guaranteed Gateway restart, timeout, and
   one final health check.
2. Never restart Gateway from the same foreground session whose completion is
   being reported; acknowledge first, then use the managed updater.
3. Fix the follow-up queue drain loop so it stops retrying when admission is
   closed and cannot block process shutdown.
4. Prevent automatic fallback to a model whose context budget cannot hold the
   recovered session; compact or start a fresh recovery turn first.
5. Reduce/split `AGENTS.md`, fix invalid skills, resolve the agent-less cron
   owner, and inspect old dead letters as separate maintenance.

## Boundaries

Read-only diagnostics only. No service, config, cron, session, queue, or code
remediation was performed. The audit artifact itself is untracked; the wider
worktree contains unrelated user changes.
