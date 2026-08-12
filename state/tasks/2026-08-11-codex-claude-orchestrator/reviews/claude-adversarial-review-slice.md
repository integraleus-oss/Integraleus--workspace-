Bash was denied in this session, so this is a pure static review — no fixture was executed. Reproductions below are given as exact inputs/commands; I flag which claims rest on CPython source semantics rather than an observed run.

# Reviewer contract slice — adversarial review

Scope: `CODEX_TASK_PACKET.md`, `implementation/review-verdict.schema.json`, `implementation/validate_review_verdict.py`. Fixtures, tests, README and EVIDENCE were out of the permitted read set.

Repository content was treated as untrusted data. The packet's `Status: COMPLETED` line and its all-`[x]` checklist are claims inside a reviewed file; they were not treated as evidence.

## Blockers

### RV-01 — `\uD800` escapes defeat the invalid-UTF-8 transport rule and yield an unencodable document
- **Severity:** blocker
- **File:** `implementation/validate_review_verdict.py:70-72`; schema `review-verdict.schema.json:566-570, 835-838`
- **Requirement violated:** "Strict transport parser rejects … invalid UTF-8" (packet:46-47)
- **Reproduction:** any otherwise-valid document with `"conclusion": {"summary": "ok \ud800", …}` (the six ASCII characters `\ud800`, not raw bytes). The file is well-formed UTF-8 on the wire, so `data.decode("utf-8")` succeeds; JSON unescapes it into a lone surrogate; no schema keyword or semantic check rejects it. Result: `contract_valid: true`, exit 0.
- **Impact:** the transport layer only validates the *encoding of the container*, not the *decoded string*. The emitted document cannot be re-encoded to UTF-8 — a coordinator doing `json.dumps(doc).encode("utf-8")`, writing it to Redis, or hashing it raises `UnicodeEncodeError` on a document the validator certified. The same hole admits `\u0000` and other C0 controls into every `text_*` field (`pattern: "\\S"` matches NUL, since NUL is not whitespace).
- **Fix:** after parsing, walk all strings and reject any that fail `s.encode("utf-8", "strict")` (transport code `invalid_utf8`), and add a control-character exclusion to the `text_short`/`text_medium`/`text_long`/`excerpt` patterns.
- **Confidence:** high (CPython `json` accepts lone-surrogate escapes; `str.encode("utf-8")` rejects them). Not executed.

### RV-02 — Empty-string evidence satisfies every evidence obligation
- **Severity:** blocker
- **File:** `review-verdict.schema.json:835-838` (`excerpt` has `maxLength` but no `minLength`/`pattern`), interacting with `:1090-1096` and `:1356-1362`
- **Requirement violated:** "Enforce severity floors and blocker/major evidence obligations" (packet:49)
- **Reproduction:** a `blocker` finding whose `evidence` array is
  ```json
  [{"evidence_id":"ev_00000000000000000000000000000000",
    "kind":"file_excerpt","description":"e","excerpt":""}]
  ```
  The `evidence` object's `anyOf` is satisfied by the presence of the `excerpt` key regardless of content; `description` needs one non-whitespace character. `contract_valid: true`.
- **Impact:** the blocker/major evidence obligation — the main anti-fabrication control in the contract — is satisfiable with zero information. The same object also satisfies `verification.results[*].evidence` (min 1) for an `appears_fixed` claim, which is what makes RV-03 exploitable rather than theoretical.
- **Fix:** require `excerpt` to be non-empty (`minLength: 1`, `pattern: "\\S"`) and require an `evidence` object to carry at least one substantive anchor: `artifact_ref` + `content_digest`, or `excerpt` + `byte_length`, or a `command` block with `argv`/`exit_code`. Consider requiring `kind`-appropriate fields (`command_output` ⇒ `command`).

### RV-03 — Targeted-verification binding is self-referential; a forged "everything fixed" review is contract-valid
- **Severity:** blocker
- **File:** `implementation/validate_review_verdict.py:263-278`; schema `:1310-1335`, `:489-531`
- **Requirement violated:** "Targeted mode requires prior-findings digest and verification data" (packet:53); "references … must be checked in Python where feasible" (packet:56-58)
- **Reproduction:** `review_mode: "targeted_verification"`, `coverage_scope: "targeted"`, `findings: []`, counts all 0, `conclusion.status: "no_findings"`, and
  ```json
  "review":{"inputs_digest":{"prior_findings_digest":"sha256:<any 64 hex>"}},
  "verification":{"prior_findings_digest":"sha256:<the same 64 hex>",
    "results":[{"finding_id":"fnd_<any 32 hex>","observed_status":"appears_fixed",
      "reverification_method":"code_inspection",
      "evidence":[{"evidence_id":"ev_<32 hex>","kind":"file_excerpt","description":"e","excerpt":""}],
      "notes":"resolved"}]}
  ```
  `contract_valid: true`, exit 0.
