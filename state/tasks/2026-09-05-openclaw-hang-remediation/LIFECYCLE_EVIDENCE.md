# Codex app-server lifecycle remediation evidence

Date: 2026-09-05
Owner: `main`
State: `SUCCEEDED`

## Changes

- Source checkout: `/home/stanislav/work/openclaw-remediation`
- Commit: `c611e20f1ad73242d7f0adcc2cac9baa59b2f45e`
- Unsuccessful, aborted, superseded, and timed-out Codex attempts now retire their
  exact shared app-server client after releasing their own lease.
- Existing sibling leases are not interrupted. The physical process tree closes
  after the last sibling lease is released.
- Heartbeat now runs `scripts/openclaw-codex-process-watch.sh`; it reports parent
  count and Gateway cgroup memory but never kills processes automatically.

## Verification

- `run-attempt.test.ts`: PASS, 179/179.
- Shared-client, cleanup, and restart-drain focused suites: PASS, 145/145.
- Extension source and test typechecks: PASS.
- Oxlint, oxfmt check, and `git diff --check`: PASS.
- Full `pnpm build:package`: PASS.
- `check:changed`: unavailable because the local Crabbox binary failed its own
  sanity check; focused lint, typecheck, tests, and package build were run instead.
- Source checkout clean after commit.

## Installation and activation

- Built `dist` installed atomically over the previous custom build.
- Previous dist retained at `/usr/lib/node_modules/openclaw/dist.b7e52a6e.backup`.
- CLI before restart: `OpenClaw 2026.9.1 (c611e20)`; config validation PASS.
- One effective Gateway restart completed at 18:07:06–18:07:20 MSK.
- Loaded Gateway PID: `4067715`.
- Post-start deep status: Gateway reachable, event loop healthy, Telegram 2/2 OK.
- The activation unit's immediate health probe recorded `ECONNREFUSED` because it
  tested the socket before readiness; the independent retry after readiness PASS.
- No restart-drain retry loop appeared in the activation journal.

## Remaining observations

- The three pre-patch app-server groups from 18:07 were proven orphaned after
  later turns had different process groups and were terminated gracefully.
- `Codex settled-turn finalization context is unavailable` is a transcript
  recovery/fallback condition, not process ownership evidence. No source change
  was made on that incorrect hypothesis.
- The original cgroup `MemoryCurrent` warning was dominated by about 6.3 GB of
  reclaimable file cache from the package build. The monitor now reports
  anonymous memory and file cache separately and warns on anonymous memory only.
- App-server alerts are age-based (15 minutes) rather than raw concurrent count,
  preventing normal overlapping/recovered turns from being labelled orphans.
- The disabled/inactive system-scope duplicate unit was archived as
  `/etc/systemd/system/openclaw-gateway.service.disabled-20260905`; the live
  user unit remained PID `4067715` throughout this cleanup.
- Doctor no longer reports the duplicate unit, missing pnpm PATH, unsafe backup
  mode, bare model declarations, missing Skill Workshop access, or missing
  plugin capability consent. The memory-core cron now has `agentId=main`.
- Security audit improved from one critical finding to zero critical findings;
  the local Ollama model has web and browser tools denied.
- Final activation completed at 19:01:28 MSK. The readiness loop passed on
  attempt 3; Gateway PID `211254`, Telegram 2/2 OK, event loop healthy.
- Post-restart cgroup memory returned to about 0.8-1.0 GB with negligible file
  cache, confirming that the earlier 6.3 GB was build cache rather than a leak.
- Startup orphan cleanup logged one conservative refusal for PID `211098`
  because it was still registered during the startup race. The PID was already
  absent on the independent follow-up check; no manual kill was required.
- Historical dead letters (outbound 115, Telegram inbound 20) were not deleted;
  deletion is unrelated and potentially destructive.
