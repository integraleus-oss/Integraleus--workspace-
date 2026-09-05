# Attempt-scoped auth profile repair — evidence

## Source result

- Source repository: `/home/stanislav/work/openclaw-remediation`
- Commit: `ba667378 fix: scope automatic auth profiles to attempts`
- Scoped files: eight auth-profile and cron runtime/test files.
- Unrelated delivery-queue changes were excluded from the commit.

## Behavior

- Automatic auth selection is returned to the current attempt and is not persisted as a session override.
- Legacy persisted automatic overrides are cleared with compare-and-swap.
- A concurrent explicit user pin wins and remains session-scoped.
- Cooldown/blocked state is consulted on every attempt using the current attempt model id.
- Cron live selections require explicit `auto` or `user` provenance at compile time; automatic selections are not persisted.
- Returning to the first healthy configured profile after cooldown is intentional. An auth-route change invalidates the native resume fingerprint and causes a compatible reseed.

## Verification

- Regression suite: 236/236 passed (9 files).
- Focused auth/cron suite: 67/67 passed.
- Core typecheck: passed.
- Full format check: passed.
- `git diff --check`: passed.
- Full lint: passed before the final type-only cron provenance tightening; the final changed files passed targeted oxlint and core typecheck.
- Full build: passed after the final source changes. Dependency-only direct-`eval` warnings came from Playwright/tree-sitter.
- Independent Claude reviews: first two requested changes; final review approved conditional on cron source provenance. The condition was closed by making provenance mandatory in `CronLiveSelection` and updating its sole producer.

## Live activation

- Activated successfully on 2026-09-05 through the managed restart unit.
- Installed build: `OpenClaw 2026.9.1 (ba66737)` from commit `ba667378`.
- Post-restart verification: Gateway active, event loop healthy, Telegram 2/2
  connected, and the primary Codex OAuth profile selected for the fresh turn.
- The pre-install `dist` backup was retained for rollback.