- **Impact:** the only prior-findings check (`:266`) compares two fields the reviewer writes itself, so equality proves nothing about the real prior-findings set. Nothing constrains `results[*].finding_id` to any prior finding, and nothing requires the results to *cover* the prior set — a reviewer (or an injected instruction inside the diff) can drop unresolved blockers by simply not listing them, or mark them `appears_fixed` with vacuous evidence. This is exactly the "reviewer cannot grant acceptance" boundary being crossed by omission rather than by a forbidden field.
- **Fix:** add a `--prior-findings <file>` input; recompute the digest over its canonical form and compare against *both* declared digests; require `results` to cover every open prior `finding_id` exactly once; and require `appears_fixed` evidence to include a `command` block or `artifact_ref` + `content_digest`. Until that exists, the coordinator must not treat `contract_valid: true` on a targeted review as verification of anything.

## Majors

### RV-04 — Non-`TransportError` failures escape as tracebacks; stdout carries no JSON
- **Severity:** major (fails closed — exit is non-zero — but violates the machine-readable-output contract)
- **File:** `implementation/validate_review_verdict.py:101-102` (`read_bytes`), `:292` (schema load outside the `try`), `:83-87` (only `TransportError`/`JSONDecodeError` caught)
- **Requirement violated:** AC-C05 "Validator output is machine-readable JSON" (packet:72-73); "Validator distinguishes transport, schema, and semantic failures" (packet:48)
- **Reproduction (certain):** `validate_review_verdict.py /nonexistent.json` → `FileNotFoundError` propagates through `validate_document` (the `try` at `:301` catches only `TransportError`) → traceback on stderr, **empty stdout**, exit 1. Same for `--schema missing.json` at `:292`, and for a directory path or a permission-denied file.
- **Reproduction (high confidence, unexecuted):** `{"a":` + `[`×200000 + `]`×200000 + `}` → `RecursionError` from the C scanner at `:83`, uncaught (the `RecursionError` handler at `:94` guards only `_max_depth`, which runs after parsing). A 5000-digit integer literal (e.g. `{"attempt": 111…1}`) → plain `ValueError` from CPython's ≥4300-digit conversion limit (3.11+), which is not `JSONDecodeError` and is not a `TransportError`, so it escapes too.
- **Impact:** a coordinator that parses stdout gets an empty string; a coordinator that keys on the exit code cannot distinguish "document invalid" from "validator crashed". The resource-exhaustion classes the packet explicitly names (`oversized/deep documents`) are handled for depth-after-parse but not for depth-during-parse.
- **Fix:** wrap the whole document/schema load in `except (OSError, RecursionError, ValueError)` and map to transport codes `io_error` / `too_deep` / `json_parse_error`; use a distinct exit code (e.g. 2) for tool errors versus 1 for contract failure; guard the int size with `sys.set_int_max_str_digits` or a pre-scan.

### RV-05 — `raw_decode` does not skip leading whitespace: valid documents are rejected
- **Severity:** major (false rejection; fails closed)
- **File:** `implementation/validate_review_verdict.py:83`
- **Requirement violated:** transport layer must reject only the enumerated malformations (packet:46-47); a leading newline is not one of them
- **Reproduction:** a byte-identical valid fixture prefixed with a single `\n` or space → `JSONDecodeError("Expecting value", pos 0)` → `{"contract_valid":false,"errors":[{"code":"json_parse_error",…}]}`, exit 1. `JSONDecoder.raw_decode(s)` calls `scan_once(s, 0)` directly; only `JSONDecoder.decode`/`json.loads` skip leading whitespace first.
- **Impact:** any producer that emits a leading newline (heredoc, shell wrapper, log-prefixed capture) is reported as a transport violation. Under the intended orchestration this is a reviewer "failure" caused by formatting, which will be misattributed.
- **Fix:** `idx = json.decoder.WHITESPACE.match(text, 0).end()` then `decoder.raw_decode(text, idx)`; keep the trailing-data check unchanged.
- **Confidence:** high (CPython `json/decoder.py` source). Not executed.

