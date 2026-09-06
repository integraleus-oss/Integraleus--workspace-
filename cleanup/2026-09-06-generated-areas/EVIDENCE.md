# Generated Areas Cleanup Evidence

## Result

- Status: `SUCCEEDED`
- Baseline HEAD: `cd1ad69ab03206836c2f51313ca1ba51c4230c80`
- Archive: `/home/stanislav/repository-cleanup-archives/2026-09-06-generated-areas/`
- Manifest: `MANIFEST.sha256` (26 regular, non-symlink files)
- Archived payload: 9.9 MiB on disk
- Pre-move verification: 26/26 SHA-256 checks passed
- Post-move verification: 26/26 SHA-256 checks passed
- Readability: both nested `tar.gz` audit packages passed `tar -tzf`; every archived file was readable for SHA-256 verification

## Classification

- `out/` (534 MiB, 33 files): retained as current or ambiguous Alpha BPR deliverables.
- `media/` (125 MiB, 279 files): retained because inbound/outbound staged media belongs to the messaging boundary.
- `outbound/` (16 MiB, 71 files): retained as delivery evidence/projects; contains SQLite and delivery-adjacent material.
- `tmp/`: 3 proven temporary files archived; directory left empty.
- `exports/` (4.9 MiB, 2 files): retained as video/SRT deliverables.
- `tmp_djvu_check/`: 23 proven OCR/DjVu scratch files archived; directory left empty.

No ambiguous, durable, message-related, SQLite, queue, notification, delivery-state, supervisor, or `state/` file was moved.

## Restoration

From the workspace root, restore any listed file by copying it from the archive to the same relative path. For the whole batch:

```bash
archive=/home/stanislav/repository-cleanup-archives/2026-09-06-generated-areas
while IFS= read -r line; do
  path="${line#*  }"
  mkdir -p "${path%/*}"
  cp -- "$archive/$path" "$path"
done < cleanup/2026-09-06-generated-areas/MANIFEST.sha256
sha256sum -c cleanup/2026-09-06-generated-areas/MANIFEST.sha256
```

The archive also contains its own copy of `MANIFEST.sha256`.

## Boundaries and checks

- No replay or message resend command was executed.
- `state/`, supervisor artifacts, message queues, outbox data, SQLite and delivery state were not mutated by this cleanup.
- `git diff --check` passed before committing the evidence.
- Pre-existing dirty paths in the excluded area remain outside this cleanup commit.
