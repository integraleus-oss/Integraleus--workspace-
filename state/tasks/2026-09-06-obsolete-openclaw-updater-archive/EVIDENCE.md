# Obsolete OpenClaw updater archive evidence

Status: SUCCEEDED
Completed: 2026-09-06 13:27 MSK

## Validation

- Exact manifest: archive `TARGETS.txt`, 3 paths.
- All three sources existed as regular non-symlink files.
- Shell syntax for both historical scripts: PASS before and after archival.
- Credential-assignment scan: 3 files scanned, 0 candidates.

## Replacement proof

- Replacement commit: `d8ff5c0b` (`feat: add transactional OpenClaw updater`).
- Regression test repeated: success/failure/dry-run cases PASS.
- Live `--dry-run --timeout 120`: PASS.
- Config validation: PASS.
- Backup dry-run: PASS; no archive written by OpenClaw dry-run.
- Update dry-run: current and target version `2026.9.2`, status `skipped`
  because versions match, restart false.
- No real update, doctor repair, Gateway restart, or service stop/start.

## Archive proof

- Archive root:
  `/home/stanislav/.openclaw/backups/workspace-repo-cleanup-2026-09-06T1148/obsolete-openclaw-update`
- Archive size: about 36 KiB.
- `finalize-update.sh` SHA-256:
  `102e6aac59a70a05405a35010fa8ac0eead076b6460f68a851542c310ab6c268`.
- `run-update.sh` SHA-256:
  `563dd6b59fcce46bf68721e68aa2dfabd51f6d396594012e3cec256aaeb887cd`.
- `TODO.md` SHA-256:
  `a8d144ee224d05203e3978ced12957a2d53cc0a8fb22a43f58d2fc73c23a145a`.
- Every pre/post-move hash matched; archived files are readable.
- Original source directory is now absent.
- Restore by moving each `payload/<relative-path>` back under the workspace
  root. Retain archive until separately approved for disposal.

## Post-cleanup boundary

- Local `main`: 186 ahead / 0 behind `origin/main` before evidence commit.
- Remaining: 11 tracked historical supervisor evidence/state/outbox changes and
  6 pre-existing untracked groups, plus this evidence task before commit.
- Historical supervisor/outbox files were not touched.
- No message queue, SQLite delivery data, notification record, or delivery
  state was read or mutated for cleanup.
- No replay or resend occurred.