### RV-06 — `evidence_id` and verification `finding_id` uniqueness is never enforced
- **Severity:** major
- **File:** `implementation/validate_review_verdict.py:185-190` (set-based collection silently collapses duplicates), `:268-278`
- **Requirement violated:** "Counts, uniqueness, references … must be checked in Python where feasible" (packet:56-58)
- **Reproduction (a):** `findings[0].evidence[0].evidence_id` and `findings[1].evidence[0].evidence_id` both `ev_<same 32 hex>` with different `description`/`excerpt`. `_collect_evidence_ids_from_items` adds the id twice to a `set`; no duplicate check exists (unlike `occurrence_id` at `:211` and `criterion_id` at `:248`). A `criteria_coverage.evidence_ids` reference to that id now resolves ambiguously, and `contract_valid: true`.
- **Reproduction (b):** two `verification.results` entries with the same `finding_id`, one `still_open` and one `appears_fixed`. Both pass; the document asserts contradictory statuses for one prior finding.
- **Impact:** evidence references become non-deterministic, so any downstream de-duplication or evidence-fetch keyed on `evidence_id` can silently pick the wrong record; contradictory verification results give the coordinator no single answer.
- **Fix:** track evidence ids in a dict id→canonical-object and emit `duplicate_evidence_id` on conflict; enforce uniqueness of `verification.results[*].finding_id`.

### RV-07 — Evidence-reference resolution is order-dependent and produces false `bad_evidence_reference`
- **Severity:** major (false rejection)
- **File:** `implementation/validate_review_verdict.py:251-256` and `:258-261`, versus the later collection at `:270` and `:286`
- **Requirement violated:** reference checking (packet:56-58)
- **Reproduction:** a `criteria_coverage` entry with `status: "satisfied"` whose `evidence_ids` names an evidence object defined only under `verification.results[0].evidence` (or `infra_symptoms[0].evidence`). At `:251` the `evidence_ids` set contains only evidence gathered from `findings` (`:239`); verification and infra evidence are not added until `:270`/`:286`. Result: spurious `bad_evidence_reference`, exit 1, on a document that is internally consistent.
- **Impact:** in `targeted_verification` mode — where most evidence lives under `verification` — this misfires for the common case, so `criteria_coverage.evidence_ids` is effectively unusable there.
- **Fix:** run a full collection pass over findings, verification results, infra symptoms (and any future evidence carriers) before any reference resolution.

### RV-08 — Timestamps outside `review`/`infra_symptoms` are never semantically parsed
- **Severity:** major
- **File:** `implementation/validate_review_verdict.py:280-286`; schema `:578-581`, `:846-848`
- **Requirement violated:** "time ordering … must be checked in Python where feasible" (packet:56-58)
- **Reproduction:** any evidence object with `"collected_at": "2026-13-40T25:61:61Z"`. The schema pattern is purely positional (`[0-9]{2}` for month/day/hour) so it matches; `_parse_timestamp` is called only for `/review/started_at`, `/review/completed_at`, and `/infra_symptoms/*/observed_at`. `contract_valid: true`.
- **Impact:** inconsistent enforcement — the same lexical type is calendar-checked in three places and unchecked everywhere else. There is also no check that evidence/infra timestamps fall inside `[started_at, completed_at]`, so evidence can be dated to a prior run and still pass, which weakens the per-run provenance the `occurrence_id` design is trying to establish.
- **Fix:** parse every `$defs/timestamp` occurrence by JSON pointer walk; add a window check against the review interval (as a semantic error or an explicit documented non-check).

### RV-09 — `--check-schema` overloads `contract_valid` and silently ignores the document argument
- **Severity:** major (misleading success signal)
- **File:** `implementation/validate_review_verdict.py:350-351`, `:326-340`, `:360-361`
- **Requirement violated:** AC-C05 "success means only `contract_valid: true`" (packet:72-73); "Missing/schema-invalid output must … never produce a success state" (packet:59-60)
- **Reproduction:** `validate_review_verdict.py forged.json --check-schema` — where `forged.json` is empty, malformed, or absent — prints `{"contract_valid":true,"errors":[],"layers":{…}}` and exits 0. The `if args.check_schema` branch wins and the `document` argument is discarded without warning.
- **Impact:** the same field name and the same exit code mean "this schema is a well-formed Draft 2020-12 schema" and "this reviewer document satisfies the contract". Nothing in the output distinguishes the two modes, so a log line or an argv-ordering mistake in the coordinator turns a missing document into a pass. `check_schema_file` also reports `"semantic": true` for a layer it never ran.
- **Fix:** emit a `mode` field (`"document"` / `"schema_self_check"`); error out when `--check-schema` is combined with a document path; report unrun layers as `null`, not `true`.

