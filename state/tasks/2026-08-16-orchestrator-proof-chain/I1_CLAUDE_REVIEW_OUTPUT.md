# Independent Review — I1 immutable requirements and traceability

Fixed point `996fb3c`; packet under review `0e30abb`. Source of truth: `state/tasks/2026-08-16-orchestrator-proof-chain/TASK_PACKET.md`.

## 1. Standards findings

**Major — schema/runtime drift; the JSON schema is never executed.**
`requirements-manifest.schema.json` is not loaded anywhere (no `jsonschema` use in `requirements_traceability.py` or `production_cycle_cli.py`); admission relies solely on the hand-rolled `validate_manifest`. The two contracts disagree: the schema's `^R[0-9]{2,3}$` permits `R00`, duplicates, gaps and mixed widths, while the runtime demands contiguous `R01..Rnn` at a single computed width; the schema permits `owner_disposition: null` on `removed_by_user`/`deferred_by_user` (runtime rejects) and permits a disposition object on active states (runtime rejects). A producer that validates against the published schema will be rejected at admission, and vice versa.

**Major — `manifest_digest` binds mutable lifecycle state.**
`canonical_digest(manifest)` covers the whole document including `state`. A normal `accepted → implementing → implemented` transition changes the digest and invalidates the `manifest_digest` in the specification, task map and acceptance documents, forcing all three to be re-issued on every state change. It also means a digest mismatch cannot distinguish tampering from a legitimate transition. The immutable core (brief + IDs + `original_text`) should be digested separately from the mutable state overlay.

**Major — ID width is a function of requirement count, so IDs are not stable across growth.**
`width = max(2, len(str(len(texts))))` in `generate_manifest`, mirrored in `validate_manifest`. A 99-requirement manifest is `R01..R99`; adding one requirement renumbers *every* requirement to `R001..R100`, breaking all spec/task/acceptance links and the manifest digest. Width must be pinned at creation, not derived.

**Nit — unbounded reads for the three proof documents.**
`load_packet` uses `_read_json` (whole-file `read_text`) for `requirements_manifest`/`_specification`/`_task_map`, while every other packet-referenced text file goes through `_bounded_text`. Size limits are only enforced *after* parse, inside `validate_manifest`.

**Nit — version dispatch falls through to the newest field set.**
`expected_fields = (legacy_fields if ... "1.0.0" else builder_fields if ... "1.1.0" else proof_fields)`. Correct today only because of the adjacent membership test; adding `"1.3.0"` to the version set silently maps it to `proof_fields`.

**Nit — proof artifacts are sealed but not bound into the reviewer contract.**
`seal.update(proof_artifacts)` and `evidence["artifacts"]` cover the three files, and `anchored_seal_digest` anchors the seal, so in-run tamper detection is sound. But `bundle.json`, `manifest.json` and the reviewer prompt text in `production_cycle_cli.review()` are unchanged, so nothing directs or obliges the reviewer to read them. Acceptable if deferred to I2, but worth stating.

**Nit — two digest domains for one document.**
`evidence["requirements_manifest_digest"]` is the canonical digest of the parsed object; `evidence["artifacts"]["requirements-manifest.json"]` is the digest of the re-serialized file. Both are legitimate, but a consumer comparing the wrong pair will see a spurious mismatch.

**Nit — task map may reference retired requirements, and may be empty.**
`validate_task_traceability` accepts `requirement_ids` pointing at `deferred_by_user`/`removed_by_user` entries, and accepts `"tasks": []` whenever no requirement is in `implementing`/`implemented` — so a 1.2.0 packet whose requirements are all `accepted` passes preflight with no task linkage at all.

Determinism and path/seal integrity are otherwise clean: `canonical_digest` uses `sort_keys=True, separators=(",", ":")`; `_inside` still rejects absolute paths, `..`, symlinks and wrong types; seal ordering (proof artifacts written and digested before `evidence.json` and `seal.json`) is correct; the builder re-validates the chain independently of the CLI.

## 2. Spec findings

**Blocker — criterion 2 is not enforced: requirements can disappear or change state with no owner disposition.**
Every validator operates on a *single* manifest in isolation. There is no prior-manifest linkage, no append-only or supersession check, and the packet does not pin an expected manifest digest. Deleting `R02` from a 3-requirement manifest and renumbering yields a manifest that passes `validate_manifest` cleanly; regressing `implemented → accepted` likewise passes. `owner_disposition` is only required when the *final* state happens to be `deferred_by_user`/`removed_by_user`, which is exactly the case an omission avoids. The module title "immutable requirements" is not backed by any immutability mechanism.

**Blocker — criterion 1 is satisfied only vacuously: the brief is self-certified and unbound to the executed task.**
`original_brief_digest` is recomputed from `original_brief` at validation time, so it detects accidental inconsistency but not rewriting — regenerate the field and the digest and the manifest validates. Nothing in `load_packet` ties `manifest["original_brief"]` to `packet["task_note"]` (the text actually handed to the implementer) or to any externally anchored owner artifact. The proof chain therefore does not start at the owner's brief; it starts at whatever the manifest asserts the brief was. The tests reinforce this: `test_tampered_brief_or_requirement_fails` only mutates text *without* recomputing the digest.

**Major — the hard gate is opt-in and bypassable by version downgrade.**
The three new fields and `validate_preflight` apply only when `schema_version == "1.2.0"`. `1.1.0` remains fully admissible with `proof_chain = None`, and `build_review_inputs` skips the chain entirely in that case. Nothing forces new packets to 1.2.0, so the "hard block" is a per-packet opt-in.

**Major — final acceptance completeness is permissive and unwired.**
`validate_acceptance_completeness` counts an active requirement as covered when its outcome is `unable_to_verify`, `deferred` or `removed`, with no consistency check against the manifest state — coverage without verification, and an active requirement can be reported "removed" while still active. The function is also not called from `production_cycle_cli.py` or `trusted_review_builder.py`; it exists only in tests. Acceptable as groundwork for I2, but criterion 5 is not yet met by this increment.

**Satisfied.** Criterion 3 (`validate_spec_completeness` requires a non-blank specification entry for every active requirement, rejects unknown/duplicate IDs) and criterion 4 (`validate_task_traceability` requires non-empty, duplicate-free `requirement_ids` per task and covers every `implementing`/`implemented` requirement) are enforced, and both are wired into admission for 1.2.0 packets and re-checked in the builder. R ID generation is stable and deterministic *within* a fixed requirement count.

## 3. Test gaps

- No builder-level test exercises `build_review_inputs(..., proof_chain=...)`: the `seal.update(proof_artifacts)`, `evidence["requirements_manifest_digest"]` wiring, and `verify_seal` detection of a tampered `requirements-manifest.json` inside the sealed directory are entirely uncovered.
- No negative test for a wrong `manifest_digest` in the specification, task map, or acceptance document — the single most important binding in the chain.
- No test for the forbidden branch: `owner_disposition` set on an `accepted`/`implementing` requirement.
- No packet-level negative tests for 1.2.0 with one of the three new fields missing, or 1.1.0 carrying the new fields (the refactored `expected_fields` chain is only exercised on the happy path).
- No test at the 99→100 requirement boundary, which is where ID stability actually breaks.
- No `generate_manifest` input-validation tests (bad `manifest_id`, empty/oversized brief, >999 texts, non-string texts).
- No determinism test for `canonical_digest` across key ordering / non-ASCII input.

VERDICT: REWORK
