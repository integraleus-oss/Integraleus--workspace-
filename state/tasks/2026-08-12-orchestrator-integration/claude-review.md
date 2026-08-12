I reviewed all six slice files plus the accepted contract/policy core (read-only). Note up front: **Bash was denied in this session**, so I could not execute the 9 integration tests or the 84 core tests; every finding below is derived from reading code, schema, and validator semantics, and I flag where a reproduction would be needed.

---

# Spec findings

## BLOCKER-1 — An incomplete review projects as a clean review and can reach `ACCEPTED`

**File:** `state/tasks/2026-08-12-orchestrator-integration/review_projection.py:111-126` (also `:60`, where the verdict is loaded but `conclusion`, `criteria_coverage`, and `limitations` are never read)

**Failure scenario:**
The projection carries only mode, scope, paths, findings, and verified IDs. The reviewer's *own statement about whether the review happened* is dropped. Two contract-valid documents therefore project identically to a clean full review:

1. `review.review_mode = "final_full"`, `conclusion.status = "unable_to_complete"`, `conclusion.unable_to_complete_reason = "environment_unusable"`, `limitations = [{code: "environment_unavailable", description: ..., blocking: true}]`, `findings = []`, `counts` all zero, `criteria_coverage = [{AC-1, statement_digest, status: "not_reviewed", verification_method: "not_attempted", notes: "..."}]`.
2. Same, but `conclusion.status = "findings_present"` with one advisory nit and every criterion `not_reviewed`.

Both pass the validator: `review-verdict.schema.json:415-457` permits `unable_to_complete` (it only requires a reason plus one blocking limitation — `$defs/limitation:1470-1508` makes `evidence_ids` optional); `review-verdict.schema.json:532-557` puts no coverage-status constraint on `final_full`; `_validate_trusted_manifest` (`validate_review_verdict.py:463-465`) only requires the coverage *ID set* to match the trusted criteria, not the statuses; and `semantic_errors` constrains coverage status only for `conclusion.status == "no_findings"` (`validate_review_verdict.py:~670-680`). So `contract_valid` is true.

The resulting projection has `findings: []`, `review_mode: "final_full"`, `coverage_scope: "full"`. In the policy core: `_open_blocking_findings` → empty, gates pass, evidence passes, `_final_full_ok` (`orchestrator_policy.py:1122-1130`) returns true → **`ACCEPTED / R17_ACCEPT`** at `orchestrator_policy.py:1336-1345`. The core cannot defend itself here — `_validate_reviewer_report` (`orchestrator_policy.py:796-811`) has no field for conclusion or coverage, so the core structurally assumes the projection builder only projects *completed* reviews. This slice is that builder, and it does not enforce the assumption.

This is the "invent acceptance authority" case in review question 2: a reviewer that explicitly says "I could not review this" is converted into acceptance authority by the adapter, not by the core.

**Bounded remediation** (in `build_projection`, before constructing the projection; no core change):
- raise `ProjectionError` when `verdict["conclusion"]["status"] == "unable_to_complete"`;
- raise `ProjectionError` when any `verdict["limitations"][*]["blocking"] is True`;
- for `review_mode in ("initial_full", "final_full")`, raise `ProjectionError` when any `criteria_coverage[*]["status"]` is not in `{"satisfied", "violated", "partially_satisfied"}`.

Refusing to project (rather than synthesising a finding) is the correct fail-closed shape: the coordinator must handle an incomplete review as escalation input, and no finding is invented. Document the rule in `README.md` next to the existing trust-boundary paragraph, and add a regression test asserting each of the three inputs yields no decision.

---

## MAJOR-2 — A contract-valid finding with no location aborts the entire run

**File:** `state/tasks/2026-08-12-orchestrator-integration/review_projection.py:88-91`

**Failure scenario:**
`path = location.get("path") or finding.get("fingerprint", {}).get("normalized_path")`. Both may legitimately be absent or null: `location` is `oneOf [null, location]` (`review-verdict.schema.json:993-1002`), `fingerprint.normalized_path` is `oneOf [null, relative_path]` (`:715-724`), and `location_absent_reason` (`:1003-1012`, values incl. `cross_cutting`, `runtime_only`) is the contract's sanctioned way to file a finding with no source location. For blocker/major the schema's `anyOf` accepts `location_absent_reason` in place of `location`; for nit there is no location requirement at all.

So a fully contract-valid `initial_full` verdict carrying one `blocker` with `location_absent_reason: "cross_cutting"` and `normalized_path: null` raises `ProjectionError("review finding has no usable path")` — the run produces **no decision at all** instead of `REWORK / R11_OPEN_FINDINGS`. The blocker is dropped on the floor and the orchestrator stalls. The same happens for the far more common case of an advisory nit with no location.

