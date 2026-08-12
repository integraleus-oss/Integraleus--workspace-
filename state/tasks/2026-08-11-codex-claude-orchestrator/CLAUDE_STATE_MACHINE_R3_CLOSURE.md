# Claude targeted closure — state-machine R3

## Role

Act as a fresh, read-only adversarial reviewer. Verify only whether the current
tree closes findings FF-01 through FF-04 from
`reviews/claude-state-machine-final-full.md`. Do not edit files and do not
expand scope into unrelated nits.

## Inputs

- `reviews/claude-state-machine-final-full.md`
- `CODEX_STATE_MACHINE_REWORK_3.md`
- `implementation/orchestrator_policy.py`
- `implementation/orchestrator-state-machine.schema.json`
- `implementation/STATE_MACHINE.md`
- `implementation/tests/test_orchestrator_policy.py`
- `implementation/fixtures/`

## Required checks

1. FF-01: public `decide(...)` is total for deeply nested already-parsed inputs
   and fails closed with a machine decision rather than `RecursionError`.
2. FF-02: consecutive no-progress attempts advance the configured streak,
   reset on genuine progress, and deterministically escalate at the budget.
3. FF-03: schema and implementation agree on optional `payload` and
   `payload_digest`, including pairing and digest mismatch handling.
4. FF-04: documentation precedence matches the safe implementation order.
5. Confirm exact regression tests exist and are meaningful.

## Verdict

Return `TARGETED_PASS` only if all four findings are closed with no blocker or
major regression caused by these fixes. Otherwise return `TARGETED_REWORK` and
list only blocker/major findings with severity, file/line, failure scenario,
reproduction, and evidence.
