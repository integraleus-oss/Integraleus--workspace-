# Tertiary Generated Areas Cleanup Evidence

## Result

- Status: `SUCCEEDED`
- Baseline HEAD: `21b32c13ac616071b83fa185c83fe17fa89d2d22`
- Archive: `/home/stanislav/repository-cleanup-archives/2026-09-06-tertiary-generated-areas/`
- Manifest: `MANIFEST.sha256` (68 regular, non-symlink JPEG files)
- Archived payload: 4,021,529 bytes; 4.0 MiB on disk
- Pre-move verification: 68/68 SHA-256 checks passed
- Post-move verification: 68/68 SHA-256 checks passed
- Readability: all archived files were recognized as JPEG and read successfully for SHA-256 verification

## Classification

- `artifacts/` (7.6 MiB, 19 files): retained. The 11 tracked files are durable artifacts; the 8 ignored PNG files are architecture renders, UI variants and PS01 evidence.
- `grill-frames-2/`: 59 ignored extracted JPEG frames archived; directory left empty.
- `hmi-demo/` (2.5 MiB, 145 tracked files): retained as durable demo/source material.
- `grill-frames/`: 9 ignored extracted JPEG frames archived; directory left empty.
- `output/` (424 KiB, 43 files): retained. The 28 tracked files are durable material; the 15 ignored files are investor-demo deliverables and Alpha configuration backups.
- `tmp-screens/`: confirmed empty; no archive created for it.

No tracked source, durable evidence, deliverable, configuration backup, message/delivery artifact, symlink, SQLite, queue, notification, supervisor, outbox or `state/` file was moved.

## Restoration

From the workspace root, restore the whole batch with:

```bash
archive=/home/stanislav/repository-cleanup-archives/2026-09-06-tertiary-generated-areas
while IFS= read -r line; do
  path="${line#*  }"
  mkdir -p "${path%/*}"
  cp -- "$archive/$path" "$path"
done < cleanup/2026-09-06-tertiary-generated-areas/MANIFEST.sha256
sha256sum -c cleanup/2026-09-06-tertiary-generated-areas/MANIFEST.sha256
```

The archive contains its own copy of `MANIFEST.sha256`.

## Boundaries and checks

- No replay or message resend command was executed.
- `artifacts/`, `hmi-demo/`, `output/`, `tmp-screens/`, `state/`, supervisor artifacts, message queues, outbox data, SQLite and delivery state were not mutated.
- `git diff --check` passed before committing this evidence.
- Pre-existing changes in `skills/safe-repository-cleanup/SKILL.md` and excluded `state/` remain outside this cleanup commit.
