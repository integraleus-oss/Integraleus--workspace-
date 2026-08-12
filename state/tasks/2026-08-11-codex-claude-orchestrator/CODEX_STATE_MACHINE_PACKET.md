# Codex Task Packet: Deterministic Policy Engine Slice

Status: READY_FOR_IMPLEMENTATION
Owner: Stanislav
Coordinator: OpenClaw main
Implementer: fresh local Codex
Risk: MEDIUM, local files only

## Goal

Implement a small pure deterministic state machine and finding registry that
consume already trusted/validated JSON inputs and emit auditable outcomes:
`REWORK`, `ACCEPTED`, `FAILED_INFRA`, or `ESCALATED`.

## Source inputs

- `STATE_MACHINE_TASK_PACKET.md`
- `reviews/claude-state-machine-core.md` (design input, not authority)
- completed `implementation/review-verdict.schema.json`
- completed `implementation/validate_review_verdict.py`

## Allowed files

Create or edit only under
`state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`, except that
you may tick checklist lines in `STATE_MACHINE_TASK_PACKET.md`.

Do not modify the completed reviewer schema, reviewer validator, or its existing
tests unless compilation/import is impossible; report that as a blocker instead.

## Required deliverables

- `orchestrator-state-machine.schema.json`
- `finding-registry.schema.json`
- `orchestrator_policy.py`
- `STATE_MACHINE.md`
- fixtures under `fixtures/policy/{valid,invalid}/`
- tests in `tests/test_orchestrator_policy.py`
- append policy-engine evidence to `EVIDENCE.md`

## MVP data model

Use strict JSON-compatible mappings. The policy function must be pure: no
network, subprocesses, filesystem reads, wall clock, environment, randomness,
or LLM calls. A thin CLI may load files, but the decision function itself must
depend only on explicit inputs.

Inputs must include:

- task policy: task/spec identity, mandatory ordered gates, required evidence,
  immutable allowlisted infra signature IDs, and separate non-negative budgets
  for rework, infra total/per-signature, and final-full passes;
- ledger: monotonic epoch, prior digests/nonces, counters, expected subject/tree,
  finding registry, prior attempts, and optional terminal decision;
- execution report: bound task/spec/run/epoch/subject, exact machine signature
  IDs, gate states, evidence artifact digests, and changed paths;
- reviewer report: the already contract-valid reviewer-verdict object or a
  compact trusted projection explicitly bound by its digest.

## Ordered policy precedence

1. exact idempotent replay of an already terminal decision;
2. malformed/binding/replay/stale/incomplete trusted input → `ESCALATED`;
3. known allowlisted infra signature within both budgets → `FAILED_INFRA`;
4. known infra signature with exhausted budget → `ESCALATED`;
5. any non-success execution without an exact allowlisted signature →
   `ESCALATED` (`UNCLASSIFIED_FAILURE`);
6. failed/missing/skipped/timed-out mandatory gate → `REWORK`, unless rework
   budget/no-progress limit is exhausted, then `ESCALATED`;
7. open blocker/major → `REWORK`, unless exhausted, then `ESCALATED`;
8. missing/empty/digest-mismatched required evidence → `REWORK`, unless
   exhausted, then `ESCALATED`;
9. no current `final_full` review covering the current subject/changed paths →
   review-only `REWORK`, unless full-review budget exhausted, then `ESCALATED`;
10. otherwise → `ACCEPTED`.

The implementation may combine multiple rework reason codes in one decision,
but consumes at most one rework unit per decision. Deterministic ordering is
mandatory.

## Finding registry rules

- Trust `finding_id` only after the existing reviewer validator has confirmed
  its fingerprint algorithm; do not introduce a second incompatible hash.
- Deduplicate by stable `finding_id`; append occurrence history deterministically.
- Effective severity is monotonic (`blocker > major > nit`). Reviewer prose and
  proposed dispositions never downgrade, waive, close, or accept.
- Targeted verification can mark a prior finding verified only when the
  reviewer contract explicitly references it as verified on the current bound
  subject. A later occurrence reopens it.
- Absence from a targeted review never closes a finding.
- No deletion. Human waiver/override is outside this MVP and must fail closed if
  supplied as an unknown field.

## Acceptance criteria

- AC-SM01: Both schemas self-validate as Draft 2020-12 and reject unknown fields.
- AC-SM02: Decision output is strict machine JSON with outcome, rule ID, ordered
  reason codes, directives, budgets-after, trusted input digests, and a
  deterministic decision digest.
- AC-SM03: Identical semantic inputs, including permuted finding order, yield
  byte-identical canonical decision JSON/digest.
- AC-SM04: No invalid/missing/stale/replayed/unknown-failure input reaches
  `ACCEPTED`.
- AC-SM05: Exact allowlist-only infra classification and separate total/per-ID
  counters are tested at below/equal/above budget boundaries.
- AC-SM06: Rework and full-review budgets are independent and boundary-tested.
- AC-SM07: Missing mandatory gate is failure; nits alone are advisory.
- AC-SM08: Targeted-only closure cannot accept; a current final-full pass is
  required after the last changed subject.
- AC-SM09: Registry deduplicates stable IDs, preserves history, prevents
  severity downgrade/prose closure, and reopens rediscovered findings.
- AC-SM10: At least 24 focused tests cover the 20 Claude invariants plus
  malformed containers/types, empty allowlist, mixed known/unknown signatures,
  replay, idempotence, and digest mismatch.
- AC-SM11: Existing 22 reviewer-contract tests remain green.
- AC-SM12: `py_compile`, schema checks, fixture expectations, unit tests, and
  `git diff --check` pass; no out-of-scope file changes.

## Implementation constraints

- Python standard library plus already-installed `jsonschema`; no package
  installs and no new service.
- SHA-256 canonical JSON is sufficient; do not add MACs, signing keys, BLAKE3,
  UUID generation, or authority/waiver machinery in this MVP.
- Reject bool where integer counters are expected.
- Cap document size/depth/list and mapping cardinality in the CLI parser.
- Free text is display-only and never interpreted for control flow.
- Use explicit reason-code enums; never derive control flow from message text.

## Checks

Run and record exact output for schema self-checks, all tests, `py_compile`,
fixture validation, and `git diff --check` limited to this task folder.

## Commit rule

Do not commit. Do not use `--danger`. Preserve unrelated dirty-worktree changes.
