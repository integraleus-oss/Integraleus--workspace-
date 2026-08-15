# Evidence

Status: accepted

## Baseline

- Orchestrator baseline commit: `f10d8f5`.
- Existing unrelated dirty files were present at intake and are out of scope.
- Prior real-project smoke failed closed after the final bounded reviewer retry
  produced an exact JSON object containing decoded `U+0009`.

## Checks

- Focused live-cycle tests: 12/12 PASS.
- Full integration suite: 83/83 PASS.
- Core policy/contract suite: 84/84 PASS.
- `py_compile`: PASS.
- Main-workspace scoped `git diff --check`: PASS.

## Implementation

- `live_review_cycle.py` now appends the same explicit control-character
  transport invariant to initial format-only, contract-only, and
  contract-repair format-only retries.
- The validator and extraction logic were not relaxed; there is no sanitizer or
  silent rewriting path.
- Regression assertions verify the invariant is present in all three retry
  prompts.

## Real-project smoke r3

- Fresh detached worktree created from clean `home-agent-factory` baseline
  `3d9c27e`; source project remained clean.
- Codex changed only `src/cli/factory.js` and `test/cli.test.js`.
- Sealed gates all returned exit 0: `npm test`, `pack list`, `pack show
  private-archive-rag`, and `git diff --check`.
- Additional direct `node --test test/cli.test.js`: 3/3 PASS.
- Managed policy chain: attempt 1 `R15_NEED_FULL_REVIEW`; attempt 3
  `SKIPPED_REVIEW_ONLY` and `R17_ACCEPT`. No second Codex attempt occurred.
- Final managed result: `ACCEPTED`, `attempts_used: 2` (one implementation leg
  plus one review-only final-full leg).
- Retained run:
  `/home/stanislav/agent-runs/orchestrator-worktrees/home-agent-factory-real-smoke-r3-run`.

## Boundary

The accepted application change remains only in the detached smoke worktree.
It was not copied, committed, pushed, or deployed in the source project.
