# `.venv` repository-hygiene checkpoint

- Owner: Stanislav / primary agent
- Started: 2026-09-06T15:34:40+03:00
- Baseline HEAD: `b59fc82741ddb06a2e528062eae1cf8943b6bdbb`
- Execution mechanism: current foreground Codex turn; no background job
- Expected output: reproducibility evidence, symlink-aware external archive, exact manifests, restore proof, and one scoped Git commit removing tracked `.venv`
- Archive retention: retain until Stanislav separately approves disposal
- Excluded: `state/`, `supervisor/`, `outbox/`, message replay/resend, and push

## Baseline

- `.venv`: 61 MiB reported by `du -sh`
- Git-tracked paths: 2,076
- Regular files: 2,072
- Symlinks: 4
- Runtime: Python 3.12.3; pip 24.0
- `pip check`: `No broken requirements found.`
- Branch divergence: `main` ahead of `origin/main` by 195 commits
- Pre-existing worktree changes are confined to the excluded `state/...` boundary.

## Checklist

- [x] Record owner, start time, mechanism, baseline, and exclusions
- [x] Identify dependency inventory and prove a clean environment can be recreated
- [x] Create exact regular-file SHA-256 manifest and symlink manifest
- [x] Create and verify external symlink-aware archive
- [x] Prove restoration into an isolated temporary directory
- [x] Remove `.venv` from Git and add/confirm ignore rule
- [x] Run relevant smoke checks and `git diff --check`
- [x] Commit only `.venv` hygiene artifacts and tracked removal

## Stop conditions

Stop without removing `.venv` if dependencies cannot be reproduced, archive or restore verification fails, symlink metadata differs, or any target crosses the excluded messaging/supervisor boundary.

## Dependency source of truth

The tracked environment had no root lockfile. `requirements.lock` records the exact
non-bootstrap package set returned by `.venv/bin/python -m pip freeze --all`; pip
itself is intentionally excluded because a fresh `venv` bootstraps it.

## Verification result

- Recreated clean environment: PASS
- External archive SHA-256/readability: PASS
- Isolated restore, 2,072 file hashes: PASS
- Isolated restore, 4 symlink targets: PASS
- Restored and recreated environment smoke checks: PASS
- Original `.venv` paths absent after archival: PASS
- Root `/.venv/` ignore rule active: PASS
