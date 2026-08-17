# Evidence

Status: IN PROGRESS

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
