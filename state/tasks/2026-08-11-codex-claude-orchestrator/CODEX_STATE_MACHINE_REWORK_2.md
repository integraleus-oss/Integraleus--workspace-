# Codex Rework Packet: State Machine Targeted R2

Status: READY
Implementer: fresh local Codex, workspace-write sandbox
Scope: only policy-engine files under `implementation/`
Commit: forbidden

## Confirmed input

Targeted report:
`reviews/claude-state-machine-targeted-r1.md`.

The coordinator locally reproduced the remaining SM-07 major: two valid
ledgers differing only in an untouched registry record's `history` order have
identical `input_digests`, but different `registry_digest_after` and
`decision_digest`, including on the `ACCEPTED` path.

## Required fix

Make merged finding-registry output use the same order-insensitive semantics as
the trusted input digest for every record, including records untouched by the
current reviewer report. Semantically equivalent history permutations must
produce byte-identical decision JSON and digests.

Also make the new registry validator and merge path agree on occurrence
identity. Choose and document one deterministic invariant:

- `occurrence_id` is globally unique within a finding history; or
- `(review_id, occurrence_id)` is unique.

The implementation must never emit a registry that its own next invocation
rejects solely because a later review reused an otherwise permitted identifier.
Do not weaken validation or permit duplicate history entries to overwrite one
another.

## Required regression

Add an exact regression with one untouched `resolved_verified` record whose two
valid history entries are reversed. Assert:

- both decisions have the same outcome/rule;
- `input_digests` are identical;
- `registry_digest_after` is identical;
- `decision_digest` and complete canonical decision JSON are identical.

Add a cross-review occurrence-ID regression matching the chosen invariant and
prove that an engine-emitted registry validates on the next invocation.

Run focused policy tests, all tests, both schema self-checks, policy fixtures,
`py_compile`, and whitespace checks. Append exact evidence to
`implementation/EVIDENCE.md`. Do not edit the completed reviewer-contract
schema/validator/tests, task packets, review reports, shared files, or files
outside `implementation/`. Do not commit and do not use danger mode.