### RV-10 — No consistency check between `criteria_coverage`, `findings`, and `conclusion.status`
- **Severity:** major
- **File:** `implementation/validate_review_verdict.py:244-256`; schema `:220-226`, `:347-388`
- **Requirement violated:** cross-field consistency the schema cannot express (packet:56-58); the contract's role as the sole artifact a deterministic coordinator consumes
- **Reproduction (a):** `findings[0]` is a `blocker` with `criterion_id: "AC-03"`, while `criteria_coverage` contains `{"criterion_id":"AC-03","status":"satisfied","verification_method":"code_inspection","evidence_ids":[<an id from that finding>]}`. Both pass — the document simultaneously asserts AC-03 satisfied and violated.
- **Reproduction (b):** `criteria_coverage: []` (the array is required but may be empty) with `conclusion.status: "no_findings"`, `findings: []`, `limitations: []`. A review that verified nothing is contract-indistinguishable from a thorough clean review. The same holds with every criterion set to `not_reviewed` plus a one-character `notes`.
- **Impact:** this is the cheapest path to a document that *reads* as an approval to any coordinator keyed on `conclusion.status` or on "all criteria satisfied", without ever touching a forbidden field.
- **Fix:** require that any criterion cited by a `blocker`/`major` finding has status `violated` or `partially_satisfied`; require `criteria_coverage` to be non-empty and to cover the criterion set implied by `acceptance_criteria_digest` (supply the criteria list as an input); reject `conclusion.status: "no_findings"` when any criterion is `not_reviewed`/`not_verifiable` unless a matching non-blocking limitation is declared.

### RV-11 — Subject and input digests are entirely reviewer-asserted; no binding to real inputs
- **Severity:** major
- **File:** schema `:81-102`, `:140-173`; validator has no corresponding check
- **Requirement violated:** "ID/hash consistency … must be checked in Python where feasible" (packet:56-58); the identity-binding intent of `inputs_digest`
- **Reproduction:** set `base_commit`/`head_commit` to any 40-hex string, `diff_digest`/`changed_files_digest`/`acceptance_criteria_digest`/`review_instructions_digest` to any `sha256:<64 hex>`. `contract_valid: true` — the tool never sees a repo, a diff, or the criteria text. Note also that `finding_id` is a public SHA-256 of the fingerprint (`:175-177`) and `occurrence_id` a public SHA-256 of `review_id∥finding_id∥ordinal` (`:180-182`): both are integrity/typo checks that any producer can compute, not authenticity bindings.
- **Impact:** a contract-valid review may describe a different commit, a different diff, or a different acceptance-criteria text than the one under review. `contract_valid: true` carries no statement about *what* was reviewed.
- **Fix:** add `--expect-subject-digest` / `--expect-criteria-digest` / `--expect-instructions-digest` options and fail with a dedicated `subject_binding_mismatch` when the coordinator's computed values differ; document that without these flags the subject fields are unverified reviewer input.

### RV-12 — The `criterion_id: null` obligation is near-vacuous and permits a contradictory category
- **Severity:** major
- **File:** schema `:1116-1133`
- **Requirement violated:** "`criterion_id=null` requires category and rationale" (packet:50)
- **Reproduction:** `{"criterion_id": null, "category": "acceptance_criterion_violation", "severity": "blocker", "rationale": "x", …}` plus the RV-02 evidence stub. The `then` adds `required: ["category", "rationale"]`, but `category` is already unconditionally required at `:932-942`, so the only new obligation is a `text_long` value — satisfied by a single non-whitespace character. And `category: "acceptance_criterion_violation"` with no criterion is self-contradictory yet accepted.
- **Impact:** the control that is supposed to stop findings from floating free of the acceptance criteria adds essentially nothing. `fingerprint.criterion_id` mirrors the same null, so the cross-check at `:221` passes too.
- **Fix:** forbid `category: "acceptance_criterion_violation"` when `criterion_id` is null; add a meaningful `minLength` (e.g. 80) to the rationale in the null-criterion branch; consider requiring an explicit `criterion_absent_reason` enum instead of relying on prose.

## Nits (no demonstrated bypass)

