# Manual-007 — run-log path and audit contract

Status: ESCALATED; TRANSFER PROHIBITED

## Goal

Harden run-log file creation and align the JSONL event runtime contract with
`run-log.schema.json` in one isolated, independently reviewed slice.

## Fixed point and scope

- Risk: MEDIUM local filesystem/audit code.
- Source: `/home/stanislav/projects/home-agent-factory`.
- Fixed commit: `f25e00150258eba2ea89146dfe114c758d462309`.
- Detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-007-run-log`.
- Run evidence:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-007-run-log-run`.
- Allowed files: `src/core/run-log.js`, `schemas/run-log.schema.json`, and
  `test/run-log.test.js`.
- Forbidden: every other source path, dependency/network changes, source
  transfer, commit, push, deploy, Gateway, cron, systemd, daemon, unattended
  execution, and system changes.

## Acceptance criteria

- [ ] One exported frozen run-log grammar is used by runtime and pinned exactly
  in the complete schema subtree.
- [ ] `runId` cannot contain separators, traversal, control characters, or
  names outside the accepted generated-ID grammar.
- [ ] `event` is a bounded ASCII identifier; `now` is a valid Date; `data` is a
  detached JSON object accepted by the schema.
- [ ] All validation and serialization complete before `mkdir` or append, so
  rejected input creates no directory, file, or partial line.
- [ ] A valid append writes exactly one newline-terminated JSON object to the
  expected `runs/YYYY-MM-DD/<runId>.jsonl` path, and repeated appends preserve
  valid JSONL records.
- [ ] Tests cover creation, traversal/control rejects, invalid date/event/data,
  no-side-effect failures, schema agreement, and successful/repeated writes.
- [ ] `npm test` and `git diff --check` pass; exactly three allowed files change.

## Budgets and stop conditions

- Maximum two Codex implementations and one review-only final-full Claude leg.
- Standard one format repair and one contract-only repair per review.
- Gate timeout 60 seconds; agent timeout 600 seconds.
- Unknown failure, forbidden path, unresolved major, exhausted budget,
  invalid verdict, or interruption means STOP without transfer.

## Checklist

- [x] Task packet and boundaries created before autonomous work.
- [x] Clean detached worktree created at the fixed commit.
- [x] Managed production cycle completed with terminal `ESCALATED`.
- [x] Evidence, paths, tests, side effects, and source state independently checked.
- [x] Result recorded; transfer is prohibited.
