# Manual-007 — sealed review-only retry

Status: COMPLETE — ACCEPTED / R17_ACCEPT; TRANSFER NOT PERFORMED

## Goal

Repeat only the timed-out independent review of the unchanged manual-007 diff,
using the existing sealed inputs and deterministic policy admission. Do not
launch Codex or change implementation files.

## Fixed subject

- Worktree: `/home/stanislav/agent-runs/orchestrator-worktrees/manual-007-run-log`.
- Base/source commit: `f25e00150258eba2ea89146dfe114c758d462309`.
- Sealed input root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-007-run-log-run/attempt-1/claude/review-inputs`.
- Sealed observed-diff SHA-256:
  `797e4e7406f3dae3c6134275881fd3ee512906e40c0921b3b3c7e4ae58142295`.
- Original failure: Claude exit 124 after 600086 ms; no decision.

## Boundaries

- Review only; Codex must not run.
- No implementation write, source transfer, commit, push, deploy, Gateway,
  cron, systemd, daemon, unattended, dependency, network, or system change.
- Re-verify seal and subject digest before and after each review.
- Initial retry timeout: 900 seconds.
- If policy requires `R15_NEED_FULL_REVIEW`, build a fresh attempt-3 sealed
  review package from the unchanged subject and run one review-only final-full
  leg with the same 900-second timeout.
- Any digest drift, invalid contract, unresolved major, timeout, unknown error,
  or non-terminal policy result means STOP and transfer remains prohibited.

## Checks

- [x] Original sealed inputs and worktree digest verified.
- [x] Initial-full review-only retry admitted by deterministic policy.
- [x] Required final-full review-only leg completed after R15 requested it.
- [x] Terminal decision and residual findings recorded.
- [x] Worktree and source remain unchanged; no orphan process remains.
