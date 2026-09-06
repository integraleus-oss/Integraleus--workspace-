# Dirty worktree preservation and migration evidence

## Outcome

Preservation and migration succeeded for the three dirty worktrees attached to
the rewritten branch refs. Original refs, original worktree contents, and the
GitHub remote configuration were not changed. No fetch, push, replay, resend,
or delivery operation was performed.

## Preserved sources and migrated bases

- `main`: source `3bb62a55aab4059b03ef5bb22275d2690f9329ff` migrated onto sanitized `3ba0e3e72f011be455726b6788baab56ed4cd232`; 33 dirty paths at the preservation boundary, including 23 untracked files.
- `managed-program-r20-isolated`: source `f70913ea89518bf7403cb154f7b0ec2045102350` migrated onto sanitized `1913397c7c0b28f0954708f1b96486725a1900a7`; 74 dirty paths, all untracked.
- `orchestrator-review-loop-reduction`: source `9adbee74b2840ba37dc9c5f9be535e4133aed89a` migrated onto sanitized `56ed73b1be448f50dc9febd86035a911a727525c`; 7 modified tracked paths.

The fourth dirty worktree, detached at
`/home/stanislav/agent-runs/orchestrator-worktrees/orchestrator-pilot3-hardening`,
was excluded because its detached commit/ref was not among the three rewritten
branch refs. It was not changed.

## Preservation

Archive root:
`/home/stanislav/repository-cleanup-archives/2026-09-06-dirty-worktree-migration/preservation/`

Each branch directory contains source HEAD and NUL-safe status/path manifests,
full-index binary patches for tracked index/worktree changes, an untracked TAR,
a file-hash/symlink-target manifest, and checksums. Checksum verification passed
for all four payload artifacts in each directory. Untracked TARs were extracted
into isolated verification directories and every regular-file SHA-256 and
symlink target matched.

Preservation artifact sizes:

- `main`: 149,424 bytes;
- `managed-program-r20-isolated`: 539,339 bytes;
- `orchestrator-review-loop-reduction`: 48,548 bytes.

The pre-rewrite rollback bundle remains unchanged at 673,103,310 bytes with
SHA-256 `a17fc4bb5a479de7f59d8ee271ed2e2614f18ffbcb788241efd2926f82916718`.

## Migrated worktrees

- `/home/stanislav/repository-cleanup-archives/2026-09-06-dirty-worktree-migration/migrated-worktrees/main`
- `/home/stanislav/repository-cleanup-archives/2026-09-06-dirty-worktree-migration/migrated-worktrees/managed-program-r20-isolated`
- `/home/stanislav/repository-cleanup-archives/2026-09-06-dirty-worktree-migration/migrated-worktrees/orchestrator-review-loop-reduction`

For every migrated worktree, the union of modified, staged, and untracked paths
matched its source exactly at the preservation boundary. Every present regular
file was byte-compared, symlink targets were compared, and absent paths were
confirmed absent. All three equivalence checks passed. `git diff --check` and
`git fsck --connectivity-only` passed in all three clones; expected dangling
pre-rewrite commits remain because no prune or garbage collection was run.

The seven filtered target rules have zero reachable path hits in all three
sanitized heads. The preserved remote-tracking boundary in the mirror remains
`6c1dddb41f2a728a2b978cfbcb633d3acd50ed65`.

## Original boundary after preservation, before authorized ref replacement

- `refs/heads/main` remains `3bb62a55aab4059b03ef5bb22275d2690f9329ff`.
- `refs/heads/managed-program-r20-isolated` remains `f70913ea89518bf7403cb154f7b0ec2045102350`.
- `refs/heads/orchestrator-review-loop-reduction` remains `9adbee74b2840ba37dc9c5f9be535e4133aed89a`.
- Original `origin` fetch/push URL remains `git@github.com:integraleus-oss/Integraleus--workspace-.git`.

No commit was created during preservation because committing would have moved
an original branch ref before authorization.
The migration clones use the local sanitized mirror as their `origin`; they are
not configured to push directly to GitHub.

## Restore and next boundary

To reconstruct a migrated dirty state, clone the sanitized mirror at the named
branch, apply `tracked-index.patch` with `git apply --index --binary`, apply
`tracked-worktree.patch` with `git apply --binary`, then extract
`untracked.tar` at the worktree root and verify `preservation-sha256.txt` plus
`untracked-manifest.tsv`.

## Authorized local-ref replacement

At 2026-09-06 18:11 MSK the owner explicitly authorized replacement of the
three local refs. The rewritten objects were imported from the local sanitized
mirror into a temporary namespace. Before mutation, the exact old/new commits
were confirmed and base-tree changes were compared with every tracked and
untracked dirty path; overlap was zero for all three worktrees.

Because `main` had an identical old/new tip tree while the other two branches
removed already-authorized target paths from their tips, each checked-out branch
was moved with `git reset --keep` to preserve unrelated dirty state while making
its index and worktree consistent with the sanitized tree.

Applied CAS boundary:

- `main`: `3bb62a55aab4059b03ef5bb22275d2690f9329ff` -> `3ba0e3e72f011be455726b6788baab56ed4cd232`;
- `managed-program-r20-isolated`: `f70913ea89518bf7403cb154f7b0ec2045102350` -> `1913397c7c0b28f0954708f1b96486725a1900a7`;
- `orchestrator-review-loop-reduction`: `9adbee74b2840ba37dc9c5f9be535e4133aed89a` -> `56ed73b1be448f50dc9febd86035a911a727525c`.

The dirty state remained present. A post-replacement change to
`skills/safe-repository-cleanup/SKILL.md` made after the first snapshot was
detected by final comparison, so a supplemental complete `main` snapshot was
created at
`/home/stanislav/repository-cleanup-archives/2026-09-06-dirty-worktree-migration/post-ref-main/`.
It contains 34 dirty paths and was restored into a fresh isolated clone;
path-set and byte equivalence, checksums, `git diff --check`, and connectivity
all passed.

The original GitHub remote configuration remains unchanged. No network fetch,
push, replay, resend, delivery action, prune, or garbage collection occurred.
Any push or force-push remains separately unauthorized and requires a fresh
pre-push audit plus exact remote-tip verification.

## Fresh worktree and pre-push audit

The owner requested focused checks of all three migrated worktrees and a fresh
pre-push audit. The complete results and `NO-GO for push now` verdict are in
`PRE_PUSH_AUDIT.md`. The rewritten transfer itself remains free of authorized
target paths/blobs, queue/outbox paths, large blobs, and confirmed live secrets;
the remaining blockers are dirty-worktree/test reproducibility and final-tip
hygiene, not a regression of the history rewrite.
