# Pre-push scoped `state` cleanup evidence

## Scope

- Owner: Stanislav / primary agent
- Started: 2026-09-06T17:07:58+03:00
- Baseline HEAD: `5775fab020d382e1b1625a7adaa365c8ea7549cc`
- Baseline divergence: 198 commits ahead of `origin/main`
- Authorized: 6 terminal outbox fixtures, 4 Blender/GLB deliverables, and
  whitespace-only normalization in 9 listed `state` files
- Excluded: history rewrite, push, replay/resend, and all other dirty paths

## Classification

- The six JSONL files are terminal test fixtures: one valid row each, status
  `SUCCEEDED`, with no message/body/payload, destination, recipient, token, or
  secret fields.
- The four 3D files are standalone deliverables/evidence introduced by
  `e21f7d5e`; no references by basename were found outside their task directory.
- The remaining nine targets contain only range-wide whitespace defects: 60
  trailing-whitespace findings in two OMX files and blank EOF lines in seven
  Markdown evidence files.

## Archive proof

- External directory:
  `/home/stanislav/repository-cleanup-archives/2026-09-06-pre-push-state-cleanup/`
- Current-worktree archive: `worktree-targets.tar`
- Baseline-HEAD archive: `head-targets.tar`
- Target count: 19 regular non-symlink files
- Current-worktree payload: 129,062,362 bytes
- Exact hashes: `WORKTREE_FILES.sha256` and `HEAD_FILES.sha256`
- Archive hashes: `ARCHIVES.sha256`

Both tar archives passed checksum/readability checks. The current-worktree
archive was extracted into an isolated temporary directory and all 19 restored
files matched `WORKTREE_FILES.sha256`. This preserves the two locally modified
outbox variants as well as every other pre-cleanup target byte-for-byte.

## Restoration

Restore the exact pre-cleanup worktree targets from the workspace root:

```bash
tar -xpf /home/stanislav/repository-cleanup-archives/2026-09-06-pre-push-state-cleanup/worktree-targets.tar -C .
sha256sum -c cleanup/2026-09-06-pre-push-state-cleanup/WORKTREE_FILES.sha256
```

To restore baseline committed versions instead, use `head-targets.tar` and
verify against `HEAD_FILES.sha256`.

The archives must remain until Stanislav separately approves disposal.

## Mutation boundary

- Removed from the current tree: exactly 6 fixtures and 4 3D files.
- Normalized: exactly 9 authorized whitespace files.
- Added narrow ignore rules for task outbox JSONL and the four exact 3D paths.
- No replay, resend, delivery operation, history rewrite, fetch, or push was run.
