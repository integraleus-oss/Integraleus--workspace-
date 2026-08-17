# Manual pilot 001 review-only retry result

Status: ESCALATED; TRANSFER PROHIBITED

- Codex was not launched and the implementation was not modified.
- Pre/post diff SHA-256 matched:
  `98f3f457cfdb83fb97f6e1af97a0c13ad57774891187a675537ac891b7dccf51`.
- The original seal verified against the unchanged worktree.
- Claude initial response required a format-only retry.
- The extracted verdict then failed semantic validation because multiple
  criteria/limitation references named evidence IDs absent from all evidence
  carriers.
- The single bounded contract repair removed that failure but introduced a new
  schema violation: `findings[3].title` exceeded its maximum length.
- No policy outcome (`R17_ACCEPT` or otherwise) was admitted.
- Repeated implementation checks passed: `npm test` 46/46 and
  `git diff --check` PASS.
- Source `/home/stanislav/projects/home-agent-factory` remained clean at
  `8985b8e`; detached worktree still contains exactly the three allowed files.
- No Claude/Codex process remains. No transfer, source commit, push, deploy,
  Gateway, systemd, cron, unattended, dependency, or external-system change
  was performed.

Next gate: repair reviewer transport/contract guidance with regression tests.
Do not re-review or transfer this implementation until that separate defect is
closed and a newly authorized review produces a valid admitted decision.
