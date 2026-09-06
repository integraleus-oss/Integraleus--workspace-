# Execution supervisor dashboard cleanup

Owner: Stanislav Pavlovskiy
Started: 2026-09-06 12:01 MSK
Execution: current foreground Codex turn
Expected output: reviewed dashboard source commit, externally archived generated
previews with hash proof, and updated workspace boundary

## Checklist

- [x] Capture Git, size, and file snapshot
- [x] Review structure and dependencies
- [x] Scan candidate files for secret material without printing values
- [x] Run tests and smoke checks
- [x] Archive only proven generated previews with exact manifest and SHA-256
- [x] Commit source/docs/tests separately
- [x] Record post-cleanup worktree boundary
- [x] Inventory and commit untracked task evidence by date
- [x] Preserve notification/outbox-related and ambiguous groups untouched

## Safety boundary

- Leave all historical supervisor evidence/state/outbox files untouched.
- Do not inspect or mutate message queues, SQLite delivery data, notifications,
  or delivery state.
- Never replay or resend messages.
- Leave ambiguous files in place.
