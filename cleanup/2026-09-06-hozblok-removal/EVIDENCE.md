# Hozblok project removal evidence

## Scope

- Baseline HEAD: `0f2cf6f71cfe66fdda036a4432bdcc775cb2d0e4`
- Removed current project directory:
  `state/tasks/2026-08-15-hozblok-blender/`
- Removed nine root hozblok plans/renders/ZIP files
- Removed two empty generated frame directories: `grill-frames/` and
  `grill-frames-2/`
- Historical mentions in unrelated evidence/memory, earlier shared cleanup
  archives, and Git history were deliberately retained.

## Inventory and archive

- Files: 63 regular non-symlink files
- Payload: 146,382,149 bytes
- Tracked files removed: 22
- Ignored files removed: 41
- Exact targets: `TARGETS.txt`
- Exact hashes: `FILES.sha256`
- Archive hash: `ARCHIVE.sha256`
- External archive:
  `/home/stanislav/repository-cleanup-archives/2026-09-06-hozblok-removal/hozblok-current-files.tar`

The tar archive passed checksum/readability checks. It was extracted into an
isolated temporary directory and all 63 restored files matched SHA-256.

## Recovery

Restore from the workspace root:

```bash
tar -xpf /home/stanislav/repository-cleanup-archives/2026-09-06-hozblok-removal/hozblok-current-files.tar -C .
sha256sum -c cleanup/2026-09-06-hozblok-removal/FILES.sha256
```

The original current files were also moved to the desktop trash with `gio
trash`, rather than irreversibly deleted. The verified external archive must be
retained until Stanislav separately approves disposal.

## Boundaries

- No unrelated evidence/memory reference was edited.
- No earlier shared archive was removed because it contains non-hozblok files.
- No Git history rewrite, push, replay, resend, or delivery action was run.
