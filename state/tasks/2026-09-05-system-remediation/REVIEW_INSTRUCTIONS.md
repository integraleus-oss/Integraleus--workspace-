Review the supplied OpenClaw worktree diff for correctness and regressions.

Invariant: retained terminal delivery tombstones (`completed_permanent` and
`completed_bounded`) are settled ownership/deduplication records, not active
dead letters. Health must still report ordinary failed entries, including
legacy rows with no recovery state and settlement-pending failures.

Check SQL three-valued NULL semantics, test coverage, naming, and whether the
fix belongs in the canonical health-count query. Report actionable findings
only; explicitly say when none remain.