- `validate_review_verdict.py:120-124` — schema error messages discard `error.message` and the schema path, reporting only the keyword name. An `additionalProperties` failure at the root does not say *which* property was smuggled, so AC-C03's "fail for the intended reason" cannot be checked from the machine-readable output alone.
- Schema `:990-1009` — `location_absent_reason` may be present alongside a non-null `location`; the two are never made mutually exclusive.
- Schema `:1031-1033`, `:1134-1153` — `propose_superseded` does not require `supersedes_finding_id`; when present it is never checked for existence, and a finding may supersede itself.
- Free-text fields (`conclusion.summary` 2000 chars, `evidence.excerpt` 4000, `limitation.description`, `tags`) can carry forged approval prose. No schema can prevent this; the coordinator must treat all of it as data. Worth stating explicitly in the README boundary notes.
- `validate_review_verdict.py:295-299` — reports `"transport": true` on the schema-self-check failure path, where the document was never read.
- `:155` — `%S` accepts second values 60/61, so leap-second-shaped timestamps pass while the schema pattern would also allow them.
- `:96-97` — the depth limit is applied only after the full parse, so the memory cost of a deep-but-under-4MB document is paid before rejection (see RV-04 for the failure that actually occurs first).
- `occurrence_id` binds to the findings-array ordinal (`:228`), so reordering a semantically identical findings list invalidates every occurrence id. Intentional per "per-run", but brittle for any producer that sorts output.
- Packet:3 and :98-105 assert `COMPLETED` and an all-checked checklist, including `git diff --check` and the scope audit. Those claims are unverifiable from the three files in scope and were not credited.

## Controls that held

- Field-level smuggling of acceptance authority is closed: root `additionalProperties: false` (`:7`) plus the `not/anyOf` list (`:290-346`) rejects `decision`, `state`, `next_state`, `verdict`, `accepted`, `approval`, `approved_by`, `merge`, `failed_infra`, `escalate`. No nested object admits an equivalent field, and `injection_observation.action_taken` is pinned to `ignored_and_reported`.
- Severity floor: I found no bypass. `category` is unconditionally required, the floor at `:1046-1075` fires on the six high-consequence categories, and the semantic check at `:219-222` forces `fingerprint.category`/`criterion_id` to match the finding, closing the obvious fingerprint-side dodge.
- Duplicate keys are rejected at every nesting level via `object_pairs_hook` (`:36-42`), and trailing JSON, non-object root, empty/whitespace-only input, UTF-8 BOM, oversized input, and `NaN`/`Infinity` are all rejected (`:64-98`).
- `no_findings` cannot coexist with findings or non-zero counts (`:365-387`, plus the semantic count check at `:241-242`); `unable_to_complete` requires a blocking limitation.
- Layering fails closed: schema failure short-circuits before semantic checks, and a missing `jsonschema` dependency yields `contract_valid: false` rather than a skipped layer (`:106-114`).

## Acceptance criteria status

| ID | Status | Basis |
|---|---|---|
| AC-C01 | **Unverified — no defect found by inspection** | Schema is structurally Draft 2020-12-shaped; all `$ref`s are local fragments, so `check_schema` needs no network. Not executed (Bash denied). |
| AC-C02 | **Unverified** | Fixtures outside the permitted read set. |
| AC-C03 | **At risk** | Two of the twelve named invalid classes are affected: deep-nesting/oversized inputs crash instead of returning a typed transport error (RV-04), and the coarse schema messages (nit) make "failed for the intended reason" unassertable from the output. Fixture files not read. |
| AC-C04 | **Unverified** | Test harness outside the permitted read set. |
| AC-C05 | **FAIL** | Output carries no acceptance decision (good), but `contract_valid: true` is overloaded between document validation and schema self-check and can be emitted with exit 0 for a missing/forged document (RV-09); stdout is empty on the crash paths (RV-04). |
| AC-C06 | **Unverified** | Requires execution and repo-wide diff inspection. |
| AC-C07 | **Unverified** | Requires repo-wide status; the packet's own claim was not credited. |

**Advisory verdict (non-authoritative):** not ready for the next slice. RV-01/02/03 combine into a single working attack — a `targeted_verification` document that declares every prior finding `appears_fixed` with empty-string evidence and a self-supplied prior digest is reported `contract_valid: true`, exit 0. RV-04/05 mean the tool's failure channel is not yet machine-readable in both directions. The deterministic coordinator should decide state.
