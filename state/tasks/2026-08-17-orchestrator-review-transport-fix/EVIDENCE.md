# Evidence

Status: COMPLETE

- Source failures: dangling evidence references and `findings[].title` over 160 characters.
- Capability-grant diff is frozen at SHA-256 `98f3f457cfdb83fb97f6e1af97a0c13ad57774891187a675537ac891b7dccf51`.
- Targeted integration tests: 16/16 PASS.
- Integration runtime tests: 121/121 PASS.
- Sealed policy-core tests: 87/87 PASS.
- `git diff --check`: PASS.
- Claude `claude-review-diff` and `claude-review-slice-readonly` both exited 0
  with empty output; neither is accepted as review evidence.
- Independent Codex review of `b8711ba` found one P2: normalization overwrote
  reviewer-authored criterion notes. Fixed by preserving and appending to notes.
- Second Codex review through `1c1e98d` found one P2: a non-list evidence carrier
  could raise `TypeError`. Fixed with list guards and a contract-failure regression.
- Third Codex review through `0abe47e` found the same risk on top-level malformed
  collections. Fixed all traversals with a non-mutating list guard and regression cases.
- Fourth Codex review through `5e4fb1e` found one P1 fail-open: malformed evidence
  IDs could be filtered out. Normalization now accepts only schema-shaped IDs and
  leaves every malformed array untouched for contract rejection.
- The first post-fix run exposed an invalid regression fixture (`ev_missing_001`);
  corrected to a schema-shaped but undefined ID before final verification.
- Fifth Codex review through `5bcde6a` found one P2: appending a normalization
  suffix could overflow the 2,000-character notes limit. Existing notes are now
  preserved byte-for-byte; the separate normalization log carries the reason.
- Final independent Codex review through `435278e`: zero findings; patch correct;
  confidence 0.91.
- Final transport verification: integration 125/125 PASS; policy core 87/87 PASS;
  `git diff --check` PASS.
- Fresh sealed capability-grant review root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant-review-retry-2`.
- Fresh review launch: OK, no format or contract retry, contract-valid verdict.
- Policy outcome: `REWORK / R11_OPEN_FINDINGS`.
- Findings: 1 blocker, 0 major, 2 nit. Blocker: runtime can emit a
  `modelPolicy` shape rejected by the new capability-grant schema.
- Post-review diff SHA-256 remains
  `98f3f457cfdb83fb97f6e1af97a0c13ad57774891187a675537ac891b7dccf51`;
  exactly the same three files are modified; implementation tests 46/46 PASS.
- Source `home-agent-factory` remains clean at `8985b8e`. No transfer, source
  commit, push, deploy, Gateway, systemd, cron, or background process occurred.
- Capability-grant transfer remains prohibited pending a separate authorized
  REWORK implementation and subsequent review.
