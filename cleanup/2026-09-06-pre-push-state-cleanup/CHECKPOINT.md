# Pre-push scoped `state` cleanup checkpoint

- Owner: Stanislav / primary agent
- Started: 2026-09-06T17:07:58+03:00
- Baseline HEAD: `5775fab020d382e1b1625a7adaa365c8ea7549cc`
- Baseline divergence: `main` ahead of `origin/main` by 198 commits
- Execution mechanism: current foreground Codex turn; no background job
- Expected output: verified external archive, scoped cleanup commit, repeated pre-push audit
- Archive retention: retain until Stanislav separately approves disposal
- Excluded: history rewrite, push, replay/resend, and every `state` path not listed below

## Authorized targets

### Remove from the current tree after verified archival

- Six terminal test `outbox.jsonl` / `notification-outbox.jsonl` fixtures identified by the pre-push review
- Four Blender/GLB deliverables introduced by `e21f7d5e`

### Whitespace-only normalization

- `state/tasks/2026-08-01-mix01-webviewer-buttons/staging/ps01-mix01-devstudio/PS01_Server.omx`
- `state/tasks/2026-08-01-ps01-alpha-native-compliance/staging/ps01-mix01-mode-devstudio/PS01_Server.omx`
- `state/tasks/2026-08-15-orchestrator-release-readiness/ACTIVATION_READINESS.md`
- `state/tasks/2026-08-23-spectech-alpha-terminology-fix/RESULT.md`
- `state/tasks/2026-08-23-spectech-alpha-terminology-release/RESULT.md`
- `state/tasks/2026-08-23-spectech-full-inventory/INVENTORY.md`
- `state/tasks/2026-08-23-spectech-git-unification/RESULT.md`
- `state/tasks/2026-09-05-orchestrator-activation-guard/ROLLBACK.md`
- `state/tasks/2026-09-05-orchestrator-activation-guard/SECURITY_PRECHECK.md`

The three non-state Markdown whitespace files remain outside this scoped batch.

## Checklist

- [x] Record exact baseline and scope
- [x] Create exact current-worktree and HEAD manifests
- [x] Archive and restore-verify all authorized targets
- [x] Remove only the six fixtures and four large deliverables
- [x] Normalize whitespace in the nine authorized state files
- [x] Verify no other dirty state path changed
- [x] Commit the scoped cleanup
- [ ] Repeat the complete pre-push audit

## Stop conditions

Stop on any missing target, non-regular/symlink target, checksum mismatch, archive
read failure, unexpected path change, or evidence that a fixture is a live queue.
