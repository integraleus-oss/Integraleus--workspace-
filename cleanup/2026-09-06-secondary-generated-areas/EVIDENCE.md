# Secondary Generated Areas Cleanup Evidence

## Result

- Status: `SUCCEEDED`
- Baseline HEAD: `57ccdbffce11edf791dfee5361fac04518483c14`
- Archive: `/home/stanislav/repository-cleanup-archives/2026-09-06-secondary-generated-areas/`
- Manifest: `MANIFEST.sha256` (96 regular, non-symlink files)
- Archived payload: 66,021,915 bytes; 64 MiB on disk
- Pre-move verification: 96/96 SHA-256 checks passed
- Post-move verification: 96/96 SHA-256 checks passed
- Readability: every archived file was readable by `file` and SHA-256 verification

## Classification

- `site_images/` (326 MiB, 687 files): retained. It is an imported user/media corpus containing documents, spreadsheets, presentations, audio and images; 37 files are tracked and 650 are ignored. Directory naming alone is not proof of disposability.
- `generated/`: 96 ignored derived image/video outputs archived. The 13 tracked Blender/3D/source files remain; size reduced from 79 MiB to 15 MiB.
- `.venv/` (61 MiB, 2072 regular files plus 4 symlinks): retained. Its paths are tracked, and moving it would alter the historical repository boundary and violate the regular/non-symlink target rule.
- `outgoing/` (23 MiB, 95 files): retained as messaging/delivery boundary; one file is tracked and 94 delivery artifacts are ignored.

No tracked source, imported corpus, message/delivery artifact, symlink, SQLite, queue, notification, supervisor, outbox or `state/` file was moved.

## Restoration

From the workspace root, restore the whole batch with:

```bash
archive=/home/stanislav/repository-cleanup-archives/2026-09-06-secondary-generated-areas
while IFS= read -r line; do
  path="${line#*  }"
  mkdir -p "${path%/*}"
  cp -- "$archive/$path" "$path"
done < cleanup/2026-09-06-secondary-generated-areas/MANIFEST.sha256
sha256sum -c cleanup/2026-09-06-secondary-generated-areas/MANIFEST.sha256
```

The archive contains its own copy of `MANIFEST.sha256`.

## Boundaries and checks

- No replay or message resend command was executed.
- `site_images/`, `.venv/`, `outgoing/`, `state/`, supervisor artifacts, message queues, outbox data, SQLite and delivery state were not mutated.
- `git diff --check` passed before committing this evidence.
- Pre-existing changes in `skills/safe-repository-cleanup/SKILL.md` and excluded `state/` remain outside this cleanup commit.
