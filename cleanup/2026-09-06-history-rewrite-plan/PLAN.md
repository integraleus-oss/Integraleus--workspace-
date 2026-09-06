# Read-only history-rewrite plan

## Baseline

- Planned at HEAD: `77958712b85bcb137a4201970ea6acb4d24e1288`.
- Verified live remote-tracking boundary: `origin/main` at
  `6c1dddb41f2a728a2b978cfbcb633d3acd50ed65`.
- Divergence at planning time: 0 behind / 201 ahead.
- This planning step does not rewrite refs, objects, index, worktree, or remote.
- Existing unrelated dirty paths in `skills/` and `state/` are excluded.

## Exact removal scope

`TARGET_PATHS.txt` contains seven filter rules:

- the complete historical task directory
  `state/tasks/2026-08-15-hozblok-blender/`;
- six exact terminal outbox-fixture paths.

The path rules currently resolve to 32 unique blobs in the push range:
26 hozblok blobs and six fixture blobs. `TARGET_BLOBS.tsv` records every object
ID, uncompressed size, and path. Root hozblok PNG/ZIP files were never tracked,
so no commit rewrite is required for them.

Affected local refs:

- hozblok: `refs/heads/main`, `refs/heads/managed-program-r20-isolated`,
  `refs/heads/orchestrator-review-loop-reduction`;
- outbox fixtures: `refs/heads/main`,
  `refs/heads/managed-program-r20-isolated`.

No tag or `refs/remotes/origin/main` contains the target commits.

## Backup before any rewrite

Create a timestamped directory outside the repository under
`/home/stanislav/repository-cleanup-archives/`. Before filtering:

1. Record `git status --porcelain=v2`, every local head/tag/remote-tracking ref,
   remotes, HEAD, origin/main, divergence, `git count-objects -vH`, and the live
   `git ls-remote origin refs/heads/main` result.
2. Create `pre-history-rewrite-all-refs.bundle` with `git bundle create --all`.
3. Record SHA-256 and byte size, run `git bundle verify`, clone the bundle into
   an isolated temporary directory, and confirm all recorded refs and tip trees.
4. Copy this plan, both target manifests, and the existing hozblok/pre-push
   cleanup evidence into the external backup directory.
5. Keep the bundle and existing content archives until the owner separately
   approves disposal.

Estimated bundle size is approximately the current packed repository size
(about 642 MiB); 624 GiB was free at planning time.

## Rewrite mechanism

`git-filter-repo` is not installed on the host at planning time. Do not fall
back to `git filter-branch`. In the authorized execution turn:

1. Install/pin `git-filter-repo` in a disposable Python virtual environment and
   record its version and package hash.
2. Create a local mirror clone from the repository after the verified bundle
   exists. Uncommitted worktree files must not enter the mirror.
3. Run `git filter-repo --invert-paths` with exactly the seven rules from
   `TARGET_PATHS.txt`, limited to the three affected local branch refs. Preserve
   `refs/remotes/origin/main` and tags unchanged.
4. Do not update the original repository refs during this phase. Treat the
   sanitized mirror as a candidate only.

This approach keeps the dirty original worktree and rollback refs untouched
while validation runs. No reflog expiry, prune, or garbage collection is part
of the rewrite task.

## Validation gates

The candidate fails closed unless all checks pass:

1. `git fsck --full` succeeds in the sanitized mirror.
2. The rewritten `main` has 0 behind relative to preserved origin/main and the
   same first-parent/merge shape and commit count expected from the filter.
3. Rewritten tip trees equal their pre-rewrite tip trees. The target paths are
   already absent at the tips, so a tree mismatch indicates unintended change.
4. No path from `TARGET_PATHS.txt` appears anywhere in any rewritten branch.
5. No object ID from `TARGET_BLOBS.tsv` is reachable from any rewritten branch.
6. The six fixture paths and all hozblok paths are absent from the proposed
   `origin/main..rewritten-main` transfer.
7. Re-run the full pre-push audit: unique blob volume/large objects,
   high-confidence secret signatures without values, queue/outbox schema scan,
   range-wide whitespace, rename-aware changed paths, and connectivity.
8. Confirm the three known non-state blank-EOF findings separately; they are
   outside this rewrite scope.
9. Re-query live remote `main` and require it to remain exactly
   `6c1dddb41f2a728a2b978cfbcb633d3acd50ed65` before any later force-push plan.
10. Run a force-with-lease dry run only after all prior gates pass. A real push
    remains separately unauthorized.

## Applying the candidate later

After a successful report, require a second explicit owner decision choosing:

- keep the sanitized mirror only and stop;
- replace the three affected local branch refs from the sanitized mirror; or
- force-push rewritten `main` with an exact lease on the verified remote SHA.

Updating original refs requires a clean or separately preserved worktree.
Force-push must use an explicit `--force-with-lease=refs/heads/main:<sha>` and
is never implied by authorization to rewrite locally.

## Rollback

- Before push: discard the sanitized mirror; the original repository remains
  unchanged.
- After local-ref replacement: restore exact refs from the verified bundle.
- After a future remote force-push: restore `main` from the bundle with an exact
  force-with-lease against the rewritten remote tip.
- Restore project files independently from the previously verified hozblok and
  pre-push-state archives if needed.

## Execution checklist

- [ ] Separate explicit authorization to execute the isolated rewrite.
- [ ] Full all-refs bundle created, hashed, verified, and test-cloned.
- [ ] Tool version pinned and recorded.
- [ ] Sanitized mirror created; original refs/worktree unchanged.
- [ ] Exactly seven path rules applied to exactly three local branches.
- [ ] All validation gates pass and evidence is written.
- [ ] Separate owner decision on local ref replacement.
- [ ] Separate owner authorization for any force-push.
