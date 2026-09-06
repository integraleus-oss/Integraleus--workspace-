# Hozblok project removal checkpoint

- Owner: Stanislav / primary agent
- Started: 2026-09-06
- Baseline HEAD: `0f2cf6f71cfe66fdda036a4432bdcc775cb2d0e4`
- Execution mechanism: current foreground Codex turn; no background job
- Expected output: verified archive and one scoped removal commit
- Scope: current project files under `state/tasks/2026-08-15-hozblok-blender/`, nine root files named for hozblok, and the two empty `grill-frames*` directories
- Excluded: historical references in unrelated evidence/memory, existing cleanup archives, Git history rewrite, push, replay/resend, and unrelated dirty files

## Baseline inventory

- Task directory: 54 files, 144,239,156 bytes
- Root named artifacts: 9 files, 2,142,993 bytes
- Total current payload: 63 files, 146,382,149 bytes
- Task tracking: 22 tracked files, 32 ignored files
- Symlinks: none expected; validation required before archival

## Checklist

- [x] Record exact scope and baseline
- [x] Create exact file manifest and SHA-256 inventory
- [x] Create external archive and isolated restore proof
- [x] Move all scoped current files to recoverable trash
- [x] Stage only tracked project removals
- [x] Verify unrelated dirty paths are unchanged
- [x] Commit the scoped removal

## Retention

Keep the verified external archive until Stanislav separately approves its disposal.
The earlier shared pre-push archives are retained because they also contain non-hozblok evidence.
