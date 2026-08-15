# Manual-003 result

Status: `ESCALATED`; review/repair budget exhausted; source transfer forbidden

Attempt 1 produced a three-file implementation and passed independent `npm
test` (11/11) and `git diff --check`. The final Claude leg timed out after 600
seconds without a verdict because it repeatedly requested commands denied by
the read-only wrapper. The managed result was correctly `ESCALATED`; the diff
is not accepted or transferable.

## Fresh infrastructure retry

- Clean worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-003-external-read-agreement-r2`.
- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-003-external-read-agreement-run-r2`.
- Codex changed only `schemas/agent-pack.schema.json`, `src/core/policy.js`, and
  `test/policy.test.js`.
- Independent `npm test`: PASS — 10 tests, 0 failures.
- Independent `git diff --check`: PASS.
- Claude returned a full review, but its first verdict exceeded a sealed field
  length and required the one allowed contract-only repair.
- The repaired review was rejected by the deterministic projection with
  `full review has incomplete criteria coverage`.
- Terminal managed result: `ESCALATED`; no further attempt is permitted.
- Attempt-1 cycle-result SHA-256:
  `aaf2b10e88953dbcf70cdb904b0c778fe65ba4a0bc0cc4a3e4506e0c0dd3fd62`.
- Retry cycle-result SHA-256:
  `c9ffef98663344e521df8694751619b14e0147d921a682fe8454888009437e8f`.

## Substantive unadmitted review evidence

The verdict was not admissible and cannot authorize policy action, but it
contained two credible major observations that a future bounded task must
resolve:

1. The runtime/schema corpus uses a hand-written partial JSON Schema evaluator
   that silently ignores unsupported keywords. It therefore does not prove
   agreement for the complete schema contract.
2. `grant.modelPolicy` is only a shallow frozen copy, so nested caller-owned
   objects could remain shared and mutable after compilation.

The review also recorded a test-coverage nit: explicit reject cases should be
added for URLs, paths, ports, credentials, wildcards, whitespace/newlines,
zone-id IPv6, and bracketed IPv6.

## Decision

Neither attempt is eligible for source transfer. The next task, if authorized,
must use a real existing schema validator or a fail-closed complete keyword
check, deep-copy/freeze nested grant policy state, extend the rejection corpus,
and receive a new admissible full review.

The source repository remains clean at
`3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`. No target-project source
transfer, commit, push, deploy, Gateway, cron, systemd, daemon, unattended,
network, dependency, or system change occurred.
