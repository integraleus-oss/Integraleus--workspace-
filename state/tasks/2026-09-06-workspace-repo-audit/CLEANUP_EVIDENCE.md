# Cleanup evidence

Status: IN_PROGRESS
Started: 2026-09-06 11:48 MSK
Archive root:
`/home/stanislav/.openclaw/backups/workspace-repo-cleanup-2026-09-06T1148`

## Batch 1 — proven temporary/local files

- Exact target list: archive `TARGETS.txt` (11 paths).
- Targets: two workspace-state migration remnants, one accidental empty file,
  four dated backups, and three empty supervisor finalize locks.
- Every target was validated as an existing regular non-symlink file.
- SHA-256 was calculated before and after archival; all 11 values matched.
- Originals no longer exist at their workspace paths.
- Archive payload size: about 140 KiB.
- Recovery: move any file from `payload/<relative-path>` back to the same
  relative path under the workspace root.
- No SQLite database or queue was opened or changed.
- No notification/message record was replayed, resent, or mutated.

The two legacy tracked workspace-state paths were already absent before this
batch. Their migration copies are now preserved in the archive, so their Git
deletions can be recorded safely.
