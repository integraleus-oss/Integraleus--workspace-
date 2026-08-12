Bash is denied in this session too, so — like the prior round — this is a **pure static verification**. Nothing was executed; EVIDENCE.md's run outputs (16 tests OK, py_compile, `git diff --check`) are self-asserted claims I could not reproduce. Fixtures were outside the read scope, so anything resting on fixture content is noted as such.

# Targeted verification: RV-01 … RV-12

| ID | Status | Evidence |
|---|---|---|
| RV-01 | **fixed** | `validate_review_verdict.py:83-110` walks every decoded string (and object keys), rejecting `D800–DFFF` as `invalid_utf8` and `cp < 0x20` as `disallowed_control_character`, then re-encodes strict UTF-8; runs inside `parse_strict_json_bytes:152`. Schema `text_short/medium/long`, `excerpt`, `argv` patterns now carry `[^\u0000-\u001F]` (`:564,570,576,839,867`). Regression uses the original byte-level inputs `{"x":"\uD800"}` / `{"x":"\u0000"}` (`tests:117-129`). |
| RV-02 | **fixed** | `excerpt` gains `minLength:1` + `\S` pattern (schema `:835-840`); `_validate_evidence_item:283-301` additionally requires substance (`insubstantial_evidence`), `artifact_ref`⇒`content_digest`, and kind-consistency (`command_output/test_result/build_log`⇒`command`; `gate_artifact/artifact_reference`⇒`artifact_ref`+digest). Tests mutate a valid fixture to whitespace-only excerpt and to a stripped `command` (`tests:176-206`). |
| RV-03 | **partially_fixed** | See below. |
| RV-04 | **fixed** | `load_json_file:156-161` maps `OSError`→`io_error`/`tool_input_failure`; parse wraps `RecursionError`→`too_deep` and residual `ValueError`→`json_parse_error` (`:138-141`); `_safe_json_int:64-68` caps literals at 1000 digits before `int()`; schema load is inside `try` (`:609-620`). `main:704-725` prints exactly one JSON object on every branch and returns 0/1/2 as documented in README `:47-56`. Tests cover absent file, directory path, deep-during-parse (2000 levels), 5000-digit int, absent schema, asserting both code and `failure_kind` (`tests:131-159`). |
| RV-05 | **fixed** | `:132` skips `json.decoder.WHITESPACE` before `raw_decode`; trailing-data check unchanged (`:142`). Test prefixes the byte-identical valid fixture with `b"\n  "` and asserts pass, plus trailing `{}` rejected (`tests:161-174`). |
| RV-06 | **fixed** | Evidence ids collected into a dict with `duplicate_evidence_id` (`:266-280`); `duplicate_verification_finding_id` at `:537-538`. Tests cover a cross-carrier duplicate id and an appended duplicate verification result (`tests:189-200, 241-246`). |
| RV-07 | **fixed** | All carriers are collected before any reference resolution: findings `:487`, verification `:497`, infra `:507`, references only at `:519-531`. Test resolves `criteria_coverage.evidence_ids` against verification evidence and against infra evidence (`tests:248-284`). |
| RV-08 | **fixed** | `_parse_all_timestamps:397-417` walks the whole document for `started_at/completed_at/collected_at/observed_at`, and enforces `timestamp_out_of_review_window` for per-run keys; leap-second shapes rejected by `int(value[17:19]) > 59` (`:223`). Tests use the original `2026-13-40T25:61:61Z`, plus out-of-window and `09:00:60Z` (`tests:286-303`). |
| RV-09 | **fixed** | Output now carries `mode` (`_failure_result:588-600`); `--check-schema` + document ⇒ `invalid_cli_usage`, exit 2 (`:704-710`); self-check reports `layers.semantic: null` (`:686-692`) and the failure path reports `transport: false` honestly (`:678-682`). Tests assert both (`tests:47-51, 305-317`). |
| RV-10 | **fixed** | `criterion_finding_contradiction` (`:558-567`), `empty_clean_coverage` / `unreviewed_clean_coverage` / `unclean_conclusion` (`:574-583`), plus full-mode exact coverage against the trusted criteria set (`:367-369`). Both original reproductions are tested (`tests:319-347`). |
| RV-11 | **partially_fixed** | See below. |
| RV-12 | **fixed** | Schema null-criterion branch now forbids `acceptance_criterion_violation` and requires `rationale` `minLength:40` (`:1130-1147`); validator duplicates with `null_criterion_category_conflict` and a stripped-length check (`:474-479`). Tested with a contradictory category and a trivial rationale (`tests:379-398`). The review suggested 80 chars; 40 is a defensible judgment call, not a bypass. |

