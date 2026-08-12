# Claude Contract Design Assessment

## Outcome

Accepted as a strong design input, not as final executable truth.

Claude completed the requested bounded no-tools fresh-session review and
returned:

- a strict JSON Schema 2020-12 draft;
- valid and invalid examples;
- a layered boundary between transport, schema, semantics, ledger, and state;
- 30 deterministic invariants;
- 40 schema-level and 40 policy-level adversarial cases;
- 10 unresolved design questions.

## Strong points to preserve

- The reviewer document is an observation record, not a decision record.
- No authoritative acceptance/state-transition field is representable.
- Missing or invalid output fails closed.
- Severity floors and blocker/major evidence obligations are structural.
- Finding and occurrence identity are separated.
- Reviewer output cannot create human approval or final resolution.
- Infrastructure fields report symptoms only; policy classifies them.
- Targeted verification cannot claim full coverage or acceptance.
- Transport checks such as duplicate keys and trailing bytes are explicitly
  separated from JSON Schema validation.

## Decisions for implementation slice

Implement the schema and validator as a bounded first slice. Do not implement
the full state machine yet.

- Use optional `rule_id` plus deterministic fingerprint fields; do not add a
  fuzzy auto-merge. Near duplicates may only be flagged later.
- Keep final full review blind to prior review prose; ledger reconciliation is
  performed afterward by policy code.
- Evidence excerpts must be redacted; unredacted sensitive artifacts are only
  referenced by digest/path under later access policy.
- Support one repository/subject in v1.
- Do not auto-close or escalate on nit count in v1.
- Reviewer may propose disposition, but validator/policy treats it as open.

## Implementation caveats

- Validate the draft against an actual Draft 2020-12 validator; Claude's schema
  is extensive and may contain subtle ineffective conditionals.
- Extract examples into standalone JSON fixtures and prove expected pass/fail.
- Add a duplicate-key/trailing-data strict parser before schema validation.
- Do not treat schema validity as semantic validity or acceptance.
- Keep identifiers and hashes policy-verifiable; JSON Schema cannot recompute
  them.
