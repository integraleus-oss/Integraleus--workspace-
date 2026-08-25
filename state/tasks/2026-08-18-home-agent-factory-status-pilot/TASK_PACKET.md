# Controlled pilot 003 — Home Agent Factory status

- Project: `/home/stanislav/projects/home-agent-factory`
- Profile: `light` (one implementation, one independent review)
- Goal: add `factory status --json` for local structural readiness.
- Allowed files: `src/cli/factory.js`, optional `src/core/status.js`, `test/status.test.js`, `README.md`.
- Forbidden: pack execution, private-data reads, adapter/OpenClaw/Gateway/systemd changes, commit, transfer, push, deploy.
- Required checks: `npm test`, CLI success/negative tests, `git diff --check`.
- Acceptance: deterministic JSON; version, pack/instance counts, policy/run-log readiness; structured error and exit 2 for malformed JSON or missing required directories.
- Transfer: separate owner decision only after ACCEPTED.

Checklist:

- [x] Task packet created
- [x] Clean isolated worktree created
- [x] Production packet validated
- [x] Light cycle executed (infra failure before edit)
- [x] Codex account limits checked before R2 (primary 5h 100%, reserve 5h 67%)
- [x] Separate R2 packet created; original failed run preserved
- [x] R2 light cycle executed (local Codex token invalidated before edit)
- [x] Local Codex reauthenticated and verified by live API probe
- [x] Separate R3 packet created; R1/R2 evidence preserved
- [x] R3 light cycle executed (52/52 gates PASS; review found 1 major, 2 nit; admission coverage error)
- [x] Separate focused R4 follow-up packet created for the concrete AC-4 test gap
- [x] R4 light follow-up executed (54/54 gates PASS; review found 2 major, 1 nit)
- [x] Owner approved separate R5 closure slice
- [x] Clean R5 worktree created at base `3b21d0d`
- [x] R5 closure packet created with R3/R4 source boundaries
- [x] R5 light closure executed
- [x] Test-harness major repaired without widening scope
- [x] Final review-only follow-up: 0 blocker, 0 major, 0 minor, 0 nit
- [x] Fixed digests and checks recorded in sealed run artifacts
- [x] Independent R4 verdict admitted: ESCALATED / R12_FINDINGS_EXHAUSTED
- [x] Owner approved transfer; accepted files transferred and committed as `f93b744`
