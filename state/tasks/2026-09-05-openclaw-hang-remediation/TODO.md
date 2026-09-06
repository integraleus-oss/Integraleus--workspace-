# OpenClaw hang remediation

- Owner: main
- Started: 2026-09-05T11:09:15+03:00
- Execution: foreground implementation; one external final restart only
- Expected output: transactional updater, shutdown/recovery safeguards, focused tests, live verification

## Scope

- [x] Audit source and dirty-worktree boundary
- [x] Build transactional external updater with guaranteed recovery
- [x] Stop follow-up retry churn during Gateway drain (`b7e52a6e`)
- [x] Verify current restart recovery/deduplication boundaries (338/338 focused tests)
- [x] Verify current fallback/context guards; no additional patch required
- [x] Re-run skill diagnostics; no invalid skills remain. Grant required
  Skill Workshop visibility to `local` and `managed-worker`.
- [x] Assign the managed memory-core promotion cron explicitly to agent `main`.
- [x] Inspect dead letters without destructive removal
- [x] Run focused tests and static checks
- [x] Perform one managed final Gateway restart
- [x] Verify version, service, event loop, Telegram and logs
- [x] Record evidence and commit boundary

## Safety

- Do not expose secrets.
- Preserve unrelated worktree changes.
- Do not delete dead letters; quarantine/archive only if evidence requires it.
- No intermediate Gateway restarts.

## Resumed lifecycle closure (2026-09-05T17:55+03:00)

- Owner: `main`
- Execution: foreground source patch and tests; no background job
- Current target: retire unsuccessful/aborted Codex app-server clients after the
  attempt lease is released, then prove physical process-tree exit.
- Activation: exactly one managed Gateway restart after all checks pass.
- [x] Lifecycle patch committed as `c611e20f`.
- [x] Regression suites, typechecks, lint, and package build passed.
- [x] Read-only heartbeat app-server/RSS monitor installed.
- [x] Custom build installed and activated with one effective Gateway restart.
- [x] Gateway, event loop, and Telegram 2/2 verified after readiness.
- [x] Final evidence: `LIFECYCLE_EVIDENCE.md`.
- [x] Remove three proven pre-patch orphan app-server process groups.
- [x] Correct the heartbeat monitor to distinguish anonymous memory from
  reclaimable build file cache and to alert only on old app-server parents.
- [x] Archive the disabled duplicate system-scope Gateway unit; keep the
  working user-scope unit unchanged and live.
- [x] Repair the user-unit PATH and backup permissions.
- [x] Normalize per-agent model fallback declarations and accept the declared
  execution-supervisor capability set.
- [x] Remove the critical small-model web exposure finding.
- [x] Activate the final config/service-definition changes with one restart
  and verify readiness.
