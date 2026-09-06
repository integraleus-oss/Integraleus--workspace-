# Tertiary Generated Areas Cleanup

- Owner: Stanislav Pavlovskiy
- Started: 2026-09-06 15:13 MSK
- Execution: current foreground Codex turn; no background job
- Baseline HEAD: `21b32c13ac616071b83fa185c83fe17fa89d2d22`
- Scope order: `artifacts/`, `grill-frames-2/`, `hmi-demo/`, `grill-frames/`, `output/`, `tmp-screens/`
- Excluded: `state/`, supervisor artifacts, message queues/outbox, SQLite and delivery state
- Safety: no replay or resend; tracked, durable, messaging-boundary and ambiguous files stay in place
- Intended archive root: `/home/stanislav/repository-cleanup-archives/2026-09-06-tertiary-generated-areas/`

## Checklist

- [x] Inventory and classify `artifacts/` — retain tracked deliverables and ignored render/evidence files
- [x] Inventory and classify `grill-frames-2/` — archive 59 ignored extracted frames
- [x] Inventory and classify `hmi-demo/` — retain 145 tracked source/demo files
- [x] Inventory and classify `grill-frames/` — archive 9 ignored extracted frames
- [x] Inventory and classify `output/` — retain tracked material, deliverables and configuration backups
- [x] Confirm `tmp-screens/` is empty
- [x] Write exact manifest for 68 proven generated frame files
- [x] Validate regular non-symlink targets and counts
- [x] Verify SHA-256 before and after the move (68/68)
- [x] Record restoration instructions and post-cleanup Git boundary
- [x] Commit only this reviewed cleanup evidence

## Baseline

- Branch: `main`, ahead of `origin/main` by 191 commits.
- Filesystem: 937 GiB total, 625 GiB available, 30% used.
- Pre-existing changes in `skills/safe-repository-cleanup/SKILL.md` and excluded `state/` are not part of this task.
