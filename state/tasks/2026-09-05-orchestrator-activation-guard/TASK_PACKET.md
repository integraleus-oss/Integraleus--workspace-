# Orchestrator activation guard

Status: BLOCKED_ON_FRESH_OWNER_RETRY
Owner: Stanislav Pavlovskiy / agent main
Started: 2026-09-05T08:19:00+03:00
Execution mechanism: activation completed in foreground-controlled exec session `90986`; Gateway restart recovery resumed the interrupted source session. No detached work is running now.
Expected output: activated commit `f70913ea`, protected runtime, verified restart/recovery delivery, and a regression guard that forbids unsupported `RUNNING` claims.

## Goal

Finish the previously approved controlled activation and prevent a final reply from claiming continued execution unless durable and live execution proofs exist.

## Boundaries

- Allowed: scoped orchestrator files from commit `f70913ea`, OpenClaw managed-worker configuration, protected runtime installation, task evidence, tests and live drill state.
- Forbidden: unrelated dirty-worktree files, Synology, external/customer sends, secrets, Alpha.BPR application changes.
- Deployment approval: granted by Stanislav in Telegram topic 2922 on 2026-09-04 and reaffirmed on 2026-09-05.
- Commit rule: only scoped orchestrator changes; do not include unrelated dirty files.

## Checklist

- [x] Durable task artifacts created.
- [ ] Managed job created from a fresh authenticated owner message, with owner context, timeout, failure mode, notification target and disable path.
- [x] Live-process proof recorded before any `RUNNING` claim.
- [x] Pre-activation tests rerun from fixed commit.
- [x] Stable rollback target verified (`92ee5436`).
- [x] Commit `f70913ea` integrated into main without unrelated files (`6c03db78`).
- [x] Protected supervisor/runner installed outside agent-writable workspace.
- [x] managed-worker remapped to intended workspace and previous sandbox removed for clean recreation.
- [x] Gateway restarted using `openclaw gateway restart` and health checked.
- [x] Restart interrupted the active reply and source-session recovery resumed it without another owner message.
- [x] Unit/integration regression covers stale/crash notification and exactly-once recovery.
- [ ] Full live drill passes or rollback completes.
- [x] Evidence and commit/status recorded; owner-originated live dispatch remains open.

## Execution truth gate

`RUNNING` is allowed only when all of these are current: material artifact, managed job ID, live process/job proof, and heartbeat evidence inside the declared freshness window. Otherwise report `PLANNED`, `STALE`, or a terminal state.
