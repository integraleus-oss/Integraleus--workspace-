# `.venv` removal evidence

## Scope and baseline

- Owner: Stanislav / primary agent
- Started: 2026-09-06T15:34:40+03:00
- Baseline HEAD: `b59fc82741ddb06a2e528062eae1cf8943b6bdbb`
- Original tree: 2,076 Git-tracked paths; 2,072 regular files; 4 symlinks
- Original size: 61 MiB reported by `du -sh`
- Excluded throughout: `state/`, `supervisor/`, `outbox/`, message replay/resend, and push

## Reproducibility proof

The original environment used Python 3.12.3 and pip 24.0. Its exact
non-bootstrap package inventory is recorded in `requirements.lock`.

An isolated environment was created with `python3 -m venv` and populated from
that lock. Verification passed:

- dependency installation: PASS
- `python -m pip check`: `No broken requirements found.`
- imports of `charset_normalizer`, `lxml`, `PIL`, `docx`, `reportlab`, and
  `typing_extensions`: `IMPORT_SMOKE_OK`

Recreation command:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r cleanup/2026-09-06-venv-removal/requirements.lock
.venv/bin/python -m pip check
```

## Archive and manifests

- Archive directory: `/home/stanislav/repository-cleanup-archives/2026-09-06-venv-removal/`
- Archive: `venv.tar`
- Archive size: 62,156,800 bytes
- Regular-file hashes: `FILES.sha256` (2,072 entries)
- Symlink metadata: `SYMLINKS.tsv` (4 entries)
- Complete tracked-path inventory: `PATHS.manifest` (2,076 entries)
- Archive hash: `ARCHIVE.sha256`

The complete manifest path set was byte-compared with `git ls-files .venv`.
The POSIX tar was created without symlink dereferencing and passed `tar -tf`.
All manifests and the archive hash are duplicated beside the external archive.

## Isolated restoration proof

The archive was extracted with `tar -xpf` into a new temporary directory.

- 2,072/2,072 restored regular files matched SHA-256.
- 4/4 restored symlinks matched their exact link targets.
- restored `python -m pip check`: PASS
- restored dependency import smoke: `RESTORE_IMPORT_SMOKE_OK`

## Full restoration

From the workspace root:

```bash
tar -xpf /home/stanislav/repository-cleanup-archives/2026-09-06-venv-removal/venv.tar -C .
sha256sum -c cleanup/2026-09-06-venv-removal/FILES.sha256
```

Then compare links:

```bash
find .venv -type l -printf '%p\t%l\n' | LC_ALL=C sort
```

against `cleanup/2026-09-06-venv-removal/SYMLINKS.tsv`.

The external archive must be retained until Stanislav separately approves its
disposal.

## Post-removal verification

- `.venv` is absent from the workspace after the verified archive was created.
- Root `/.venv/` is covered by `.gitignore`.
- All 2,076 manifest source paths are absent.
- External archive SHA-256 and `tar -tf` readability were rechecked after removal.
- The clean reproduced environment again passed `pip check` and all dependency
  imports (`FINAL_REPRO_SMOKE_OK`).
- `git diff --check` passed before commit.
- No path under `state/`, `supervisor/`, or `outbox/` is part of this task's
  staged boundary.
