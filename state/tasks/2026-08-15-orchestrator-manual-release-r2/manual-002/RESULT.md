# Manual-002 result

Status: `ESCALATED`; implementation retained; review infrastructure retry pending

## First run

- Codex implementation: `OK`, 281487 ms.
- Changed only `schemas/agent-pack.schema.json`, `src/core/policy.js`, and
  `test/policy.test.js`.
- Claude launch: `FAILED`, exit `1`, 83023 ms.
- Wrapper evidence reported the explicit known condition: Claude session limit
  reached, reset scheduled for 20:30 Europe/Moscow.
- Live review result: `FAILED_LAUNCH`; no reviewer verdict or policy acceptance
  was produced.
- Managed terminal result: `ESCALATED`; no automatic continuation occurred.
- Cycle-result SHA-256:
  `aaf2b10e88953dbcf70cdb904b0c778fe65ba4a0bc0cc4a3e4506e0c0dd3fd62`.

## Independent implementation checks

- `npm test`: PASS — 11 tests, 0 failures.
- `git diff --check`: PASS.
- Source repository remains clean at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.

## Retry boundary

One manual retry is permitted only after the declared session reset and must
use a new evidence root. It may inspect or correct only the same three allowed
files. A repeated Claude limit/failure, path expansion, or any unknown failure
is terminal. No result may be transferred without `R17_ACCEPT` and a separate
explicit source-transfer decision.
