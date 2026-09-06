# Dirty worktree preservation and migration

- Owner: OpenClaw main agent
- Started: 2026-09-06 18:04 MSK
- Execution: current foreground turn; no background job
- Expected output: verified preservation archives plus three migrated worktrees based on sanitized refs
- Boundaries: do not change original refs, original worktree contents, remote refs, or messaging/delivery state; do not push, replay, or resend

## Checklist

- [x] Inventory the three affected dirty worktrees and their exact base commits.
- [x] Preserve tracked diffs, untracked files, symlinks, status, and hashes outside the repository.
- [x] Verify each preservation archive by isolated extraction and byte/hash comparison.
- [x] Create three separate migration worktrees from the sanitized mirror refs.
- [x] Apply each preserved dirty state and verify source-to-destination equivalence.
- [x] Record final evidence, migration paths, rollback instructions, and Git boundaries.
- [x] Replace the three authorized local branch refs with exact sanitized SHAs.
- [x] Verify retained dirty state, filtered-path absence, rollback bundle, and unchanged remote.
- [x] Validate current dirty contents in each migrated worktree with focused checks.
- [x] Re-query live remote tip without updating remote-tracking refs.
- [x] Run the complete rewritten-range pre-push audit.
- [x] Record a push/no-push verdict and residual blockers without pushing.

## Main publication preparation (2026-09-06 continuation)

- Owner: OpenClaw main agent
- Started: 2026-09-06 18:35 MSK
- Execution: current foreground turn; no background job
- Expected output: narrow reviewed commits on `main`, self-contained review-loop tests, and a fresh pre-push audit
- Boundaries: prepare only `main`; keep service branches local; do not commit backup or notification-outbox paths; do not push, force-push, replay, resend, prune, or garbage-collect

### Planned semantic batches

- [ ] Final-tip hygiene: remove the three known blank lines at EOF in `projects/openclaw-shared-memory/docs/PHASE4_*.md`.
- [ ] Sanitized-history governance: review and commit the cleanup evidence, decision/state records, and safe-cleanup procedure updates.
- [ ] Supervisor/orchestrator evidence: review changed execution evidence/state separately from product code.
- [ ] Alpha BPR R6 orchestrator corpus: review the new task corpus while excluding `notification-outbox-r3.jsonl`.
- [ ] Backup boundary: leave `state/tasks/2026-09-04-orchestrator-live-recovery/backup/` uncommitted.
- [ ] Review-loop integration: make the fixture self-contained and prove 152/152 plus 87/87 before bringing the reviewed change to `main`.
- [ ] Run the complete pre-push audit against the final exact `main` tip and stop before push.
