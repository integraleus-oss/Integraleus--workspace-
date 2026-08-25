# Orchestrator Regression Pilot

Status: PILOT_004_INPUT_REQUIRED
Owner: Stanislav Pavlovskiy
Risk: MEDIUM (local tests and project audit; no deploy/runtime changes)

## Goal

1. Prove the newly transferred bounded `criteria_coverage` repair in an isolated regression run.
2. Prove `expected_test_count` rejects an incomplete TAP result.
3. Record a stop/continue verdict for orchestrator development.
4. Audit unfinished Alpha BPR Track F without changing or committing its product files.
5. Prepare, but do not start, pilot #4 until Track F is clean and separately accepted.

## Boundaries

- Source of truth: `state/tasks/2026-08-12-orchestrator-integration/` and `/home/stanislav/projects/alpha-bpr`.
- Allowed changes: this task folder only.
- Forbidden without a later explicit gate: product edits, transfer, commit, push, deploy, Gateway/systemd changes, VM/service changes.
- Preserve all unrelated dirty files.

## Acceptance checklist

- [x] Record current orchestrator commit/status and tested file digest.
- [x] Run a red-capable coverage-repair scenario and prove exactly one repair.
- [x] Run matching and mismatching TAP-count scenarios; mismatch must fail closed.
- [x] Run focused regression tests and `git diff --check`.
- [x] Write `EVIDENCE.md` and final orchestrator verdict.
- [x] Inventory Track F modified/untracked paths and existing evidence.
- [x] Run only safe read-only/focused checks needed to classify Track F.
- [x] Write `TRACK_F_AUDIT.md` with next gate for pilot #4.
- [x] Record commit/export/deploy status.

## Blocker behavior

Stop fail-closed if a regression mechanism does not reproduce deterministically, if required fixtures are missing, or if Track F requires mutation/root/runtime action. Report the exact blocker; do not repair product code silently.

## Commit rule

No commit unless separately justified after all evidence is complete. Push and deploy are out of scope.