`path` is display-only downstream: `merge_finding_registry` (`orchestrator_policy.py:1046-1052`) stores it in history, and no rule reads it. The core only requires a non-empty string (`orchestrator_policy.py:861-862`).

**Bounded remediation:** add a deterministic third fallback rather than erroring, e.g. `f"<no-location:{finding.get('location_absent_reason', 'unspecified')}>"`, keeping the `ProjectionError` only for the impossible case of a non-string `location.path`. Add tests for (a) blocker + `location_absent_reason`, (b) nit with `location: null`.

---

## MAJOR-3 — Failure paths are not auditable, and the failed `run_name` is permanently burned

**File:** `state/tasks/2026-08-12-orchestrator-integration/local_orchestrator_runner.py:50-69` (dir created at `:53`, first possible failure at `:63`, later at `:72`, `:75-78`, `:79`)

**Failure scenario:**
`run_dir.mkdir(parents=True)` executes before any input is read or validated. Every subsequent failure — missing input file (`:63`), contract-invalid verdict or binding mismatch (`:72`), policy fixture missing a key (`:75-78`) — propagates out of `run()` with **nothing written into the run directory**. The directory is left holding read-only input snapshots, no `review-validation.json`, no error record, no `run-result.json`. The only trace of *why* the run failed is the JSON line on stdout from `main()` (`:109-112`), which is lost if the operator did not capture it, and which is absent entirely for library callers.

The slice's own test `test_contract_invalid_review_produces_no_decision` (`tests/test_integration.py:199-205`) asserts the absence of `decision.json` but never checks that the failure was recorded anywhere.

Second-order effect: because `run_dir.exists()` refuses reuse (`:51-52`), retrying the corrected inputs under the same `run_name` is refused forever. Combined with a run directory that is indistinguishable from a successful one except by the absence of files, the audit trail accumulates unlabelled partial runs.

This directly answers review question 4: input snapshots survive, failure reasons do not.

**Bounded remediation:** wrap the body after `run_dir.mkdir` in `try/except Exception as exc:`, write `run-error.json` (`{document_type: "local_orchestrator_run_error", schema_version, run_name, error: {type, message}, input_digests: <those snapshotted so far>}`) into `run_dir`, then re-raise. Keep the never-overwrite rule. Add a test asserting `run-error.json` exists and `decision.json` does not, for both the contract-invalid and missing-input cases.

---

## MINOR-4 — `run-result.json` does not record the runner exit status or the bundle digest (AC-04)

**File:** `state/tasks/2026-08-12-orchestrator-integration/local_orchestrator_runner.py:86-95`

**Failure scenario:** AC-04 requires output to include "the contract-validation result, policy decision, exit status, and content digests". Validation and decision are written; the exit status appears nowhere in any artifact (only as the process return code in `main()`), and `input-run-bundle.json` is snapshotted at `:68-69` but excluded from `input_digests` at `:92` — so the manifest that ties the run together is not itself digested. A later auditor reading only `run_dir` cannot confirm which bundle produced the run.

**Bounded remediation:** add `"run_bundle_digest": _sha256(run_dir / "input-run-bundle.json")` and `"exit_status": "OK"` to the manifest at `:86-95`, and assert both in the existing runner test.

---

# Standards findings

## MINOR-5 — Bundle path fields escape the bundle directory

**File:** `state/tasks/2026-08-12-orchestrator-integration/local_orchestrator_runner.py:61`

**Failure scenario:** `source = (base / bundle[name]).resolve()` applies no containment check. `"review_verdict": "/etc/some.json"` resolves to the absolute path (Python discards `base` when the right operand is absolute), and `"../../../elsewhere/x.json"` traverses upward. The file is then copied into the run directory at `:65`. Exposure is bounded — the file must survive the strict JSON parser and, for the verdict, full contract validation — but `--runs-root` is likewise unconstrained, so the effective input/output boundary claimed by AC-02/AC-03 is not enforced anywhere in code.

**Bounded remediation:** at `:61`, reject absolute paths and any `..` segment in `bundle[name]`, and assert `source.is_relative_to(base)` after `resolve()`; raise `ProjectionError(f"input path escapes bundle directory: {name}")`. Add one test per rejection.

## MINOR-6 — "Immutable snapshot" overstates `chmod(0o444)`, and digests are taken from disk after evaluation

**File:** `state/tasks/2026-08-12-orchestrator-integration/local_orchestrator_runner.py:65-69` and `:92`

