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

- `live_review_cycle.py` now appends one explicit control-character transport
  invariant to the initial prompt; all bounded retry prompts inherit it without
  duplication. It gives safe textual replacements for both newlines and tabs.
- The validator and extraction logic were not relaxed; there is no sanitizer or
  silent rewriting path.
- The regression injects a decoded `U+0009` into the contract-repair candidate,
  verifies the candidate contains the tab, and proves the bounded format retry
  reaches an admissible decision without carrying the tab forward. It also pins
  guidance presence on initial, format-only, contract-only, and contract-repair
  format-only prompts.

## Independent commit review

- Post-commit review of `bb14bbc` found the controller wording mechanically
  correct and confirmed no validator relaxation.
- It correctly identified that the first version tested prompt substrings but
  did not reproduce decoded `U+0009`, omitted controller-level initial-launch
  guidance, did not prescribe a tab replacement, and duplicated guidance on the
  final retry.
- All four findings were addressed in the follow-up change described above.

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

## Post-review real-project smoke r4

- Fresh detached worktree again started from clean `3d9c27e`; packet validation
  passed and Codex stayed within the same two allowed paths.
- The initial verdict reached deterministic contract repair. The repaired
  verdict passed strict transport and schema validation; no decoded control
  character failure occurred.
- Admission then failed closed at the semantic layer because the reviewer
  referenced four evidence IDs absent from its evidence objects
  (`bad_evidence_reference`). Managed terminal status: `ESCALATED`, one Codex
  attempt, no policy acceptance.
- This is a precise reviewer-content residual blocker, not a transport failure.
  The accepted r3 result remains the successful terminal proof; r4 proves the
  post-review controller change removed the observed control-character edge
  while preserving semantic fail-closed behavior.
- Retained run:
  `/home/stanislav/agent-runs/orchestrator-worktrees/home-agent-factory-real-smoke-r4-run`.
