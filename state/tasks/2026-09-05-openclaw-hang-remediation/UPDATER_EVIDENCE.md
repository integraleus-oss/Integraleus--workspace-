# Transactional updater evidence

Date: 2026-09-05
Owner: `main/transactional_updater`
Scope: updater implementation only; no real update or Gateway restart

## Files

- `scripts/openclaw-transactional-update.sh`
- `scripts/test_openclaw_transactional_update.sh`
- `state/tasks/2026-09-05-openclaw-hang-remediation/UPDATER.md`

## Verified behavior

- Success path: config validates twice, verified backup precedes update,
  `update --no-restart` is used, and exactly one safe restart is requested.
- Failure path: no planned restart occurs after update failure; when the mock
  service becomes inactive, the EXIT trap invokes `gateway start` once and
  preserves the original failing exit code.
- Dry-run path: only validation and OpenClaw backup/update previews run; doctor,
  restart and recovery start do not run.
- Status transitions are persisted to per-run and latest status files.

## Checks

```text
bash -n scripts/openclaw-transactional-update.sh                  PASS
bash -n scripts/test_openclaw_transactional_update.sh             PASS
bash scripts/test_openclaw_transactional_update.sh                PASS
  PASS: transactional updater success, failure, and dry-run cases
git diff --check (scoped files)                                   PASS
```

The actual updater and its real `--dry-run` were deliberately not invoked in
this subtask. The parent remediation task owns the one allowed managed restart.