**Failure scenario:** `0o444` is advisory against the file's own owner, who can `chmod` it back; the run directory itself stays writable, so a snapshot can be unlinked and replaced. More concretely, the bytes are read at least three times — by `validate_document`, by `_load_json` inside `build_projection` (`review_projection.py:52` then `:60`), and finally by `_sha256` at `:92` — so `input_digests` records the file's state *after* the decision was made, not the bytes the decision was made from. Under the stated single-user local threat model this is not exploitable, but `README.md:54-56` and AC-03 claim more immutability than the code delivers.

**Bounded remediation:** read each snapshot once into memory, digest those exact bytes, and reuse the parsed objects; or, if the double-read stays, soften the README wording to "snapshots are marked read-only" and state that digests are recorded post-evaluation.

## INFO-7 — Assorted

- `local_orchestrator_runner.py:80-81`: the `ACCEPTED and not contract_valid` guard is unreachable — `build_projection` already raises at `review_projection.py:57-58`. Harmless, but it advertises a fail-closed check that is not actually doing work; keep it only with a comment marking it as a belt-and-braces assertion.
- `local_orchestrator_runner.py:14` imports `review_projection` by bare name, so the documented invocation in `README.md:50-52` works only with the slice directory on `sys.path` (i.e. run from that directory). Either note the `cd` in the README or insert the script's own directory into `sys.path`.
- `review_projection.py:14` anchors the core via `parents[3]`; moving the slice silently repoints `CORE`. Consider asserting `CORE / "orchestrator_policy.py"` exists at import with a clear error.
- `verdict["injection_attempts_observed"]` and `infra_symptoms` are dropped by the projection. Correct for the current contract (the core has no field for them), but worth an explicit README line so the omission reads as deliberate.

---

# Answers to the review questions

1. **Invalid document / binding mismatch reaching a decision** — No. `build_projection` raises before any policy call (`review_projection.py:57-58`, `:66-84`), and the runner calls `POLICY.decide` only after (`local_orchestrator_runner.py:72-79`). The binding cross-check on `task_id`/`run_id`/`attempt_epoch` is genuine, and because the validator forces `subject == trusted_manifest.subject`, checking against the verdict is equivalent to checking against the manifest. `spec_digest` and `reviewed_tree_digest` are unanchored in the adapter but self-defend in the core (`_binding_errors` → `R01_BINDING`; `orchestrator_policy.py:1189` → `R03_STALE`).
2. **Falsely closing findings / downgrading severity / inventing authority** — Closure and severity are clean: severity is copied verbatim, and only exact `appears_fixed` enters `verified_finding_ids` (`review_projection.py:106-109`), which the validator further constrains (results must exactly cover open prior IDs, `validate_review_verdict.py:~636`; `appears_fixed` requires command or digest-bound evidence, `:599-605`), and `merge_finding_registry` closes only for the current tree in targeted mode (`orchestrator_policy.py:1064-1076`). **Acceptance authority is not clean — see BLOCKER-1.**
3. **Path escape / overwriting audit artifacts** — Overwrite protection holds (`:51-52`, and `mkdir` without `exist_ok` closes the TOCTOU window by raising). Input path resolution does escape — MINOR-5.
4. **Immutability and auditable failure paths** — Immutability is adequate for the stated local threat model but overstated in the README (MINOR-6). Failure paths are **not** auditable (MAJOR-3).
5. **Deterministic replay** — Holds. `_digest` (`review_projection.py:41-43`) is byte-identical to the core's `_canonical_bytes` (`orchestrator_policy.py:73-74`); projection lists are sorted; the core takes no clock, randomness, or environment. `test_replay_in_new_run_directory_is_byte_deterministic` covers it (unexecuted here).
6. **Four outcomes exercised without weakening the core** — `ACCEPTED`, `REWORK/R11`, `FAILED_INFRA`, `ESCALATED/R01` are each exercised, and no core file is touched. But the `ACCEPTED` test asserts only the happy path; BLOCKER-1 shows the adapter widens the set of inputs that reach it.
7. **Missing tests vs TASK_PACKET** — AC-07 is not met. The entire `targeted_verification` path is untested: no test sets `review_mode: "targeted_verification"`, no test passes a non-null `prior_findings` (so `local_orchestrator_runner.py:57-58` never executes), and the README's central trust rule — that only `appears_fixed` closes a registry finding, while `still_open` / `not_verifiable` / `no_longer_applicable` do not — has no regression at all. Also missing: findings without a location (MAJOR-2), failure-artifact assertions (MAJOR-3), and a negative test that an incomplete review cannot reach `ACCEPTED` (BLOCKER-1).

**Verification caveat:** the packet's claims of 9/9 and 84/84 green, `py_compile`, and `git diff --check` are unverified in this session — Bash was denied, so I executed nothing. AC-08 and AC-09 are outside what I could confirm.

INTEGRATION_REWORK
