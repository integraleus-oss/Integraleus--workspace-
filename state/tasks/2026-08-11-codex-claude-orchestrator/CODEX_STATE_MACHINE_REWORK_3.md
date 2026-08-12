# Codex Rework R3: Final-Full Major Findings

Status: IMPLEMENTED_AND_INDEPENDENT_GATES_GREEN
Source review: `reviews/claude-state-machine-final-full.md`
Implementer: fresh local Codex

## Scope

Fix only FF-01 through FF-04 from the final-full review. Edit only files under
`implementation/`. Do not edit completed reviewer-contract schema, validator,
or reviewer tests. Do not commit, install packages, use network, alter runtime,
or use danger mode.

## Required fixes

1. FF-01: make public `decide()` total for deeply nested already-parsed inputs.
   Enforce the same structural depth/cardinality/string safety boundary before
   any digest/deepcopy recursion. A hostile value must yield deterministic
   `ESCALATED/R01_BINDING`, never raise `RecursionError`.
2. FF-02: make `no_progress` mechanically effective. Define and document a
   deterministic progress identity using explicit trusted data already in the
   ledger/current subject. Validate `prior_attempts` strictly enough to avoid
   prose judgment. `budgets_after.no_progress_streak` must advance for repeated
   no-progress rework, reset on demonstrable changed progress identity, and
   trigger `NO_PROGRESS` at the stated boundary. Add a two-successive-decision
   regression that propagates `budgets_after`; do not merely hand-set the
   terminal counter. Keep behavior pure and deterministic.
3. FF-03: align `orchestrator-state-machine.schema.json` with the implemented
   paired optional `execution_report.payload` and `payload_digest` contract.
   A schema-wrapped valid fixture containing a correctly bound payload must
   pass through the CLI, while missing/mismatched pairs fail closed.
4. FF-04: correct `STATE_MACHINE.md` to state the actual safe precedence:
   structural/binding/replay/stale/incomplete and fresh policy derivation occur
   before terminal-decision equality/idempotence validation. Do not weaken code
   back to replay-first behavior.

## Regression and evidence requirements

- Exact deep-nesting reproductions under `ledger.prior_attempts` and
  `execution_report.payload`, both through `decide()`.
- Multi-round no-progress test using prior decision outputs and explicit
  trusted prior-attempt identity; changed subject/progress identity resets the
  streak.
- Schema/CLI fixture test for paired payload plus tests for missing partner and
  wrong digest.
- A test or machine-checkable assertion that documented precedence agrees with
  the safe implementation order where practical.
- Preserve all previous SM-01..SM-07 regressions.
- Run focused tests, all tests, both schema self-checks, fixture checks,
  `py_compile`, and whitespace/diff checks. Append exact results and changed
  files to `implementation/EVIDENCE.md`.

If a requested fix conflicts with an existing acceptance criterion, stop and
report the conflict instead of silently changing policy.
