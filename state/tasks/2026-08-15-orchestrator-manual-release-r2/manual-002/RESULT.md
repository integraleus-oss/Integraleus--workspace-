# Manual-002 result

Status: `ESCALATED`; implementation retained; source transfer forbidden

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

The first retry packet was rejected before any agent launch with
`BuilderError: project baseline is not clean`, because it pointed at the
retained implementation worktree. This consumed no Codex or Claude attempt.
The corrected retry uses a new clean detached worktree and a new evidence root;
the failed preflight evidence remains preserved.

## Corrected r3 run

- Clean detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-002-external-read-contract-r3`.
- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-002-external-read-contract-run-r3`.
- Codex: `OK`, 256463 ms; only the three allowed paths changed.
- Claude initial review: `OK`, 503863 ms.
- The initial verdict was rejected by the deterministic contract validator and
  consumed the one allowed contract-only repair.
- The repaired verdict still violated the sealed schema by adding unsupported
  fingerprint property `normalized_symbol_placeholder`.
- Terminal managed result: `ESCALATED`; no further retry was launched.
- Cycle-result SHA-256:
  `58614573aa36aeff9e540f115b361d53e6e4f5db6e66cd83bbb800d16c9b17db`.
- Independent `npm test`: PASS — 10 tests, 0 failures.
- Independent `git diff --check`: PASS.

## Substantive unadmitted review evidence

Although the verdict was not admissible and cannot authorize policy action, it
contained one credible major observation that must be resolved in a new task:
the runtime accepts IPv4-embedded/mapped IPv6 forms through `node:net.isIP`
(for example `::ffff:192.0.2.1`), while the hand-written schema IPv6 pattern
cannot match an address containing both colons and a dotted IPv4 tail. Runtime
and schema therefore do not yet define one grammar.

Additional advisory observations were inconsistent IP literal
canonicalization, lack of an executable runtime-versus-schema agreement test,
and mutable grant/allowedExternal containers around frozen arrays.

Because the repair budget is exhausted and a major contract divergence remains,
neither r1 nor r3 implementation is eligible for source transfer. A new bounded
task packet and fresh full review are required.
