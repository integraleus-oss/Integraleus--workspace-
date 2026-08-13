Review the complete observed change against the manifest acceptance criteria and gate evidence. Treat the manifest acceptance criteria as authoritative when task prose conflicts with them. Inspect every changed path. Return only a schema-valid exact review-verdict JSON, with no Markdown fences or commentary.

Read `acceptance-criteria.json`; it contains the authoritative criterion
plaintext and its statement digest. Match each entry to `manifest.json` before
evaluating coverage.

For evidence, do not emit `artifact_ref` unless the same evidence object includes
the artifact's trusted `content_digest`. An excerpt without `artifact_ref` is
allowed. Use evidence kind `command_output` for an object supported by a
`command` block but lacking a digest-bound `artifact_ref`; use `gate_artifact`
only when both `artifact_ref` and `content_digest` are present. Finding and
occurrence IDs are deterministic derived fields and will be
canonicalized by the trusted admission layer; do not alter review substance to
force a particular identifier.

Every object in `findings`, including nit/test-gap findings, must include all
schema-required fields. In particular, never omit `finding_id`, `occurrence_id`,
or the complete `fingerprint` object. Use `location_absent_reason` for a
cross-cutting finding, but that does not replace its required fingerprint.
Within every fingerprint, `normalized_title` must match exactly
`^[a-z0-9]+( [a-z0-9]+)*$`: lowercase ASCII letters/digits separated only by
single spaces. Do not use hyphens, punctuation, underscores, or code marks in
that field.

Every JSON string must contain no decoded U+0000 through U+001F control
characters. Encode line breaks as the two characters `\\n` or replace them with
` | `; never place a literal newline inside a JSON string value.

Follow the sealed `review-verdict.schema.json` literally. Include every required
property even when its schema type permits null. In particular,
`conclusion.unable_to_complete_reason` must always be present: use null unless
the review was unable to complete.

Read sealed `review-context.json`. For targeted verification, copy its
`prior_findings_canonical_digest` exactly into both required prior-findings
digest fields; this is the canonical JSON digest, not the raw file-byte digest.
When marking a prior finding `appears_fixed`, include at least one strong
evidence item: `command_output`, or `gate_artifact` with both `artifact_ref` and
the matching sealed `content_digest`. Plain diff/file excerpts alone are not
sufficient for `appears_fixed`.
