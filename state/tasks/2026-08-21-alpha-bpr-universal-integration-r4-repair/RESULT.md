# R4 Repair Result

Status: `ESCALATED / R12_FINDINGS_EXHAUSTED`

The sealed packet
`sha256:a97cf78ff063080dcec27f08aa57d902b4bad4c643f56194e16313467d180195`
ran under the controlled-manual production cycle.

## Execution

- Attempt 1: Codex completed; focused gate failed with an
  `IMPLEMENTATION_FAILURE` (`CS0120`).
- The Trusted Builder converted that failure into the single allowed bounded
  repair attempt.
- Attempt 2: Codex completed; all sealed gates passed.
- Focused tests: 25/25, minimum 20.
- Full tests: 365/365, minimum 360.
- Restore, build, and `git diff --check`: PASS.
- Build: 0 warnings, 0 errors.
- No `bin/obj` directories exist in the repair worktree.

## Independent review

- Review outcome: `ESCALATED`, rule `R12_FINDINGS_EXHAUSTED`.
- Open findings: 1 major, 2 nit.
- AC-1, AC-2, AC-4, AC-5, and AC-6: satisfied.
- AC-3: partially satisfied.

Major finding:

- `IntegrationProfileValidator.TryNormalizeValue` routes `Int64` values through
  binary64 even for the identity transform. Values above 2^53 may silently
  round, while `long.MaxValue` may be rejected as overflow. The reviewer
  requires exact integer identity handling and focused boundary tests.

Nit findings:

- `FixtureIntegrationProfileStore` duplicates JSON loading logic and one
  overload omits the name guard.
- ADR-009 consequences do not yet list the new fail-closed behaviours.

The initial reviewer response required one contract-only retry. The retry used
the same sealed inputs and changed no product code.

## Isolation

- The implementation remains only in the isolated repair worktree at baseline
  `72b06e72738fa909c3e801394885da7afba32ec4`.
- Canonical Alpha BPR remains clean at `b9e6377`.
- Transfer, commit, push, deploy, VM/service/Gateway actions, credentials, and
  private endpoints were not used.
- The repair is not accepted and must not be transferred.

## Next action

Prepare a new sealed closure-repair packet limited to the one major and two nit
findings. Re-run the gates and independent closure review before any transfer.