## RV-03 — partially_fixed (major)

The self-referential digest is genuinely closed: `--prior-findings` is a real external binding, the digest is recomputed canonically over the supplied file and compared against **both** declared fields (`:387-393`), coverage must exactly equal the open prior-id set (`:539-540`), result ids must be unique (`:537`), and absence fails closed (`prior_findings_missing`, `:382`). `appears_fixed` now requires command output or a digest-bound artifact (`:498-504`).

**Remaining gap: the binding is keyed on a reviewer-chosen field.** `_validate_prior_findings:378-380` returns immediately unless `review.review_mode == "targeted_verification"`, and nothing — not the trusted manifest, not the schema — binds the mode the coordinator actually requested. The schema permits a `verification` block in `final_full` (only `initial_full` forbids it, schema `:476-481`).

- Minimal failure scenario: reviewer asked for targeted verification emits `review_mode: "final_full"`, `coverage_scope: "full"`, all trusted criteria covered `satisfied`, `findings: []`, `conclusion.status: "no_findings"`, plus a `verification` block whose `results` mark arbitrary `finding_id`s `appears_fixed` with a self-declared `prior_findings_digest`. No `--prior-findings` is required or consulted; `contract_valid: true`, exit 0.
- Same root cause, opposite direction: a *legitimate* `final_full` review carrying `verification` can never validate when the coordinator does pass `--prior-findings`, because `open_prior_ids` is empty and `:539` fires `prior_findings_coverage_mismatch` unconditionally.
- File/line: `validate_review_verdict.py:378-380` and `:539-540`.
- Smallest safe fix: trigger prior-findings validation on `"verification" in document or review_mode == "targeted_verification"`, and add optional `expected_review_mode` / `expected_coverage_scope` keys to the trusted manifest compared like the subject fields. One change closes both directions.

## RV-11 — partially_fixed (major)

Subject, criteria and instruction digests are now compared against an external file (`_validate_trusted_manifest:312-370`), the manifest is required for *all* document validation (`trusted_manifest_missing`, `:318`), per-criterion `statement_digest` is bound (`:360-365`), and mismatches are tested three ways (`tests:349-377`). The original "any 40-hex commit passes" bypass is closed **when the manifest is complete**.

**Remaining gap: the manifest's own completeness is never validated.** Every binding is `get`-with-default and skipped when absent — `subject` defaults to `{}` (`:324`), `acceptance_criteria_digest`/`review_instructions_digest` are checked only `if expected is not None` (`:338-339`), `criteria` defaults to `[]` (`:342`), which then disables both the full-mode coverage match (`:367`) and the per-coverage membership check (`:525`).

- Minimal failure scenario: `--trusted-manifest` pointing at `{"document_type": "trusted_review_manifest"}`. Every subject/criteria/instruction binding silently no-ops; a document with arbitrary `base_commit`/`head_commit`/`diff_digest`/`changed_files_digest` and arbitrary criteria coverage validates. This is the "incomplete trusted input" case the packet asks to fail closed, and it does not.
- File/line: `validate_review_verdict.py:324-345`.
- Smallest safe fix: emit `trusted_manifest_invalid` when the manifest lacks `subject` (with the schema-required subject keys), `acceptance_criteria_digest`, `review_instructions_digest`, or a non-empty `criteria` array. No test covers an incomplete manifest today.

