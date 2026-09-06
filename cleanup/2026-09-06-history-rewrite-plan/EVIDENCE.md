# Isolated history-rewrite evidence

## Outcome

The isolated rewrite candidate passed validation. The original repository refs,
index, worktree, and remote were not rewritten or pushed.

## Original boundary

- Original HEAD before and after: `77958712b85bcb137a4201970ea6acb4d24e1288`.
- Live remote `main`: `6c1dddb41f2a728a2b978cfbcb633d3acd50ed65`.
- Original divergence: 0 behind / 201 ahead.
- The original worktree remained dirty with 14 pre-existing/unrelated status
  entries, including the uncommitted plan directory as one entry.

## Backup proof

- Bundle:
  `/home/stanislav/repository-cleanup-archives/2026-09-06-history-rewrite/pre-history-rewrite-all-refs.bundle`
- Size: 673,103,310 bytes.
- SHA-256:
  `a17fc4bb5a479de7f59d8ee271ed2e2614f18ffbcb788241efd2926f82916718`.
- `git bundle verify`: PASS; bundle records complete history and ten refs.
- Test mirror clone from the bundle: PASS.
- Local heads and tags in the test clone matched the original refs.
- Test-clone `git fsck --full`: PASS.

## Tool and candidate

- Tool: `git-filter-repo` 2.47.0 (`a40bce548d2c`).
- Wheel SHA-256:
  `2cd04929b9024e83e65db571cbe36aec65ead0cb5f9ec5abe42158654af5ad83`.
- Candidate mirror:
  `/home/stanislav/repository-cleanup-archives/2026-09-06-history-rewrite/sanitized-mirror.git`
- Exactly seven path rules were applied with `--invert-paths` to exactly:
  `main`, `managed-program-r20-isolated`, and
  `orchestrator-review-loop-reduction`.
- `origin/main` and both tags remained unchanged.

## Ref mapping

- `main`: `77958712b85bcb137a4201970ea6acb4d24e1288` ->
  `0d7f6684b6772dc5e605b1ea02697274e682c743`.
- `managed-program-r20-isolated`:
  `f70913ea89518bf7403cb154f7b0ec2045102350` ->
  `1913397c7c0b28f0954708f1b96486725a1900a7`.
- `orchestrator-review-loop-reduction`:
  `9adbee74b2840ba37dc9c5f9be535e4133aed89a` ->
  `56ed73b1be448f50dc9febd86035a911a727525c`.
- Full map SHA-256:
  `88aadb6f5ed67255b33ba6507c6171660c7639dbb90d2712e13b2cd6a1345ef0`.

The hozblok-only commit `e21f7d5e53842733e01251cb35c5e90a7fa36dc4`
became empty and was removed. Therefore rewritten `main` is 200 commits ahead,
not 201.

## Validation

- Target paths reachable from rewritten heads: 0/7.
- Target blob IDs reachable from rewritten heads: 0/32.
- Non-target tip-tree content matches the original for all three branches.
- `main` full tip-tree is byte-identical because targets were already absent.
- Rewritten `main` divergence: 0 behind / 200 ahead.
- New unique transfer payload: 1,493 blobs / 21,479,984 bytes.
- Reachable transfer blobs at least 1 MiB: 0.
- Added high-confidence secret signatures: 0.
- The two whole-patch heuristic matches were removed vendor-code lines from the
  historical virtualenv deletion, not added secrets.
- Target queue/outbox paths in the transfer: 0.
- Rename-aware diff with `diff.renameLimit=12000`: PASS.
- `git fsck --full`: exit 0. It reports old pre-rewrite commits as dangling in
  the isolated mirror; no prune or garbage collection was run.
- Remaining `git diff --check` findings: three known non-state blank-EOF lines
  in shared-memory Markdown, outside rewrite scope.
- Live remote remained exactly `6c1dddb41f2a728a2b978cfbcb633d3acd50ed65`.

## Stop boundary

The candidate is validated but not applied to the original local refs. No
force-with-lease dry run or real push was performed. A separate owner decision
is required to replace local refs; any push needs an additional explicit
authorization.
