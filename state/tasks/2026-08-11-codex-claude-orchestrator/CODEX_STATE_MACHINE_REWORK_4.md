# Codex Rework R4: Targeted Closure Majors

Status: READY
Source review: `reviews/claude-state-machine-r3-closure.md`
Implementer: fresh local Codex, workspace-write sandbox

## Scope

Fix only R3-01 and R3-02 from the targeted R3 closure. Edit only files under
`implementation/`. Do not commit, install packages, use network, alter runtime,
or use danger mode. Preserve all prior behavior and regressions.

## Required fixes

1. R3-01: make the progress identity a public, machine-usable part of the
   deterministic contract. The exact canonical preimage, serialization, hash
   prefix, and fields must be specified without prose ambiguity. A coordinator
   must be able to construct `ledger.prior_attempts[*].progress_identity` from
   public output/data without importing a private helper. Keep validation
   strict and ensure repeated identical subjects advance no-progress while a
   genuinely changed subject resets it.
2. R3-02: replace the weak deep-input regression with discriminating tests.
   Use structurally valid hostile values deep enough to reproduce the old
   `RecursionError` path (around 3000 levels), through public `decide()`, under
   both `ledger.prior_attempts` and paired `execution_report.payload` fields.
   Tests must fail if the input-limit guard is removed or digesting is moved
   outside the protected path. Fix the reset test so it begins with a streak
   of at least 1 and proves changed progress identity resets it to 0.

## Acceptance criteria

- The public contract exposes or deterministically derives the exact progress
  identity used by policy; documentation and implementation agree.
- Two successive same-identity decisions advance and reach the configured
  no-progress boundary; a changed identity resets a nonzero streak.
- Both exact 3000-level public-`decide()` regressions return a machine decision
  and cannot pass solely due to unrelated schema errors.
- Focused and full tests, both schema self-checks, fixture checks,
  `py_compile`, and whitespace/diff checks pass.
- Append exact evidence and changed files to `implementation/EVIDENCE.md`.
- No files outside `implementation/` changed and no commit created.

If exposing the identity conflicts with an existing schema or immutable-output
contract, stop and report the conflict rather than inventing a bypass.
