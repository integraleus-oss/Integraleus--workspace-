# Evidence: Orchestrator proof chain and controlled OpenClaw pilot adapter

Status: active
Date: 2026-08-16
Task packet: `state/tasks/2026-08-16-orchestrator-proof-chain/TASK_PACKET.md`

## Baseline

- Workspace HEAD at start: `996fb3c`.
- Existing unrelated untracked hozblok artifacts were present and are excluded.
- Durable boundary: ready for a separately approved controlled manual OpenClaw
  pilot; not activated; not ready for unattended use.

## Increment Log

### I0 — admission and artifact gate

- [x] Read `agent-workflow-v2`.
- [x] Read relevant technical rules and existing orchestrator architecture.
- [x] Created this task packet and evidence log before implementation.
- [x] `git diff --check`.
- [ ] Scoped commit (included with I1).

### I1 — immutable requirements and traceability preflight

- [x] Added strict JSON Schema for the immutable requirements manifest.
- [x] Added exact-brief and exact-requirement SHA-256 validation.
- [x] Added stable contiguous `R01..Rnn` generation.
- [x] Added explicit owner disposition for deferred/removed requirements.
- [x] Added spec completeness, bidirectional requirement/task, and acceptance completeness validators.
- [x] Added production packet `1.2.0` admission and sealed review-input copies.
- [x] Initial integration suite: 103/103 tests passed.
- [x] Initial Claude review: `REWORK` (2 blockers, 4 majors, nits).
- [x] Reworked: external brief anchor, immutable-core digest, revision chain,
  fixed R01..R99 namespace, executed JSON Schema, legacy execution block,
  stricter task/acceptance consistency, and sealed-artifact coverage.
- [x] Post-rework integration suite: 109/109 tests passed.
- [x] Python compile checks passed.
- [x] `git diff --check` passed.
- [ ] Independent closure review.
- [ ] Scoped commit.

### I2 — blind final acceptance

- [x] Blind prompt contains the exact brief, source requirement excerpts,
  observed worktree access, and verification commands.
- [x] Internal spec, task tracker, prior review prose, and orchestrator rationale are excluded.
- [x] Missing, failed, unverified, or disagreeing Rxx results block final acceptance.
- [x] Read-only launch and digest-bound verdict evidence added.

### I3/I4 — dashboard and pilot modes

- [x] Static HTML is generated only from digest-verified JSON evidence.
- [x] Evidence content is escaped and existing output cannot be overwritten.
- [x] Pilot admission permits only `manual + strict/normal`.
- [x] `automatic`, `deep`, and pre-1.3 production execution are rejected.

### I5 — foreground adapter

- [x] One packet per foreground invocation.
- [x] Approved packet-root restriction and non-blocking single-run lock.
- [x] Structured terminal status and interrupt preservation.
- [x] No activation, Gateway/config, cron, commit, transfer, push, deploy, or rollback capability.

### Current verification

- [x] Initial final review: `REWORK` (2 blockers, 10 majors).
- [x] Reworked internal acceptance to derive per-R outcomes from the sealed
  reviewer criterion coverage and explicit AC↔R mapping.
- [x] Added fixed global execution lock and explicit foreground authorization.
- [x] Blind verification commands now execute and worktree state is checked before/after.
- [x] Blind source excerpts must be exact substrings of the anchored brief.
- [x] Dashboard now covers failed managed cycles, shows actual blind gates, and
  records source/dashboard digests in final evidence.
- [x] Fixed symlink and unsafe artifact-link handling.
- [x] `strict` vs `normal` now changes admitted reviewer verification methods.
- [x] Full suite after rework: 118/118 tests passed.
- [x] First closure review: `REWORK` (7 majors, no blockers).
- [x] Bound internal per-R derivation to the admitted reviewer verdict digest.
- [x] Added single-use owner authorization bound to packet digest and source message.
- [x] Applied the fixed global lock to legacy and current executions.
- [x] Added structured internal-acceptance failure and broader interrupt evidence.
- [x] Added ignored-file mutation tracking and persisted failed blind gate records.
- [x] Second closure review: `REWORK` (2 majors, 2 major-risk findings).
- [x] Replaced filename-based authorization consumption with a fixed trusted
  registry and global content-identity ledger keyed by authorization digest,
  packet digest, and source message ID.
- [x] Added copied-authorization replay test; suite now 119/119.
- [x] Python compile checks passed.
- [x] `git diff --check` passed.
- [ ] Final independent review.
- [ ] Controlled local pilot.

## Files Created Or Changed

- `TASK_PACKET.md` — scope, gates, acceptance, and commit rules.
- `EVIDENCE.md` — persistent verification ledger.
- `requirements-manifest.schema.json` — immutable manifest JSON contract.
- `requirements_traceability.py` — generator and hard validators.
- `production_cycle_cli.py` — packet `1.2.0` proof-chain admission.
- `trusted_review_builder.py` — proof artifacts in sealed reviewer evidence.
- `tests/test_requirements_traceability.py` — positive and negative contract tests.
- `tests/test_production_cycle_cli.py` — production admission regression test.

## Residual Risks

- The current runtime has strong review-evidence integrity but no native
  original-requirements traceability yet.
- OpenClaw integration remains intentionally inactive throughout this task.
