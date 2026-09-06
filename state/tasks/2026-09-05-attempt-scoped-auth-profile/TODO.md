# Attempt-scoped auth profile repair

- Owner: main
- Started: 2026-09-05 20:57 Europe/Moscow
- Mechanism: foreground Codex turn
- Expected output: OpenClaw source patch, regression tests, verification evidence, scoped commit
- Restart: only after tests/build and installation; one managed restart maximum

## Checklist

- [x] Identify every persistence path for automatically selected auth profiles
- [x] Make automatic selection attempt-scoped; preserve explicit user overrides
- [x] Re-evaluate blocked/cooldown profiles before every new and follow-up turn
- [x] Add regression tests for stale auto profile and explicit manual profile
- [x] Run focused tests, typecheck, lint, build, and independent review
- [x] Commit scoped patch
- [ ] Install and verify live routing

## Acceptance

- Automatic failover never becomes a sticky session override.
- A blocked automatic profile is not reused on a later turn when a healthy profile exists.
- Explicit user-selected profiles remain sticky.
- No unrelated dirty-worktree changes enter the commit.
