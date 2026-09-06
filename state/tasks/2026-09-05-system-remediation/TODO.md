# System remediation

- Owner: main
- Started: 2026-09-05T20:15:00+03:00
- Mechanism: foreground Codex turn
- Expected output: verified queue-health fix, archived historical ingress cleanup, and evidence-backed hardening status

## Checklist

- [ ] Exclude completed delivery tombstones from failed queue health
- [ ] Add regression tests and run focused suite
- [ ] Remove only the 20 already-backed-up historical ingress dead letters
- [ ] Verify queue health, Gateway, Telegram, and database integrity
- [ ] Audit SecretRef migration feasibility without exposing values
- [ ] Reconcile remaining task/documentation warnings
- [ ] Record evidence and commit scoped changes
