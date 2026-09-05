# Ordered system hardening

- Owner: main
- Started: 2026-09-05T22:15:00+03:00
- Mechanism: foreground Codex turn
- Expected output: heartbeat repair, corrected evidence, archived ingress cleanup, SecretRef migration, and scoped hardening commits

## Boundaries

- Do not replay inbound dead letters.
- Preserve outbound deduplication fences.
- Never print or commit secret values.
- Keep unrelated dirty-worktree changes out of scoped commits.
- Restart Gateway only when required, once per activation stage, with post-restart verification.

## Checklist

- [x] Identify and repair the exact `heartbeat-main` hang step; add bounded execution proof
- [x] Correct stale `ba667378` activation evidence
- [x] Archive/remove only the 20 already-backed-up inbound timeout records without replay; verify SQLite
- [ ] Migrate plaintext configuration secrets to SecretRefs; verify Gateway and Telegram
- [x] Re-run doctor/security checks and classify remaining hardening findings
- [ ] Create scoped commits and record final evidence