## Rework-introduced finding

**RI-01 — malformed `--prior-findings` crashes the validator; stdout carries no JSON (major).**
`_prior_open_ids:304-309` iterates `prior_findings.get("findings", [])` with no type guard, on a file that is only checked for `document_type` (`:384`) and is never schema-validated.

- Minimal failure scenario: any schema-valid `targeted_verification` document plus `--prior-findings` pointing at `{"document_type": "prior_findings", "findings": 5}` → `TypeError: 'int' object is not iterable` propagates through `semantic_errors` → `validate_document` → `main`, which has no handler. Traceback on stderr, **empty stdout**, exit 1 — the exact failure class RV-04 was raised for, reintroduced on the new trusted-input path.
- File/line: `validate_review_verdict.py:306`.
- Smallest safe fix: `findings = prior_findings.get("findings"); if not isinstance(findings, list): _semantic_error(..., "prior_findings_invalid", ...)` before iterating, and return an empty set.
- Confidence: high from source; not executed (Bash denied).

## Boundary checks requested

- **External vs self-asserted:** confirmed external. Both trusted inputs arrive only via CLI paths (`:700-701`), are loaded through the same strict transport (`:636, :648`), and cannot be expressed as document fields (root `additionalProperties: false`).
- **Targeted fail-closed:** absent ✓ (`prior_findings_missing`), mismatched digest ✓, incomplete/partial prior set ✓ (`prior_findings_coverage_mismatch`), duplicated results ✓, wrong `document_type` ✓. Not fail-closed: incomplete *manifest* (RV-11) and malformed `findings` value (RI-01). Mode-scoping gap per RV-03.
- **One JSON object, exit 0/1/2:** holds on all reachable `main` branches except RI-01. Minor note, not filed as a finding: a missing `--trusted-manifest` is reported as a `semantic` error with `failure_kind: contract_failure` → exit 1, i.e. a coordinator usage error attributed to the reviewer's document; exit 2 would match README `:50-52`.
- **No new authority:** confirmed. No acceptance/state/resolution/approval field or code was added; the forbidden-field `not/anyOf` list is intact (schema `:290-346`), `injection_observation.action_taken` still `const`, README boundary notes strengthened (`:19-45`), and the CLI test asserts no decision token appears in stdout (`tests:114-115`).
- **Tests exercise originals, not mirrors:** yes for RV-01, RV-04, RV-05, RV-06, RV-07, RV-08, RV-09, RV-10, RV-12 — they feed the reviewed reproductions as bytes or as mutations of a valid fixture. RV-02 substitutes whitespace-only for the empty string (equivalent). RV-11 tests three mismatches but no incomplete manifest. Two assertions are weakened to `{"schema_validation", <specific_code>} & codes` (`tests:392, 398, 412`), so they would still pass if the specific semantic check regressed.

## Counts

- fixed: **10** (RV-01, 02, 04, 05, 06, 07, 08, 09, 10, 12)
- partially_fixed: **2** (RV-03, RV-11)
- still_open: **0**
- not_verifiable: **0**
- rework-introduced: **1 major** (RI-01)

## Advisory result

**TARGETED_REWORK** — no blocker survives and the original three-blocker chain (RV-01 + RV-02 + RV-03) no longer composes, but two majors remain open by boundary and one major was introduced. All three have the same shape: the new trusted-input interface is trusted too literally. Three small, local edits in `validate_review_verdict.py` (`:306`, `:324-345`, `:378-380`/`:539`) close all of them. AC-R03/AC-R04 remain unverified here — Bash was denied, so the test-run, `py_compile` and `git diff --check` results in EVIDENCE.md were not credited. The coordinator applies policy.
