# Reviewer Contract Implementation Slice

This directory contains the bounded executable slice for
`state/tasks/2026-08-11-codex-claude-orchestrator/CODEX_TASK_PACKET.md`.

## Files

- `review-verdict.schema.json` - Draft 2020-12 schema for reviewer observation output.
- `validate_review_verdict.py` - strict transport parser plus schema and semantic validator.
- `fixtures/valid/*.json` - known-good reviewer documents.
- `fixtures/invalid/*.json` - known-bad documents covering transport, schema, and semantic failures.
- `fixtures/trusted/*.json` - coordinator-supplied validation inputs used by tests.
- `tests/test_review_verdict.py` - unittest coverage for schema, fixtures, parser guards, CLI output, and malformed trusted-input regressions.
- `EVIDENCE.md` - verification results for this implementation slice.

`SANDBOX_PROBE.md` is preserved from the prior infrastructure probe and is not
part of the contract implementation.

## Boundary Notes

The reviewer document is only an observation record. The schema and validator do
not represent acceptance, state transitions, merge instructions, human approval,
or `FAILED_INFRA` classification. The CLI success condition is only
`contract_valid: true`.

The schema rejects unknown fields everywhere. The Python validator adds checks
that JSON Schema cannot express in this slice:

- empty input, invalid UTF-8, duplicate keys, trailing JSON, non-object root, size and depth caps;
- decoded lone surrogates and disallowed control characters in strings;
- deterministic `finding_id` and `occurrence_id` consistency;
- count totals, unique IDs, and local references after collecting all evidence carriers;
- timestamp validity, invalid leap-second rejection, and per-run evidence window checks;
- finding/fingerprint category and criterion consistency;
- trusted subject, expected review mode/scope, criteria, and instruction bindings
  from `--trusted-manifest`;
- strict trusted-manifest completeness: required subject keys, expected
  review mode, expected coverage scope, acceptance/instruction digests, and
  non-empty unique criteria records with statement digests, with scalar
  type checks before enum membership checks;
- strict prior-findings structure: document type, schema version, array shape,
  unique finding IDs, and scalar allowed status values;
- prior digest and exact open-finding coverage from `--prior-findings` whenever
  the document contains a verification block or the trusted manifest expects
  `targeted_verification`.

Reviewer-declared hashes are treated as untrusted claims until they match the
coordinator-supplied manifest or prior-findings file. Without
`--trusted-manifest`, document validation fails closed. Malformed
coordinator-supplied trusted input fails with `failure_kind:
"tool_input_failure"` and CLI exit `2`. Without `--prior-findings`,
documents with verification blocks and documents whose trusted manifest expects
`targeted_verification` fail closed.

Free-text fields, excerpts, notes, and summaries remain untrusted observation
data. A coordinator must not treat them as acceptance, resolution, or human
approval prose.

## CLI Contract

- Exit `0`: document contract is valid, or schema self-check succeeded.
- Exit `1`: reviewer document was read but failed the contract.
- Exit `2`: validator/tool/input failure such as missing files, directory
  paths, schema-load failure, invalid CLI usage, incomplete trusted manifests,
  or malformed prior-findings files.

Every CLI path prints one JSON object. Document validation output has
`mode: "document"`. Schema self-check output has `mode: "schema_self_check"`
and `layers.semantic: null` because document semantics are not run.

## Commands

Run from the workspace root:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py --check-schema
```

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py \
  state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/valid/initial_blocker.json \
  --trusted-manifest state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/trusted/manifest_initial.json
```

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py \
  state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/valid/targeted_verification.json \
  --trusted-manifest state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/trusted/manifest_targeted.json \
  --prior-findings state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/trusted/prior_findings_targeted.json
```

```sh
python3 - <<'PY'
from pathlib import Path
import importlib.util

root = Path("state/tasks/2026-08-11-codex-claude-orchestrator/implementation")
spec = importlib.util.spec_from_file_location("validator", root / "validate_review_verdict.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

for expected, folder in ((True, "valid"), (False, "invalid")):
    for fixture in sorted((root / "fixtures" / folder).glob("*.json")):
        targeted = fixture.name in {"targeted_verification.json", "bad_targeted_mode.json", "prior_digest_mismatch.json"}
        manifest = root / "fixtures" / "trusted" / ("manifest_targeted.json" if targeted else "manifest_initial.json")
        prior = root / "fixtures" / "trusted" / "prior_findings_targeted.json" if targeted else None
        result = validator.validate_document(fixture, trusted_manifest_path=manifest, prior_findings_path=prior)
        print(f"{fixture.relative_to(root)} expected={expected} actual={result['contract_valid']} codes={[error['code'] for error in result['errors']]}")
        if result["contract_valid"] is not expected:
            raise SystemExit(1)
PY
```

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover
```

```sh
python3 -m py_compile \
  state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py \
  state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_review_verdict.py
```

```sh
git diff --check -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation
```
