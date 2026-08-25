# Pilot 003 targeted orchestrator hardening

Goal: add only two low-bureaucracy safeguards learned from Pilot 003.

1. A single contract/schema repair may correct incomplete full-review `criteria_coverage` before final escalation.
2. A task packet may optionally declare an expected test count for a gate; when present, a passing command with the wrong observable count fails closed.

Boundaries:

- isolated worktree from canonical orchestrator commit `e2a755a5`;
- no mandatory criterion-to-test matrix;
- no new substantive review pass;
- expected test count remains optional;
- no project transfer, push, deploy, Gateway, systemd, or runtime configuration changes;
- preserve unrelated canonical workspace files.

Checklist:

- [x] Task packet created
- [x] Isolated tracked baseline created at `e2a755a5`; unrelated untracked paths documented
- [x] Existing repair and gate contracts mapped
- [x] Focused tests added red-first
- [x] Minimal implementation completed
- [x] Focused 4/4, integration 154 available tests, policy-core 87/87, compilation PASS
- [x] Independent review plus bounded closure follow-up completed
- [ ] Separate transfer decision requested
