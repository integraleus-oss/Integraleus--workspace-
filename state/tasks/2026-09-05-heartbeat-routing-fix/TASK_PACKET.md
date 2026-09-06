# Heartbeat routing fix

- Owner: Stanislav / main agent
- Started: 2026-09-05 09:56 MSK
- Status: SUCCEEDED
- Execution: foreground Codex session in Telegram topic 2922
- Goal: prevent host-health heartbeat checks from running in a sandbox-only managed worker and reporting sandbox limitations as host failures.
- Source of truth: OpenClaw agent/runtime configuration plus `HEARTBEAT.md` and workspace scripts.
- Allowed scope: heartbeat routing/configuration, heartbeat diagnostics, focused tests and evidence.
- Forbidden scope: unrelated dirty files, destructive cleanup, Synology changes, unrelated gateway/model/auth changes.

## Checklist

- [x] Capture reported sandbox false-positive as the regression case.
- [x] Identify the heartbeat execution route and responsible configuration/code.
- [x] Add a deterministic configuration guard: `managed-worker.heartbeat.every = 0m`.
- [x] Apply the smallest scoped fix.
- [x] Run focused tests and one host-backed heartbeat command smoke check.
- [x] Record changed files, verification, runtime state, and commit boundary in `EVIDENCE.md`.

## Acceptance criteria

1. A heartbeat that performs host checks runs in the host-capable main context; `managed-worker` cannot schedule its own heartbeat.
2. Sandbox-only execution cannot record missing host CLI/modules as a host regression.
3. Existing supervisor behavior remains green.
4. No unrelated dirty-worktree changes are overwritten or committed.

## Completion

- Completed: 2026-09-05 10:08 MSK
- Result: main heartbeat scheduler is enabled at 1h; managed-worker heartbeat scheduler is disabled at 0m; post-restart health and host-capable diagnostics pass.
- Commit: none; runtime configuration is outside the repository and the repository was already dirty with unrelated work.
