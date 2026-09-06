# Generated Areas Cleanup

- Owner: Stanislav Pavlovskiy
- Started: 2026-09-06 14:51 MSK
- Execution: current foreground Codex turn; no background job
- Baseline HEAD: `cd1ad69ab03206836c2f51313ca1ba51c4230c80`
- Scope order: `out/`, `media/`, `outbound/`, `tmp/`, `exports/`, `tmp_djvu_check/`
- Excluded: `state/`, supervisor artifacts, message outbox/queues, SQLite and delivery state
- Safety: no replay or resend; ambiguous and durable files stay in place
- Archive root: `/home/stanislav/repository-cleanup-archives/2026-09-06-generated-areas/`

## Checklist

- [x] Inventory and classify `out/` — retain: current/ambiguous deliverables
- [x] Inventory and classify `media/` — retain: messaging media boundary
- [x] Inventory and classify `outbound/` — retain: delivery evidence and SQLite boundary
- [x] Inventory and classify `tmp/` — archive 3 proven temporary files
- [x] Inventory and classify `exports/` — retain: current deliverables
- [x] Inventory and classify `tmp_djvu_check/` — archive 23 scratch files
- [x] Write exact manifest for 26 proven archival targets
- [x] Validate regular non-symlink files and target counts
- [x] Record pre-move SHA-256 checksums
- [x] Move while preserving workspace-relative paths
- [x] Verify post-move SHA-256 and archive readability
- [x] Record restoration instructions and post-cleanup Git boundary
- [x] Commit only the reviewed cleanup evidence

## Baseline

- Branch: `main`, ahead of `origin/main` by 189 commits
- Workspace filesystem: 937 GiB total, 625 GiB available, 30% used
- Repository size: 9.5 GiB; `.git`: 651 MiB
- Pre-existing dirty paths under excluded `state/` are intentionally untouched.
