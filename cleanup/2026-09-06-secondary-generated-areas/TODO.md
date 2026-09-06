# Secondary Generated Areas Cleanup

- Owner: Stanislav Pavlovskiy
- Started: 2026-09-06 15:06 MSK
- Execution: current foreground Codex turn; no background job
- Baseline HEAD: `57ccdbffce11edf791dfee5361fac04518483c14`
- Scope order: `site_images/`, `generated/`, `.venv/`, `outgoing/`
- Excluded: `state/`, supervisor artifacts, message queues/outbox, SQLite and delivery state
- Safety: no replay or resend; durable, messaging-boundary and ambiguous files stay in place
- Intended archive root: `/home/stanislav/repository-cleanup-archives/2026-09-06-secondary-generated-areas/`

## Checklist

- [x] Inventory and classify `site_images/` — retain imported user/media corpus
- [x] Inventory and classify `generated/` — retain 13 tracked sources; archive 96 ignored outputs
- [x] Inventory and classify `.venv/` — retain tracked environment with symlinks
- [x] Inventory and classify `outgoing/` — retain messaging/delivery boundary
- [x] Write exact manifest for 96 proven generated outputs
- [x] Validate regular non-symlink targets and counts
- [x] Verify SHA-256 before and after the move (96/96)
- [x] Record restoration instructions and post-cleanup Git boundary
- [x] Commit only this reviewed cleanup evidence

## Baseline

- Branch: `main`, ahead of `origin/main` by 190 commits.
- Filesystem: 937 GiB total, 625 GiB available, 30% used.
- Pre-existing changes in `skills/safe-repository-cleanup/SKILL.md` and excluded `state/` are not part of this task.
