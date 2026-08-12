# Deterministic Orchestrator State Machine

This slice implements a pure policy core in `orchestrator_policy.py`.
`decide(task_policy, ledger, execution_report, reviewer_report)` is the only
adjudication entry point. It performs no file, network, subprocess, clock,
environment, random, or LLM access.

Finding-history occurrence identity is the pair
`(review_id, occurrence_id)`. The pair is unique within one finding's history;
an `occurrence_id` may be reused by a different review. Merge is append-only:
an existing pair is retained and never overwritten, and all histories are
emitted in canonical order.

## Outcomes

- `FAILED_INFRA`: exact machine signature IDs are fully allowlisted and both
  total and per-signature infra budgets remain available.
- `REWORK`: deterministic fix or review work is required and the relevant
  budget remains available.
- `ESCALATED`: input binding, replay, stale data, malformed trusted data,
  unknown failure, or exhausted budget requires human coordination.
- `ACCEPTED`: reached only by fall-through after all earlier guards are false.

## Precedence

The implementation follows the safe derivation order:

1. malformed or binding-invalid input;
2. nonce/epoch replay;
3. stale subject or review mismatch;
4. incomplete digest-bound input;
5. fresh policy derivation across infra, gates, findings, evidence, full-review,
   and acceptance rules;
6. terminal-decision equality/idempotence validation, which returns the recorded
   terminal decision only when it exactly equals the freshly derived current
   decision.

Replay is intentionally not a short-circuit before validation. The engine first
re-derives the current safe policy result, then compares any recorded
`terminal_decision` against that result and its current trusted-input digests.

Every decision contains ordered reason codes, directives, budget counters after
the transition, digests of all trusted inputs, the post-merge registry digest
when available, and a deterministic SHA-256 decision digest.

`no_progress_streak` is mechanical. Every decision includes
`progress_identity`, and `ledger.prior_attempts[*].progress_identity` must be
copied from the prior decision output or recomputed from the prior
`execution_report.subject` using this exact public contract:

1. Build the canonical preimage object:
   `{"subject":{"changed_paths":SORTED_CHANGED_PATHS,"tree_digest":TREE_DIGEST}}`.
2. `TREE_DIGEST` is the exact string from
   `execution_report.subject.tree_digest`.
3. `SORTED_CHANGED_PATHS` is the array from
   `execution_report.subject.changed_paths` sorted ascending as strings, with no
   deduplication or path normalization by the identity function.
4. Serialize that object as UTF-8 JSON with lexicographic object-key sorting,
   no insignificant spaces, separators `,` and `:`, and non-ASCII characters
   emitted as UTF-8 rather than escaped.
5. Hash the serialized bytes with SHA-256 and format the identity as
   `sha256:` followed by 64 lowercase hexadecimal characters.

Repeated rework on the same `progress_identity` advances the streak. A changed
identity resets a nonzero streak to `0`. Reaching the configured
`task_policy.budgets.no_progress` boundary escalates with `NO_PROGRESS`.

## Finding Registry

The policy does not calculate reviewer `finding_id` values. It trusts IDs only
after the existing reviewer validator has validated the reviewer contract or
after a compact trusted projection is supplied by the coordinator.

Registry updates are append-only:

- findings are deduplicated by stable `finding_id`;
- effective severity is monotonic;
- reviewer prose and proposed dispositions are display-only and never close,
  waive, downgrade, or accept findings;
- targeted verification may mark an open finding `resolved_verified` only when
  it explicitly lists the finding in `verified_finding_ids` for the current tree;
- any later occurrence reopens the finding and preserves history.

## CLI

The CLI is intentionally thin:

- `--check-schema` validates the two Draft 2020-12 schemas.
- `--fixture PATH` evaluates one policy fixture.
- `--check-fixtures fixtures/policy` validates all fixture expectations.

The CLI parser caps bytes, depth, list length, and mapping cardinality before
schema or policy evaluation.
