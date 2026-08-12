Bash is denied in this session, so — as with the prior round — every item below is a line-exact static control-flow proof against the six in-scope files. I did not run anything.

# Targeted verification: SM-01 … SM-07 against R1

All line references are `implementation/orchestrator_policy.py` unless noted.

---

**SM-01 — `fixed`**

Two mechanisms both closed.

1. Lossy key-name normalization is gone. `UNORDERED_DIGEST_LIST_PATHS` (`:80-93`) is now a set of *absolute* paths, matched by `_path_matches` (`:96-97`) which requires equal length and positional equality, and `_normalized_for_digest` (`:139-148`) threads a root-anchored path from `_input_digests` (`:283-286`). A list at `("execution_report","payload","findings")` is length 3 and matches none of the length-3 patterns (`("execution_report","subject","changed_paths")`, `("ledger","expected_subject","changed_paths")`, `("ledger","finding_registry","findings")`), so payload interiors are no longer sorted. The old collision is unreachable.
2. Terminal replay no longer precedes validation. `decide` (`:1136-1161`) runs `_validate_task_policy`/`_validate_ledger`/`_validate_execution_report` (`:1140`), `_validate_reviewer_report` (`:1143`), `_binding_errors` (`:1147`), then `_decide_policy` (`:1151`) — which contains the R02/R03/R04 checks (`:986-1002`) — and only consults `ledger["terminal_decision"]` at `:1154`.

Original repro replayed: payload permuted with a stale `payload_digest` reaches `:1001`, `canonical_digest(payload) != payload_digest` → `R04_INCOMPLETE`; `:1152` short-circuits on `R04_INCOMPLETE` and returns `derived` without touching the terminal record. Covered by `tests/test_orchestrator_policy.py:442-453` and `:616-625`.

---

**SM-02 — `fixed`**

`_validate_execution_report` now rejects duplicate `evidence_artifacts.req_id` at `:634-635` (`duplicate_artifact_req_id`), which becomes a `schema_errors` entry and short-circuits to `R01_BINDING` at `:1140-1142` before `_evidence_failures` (`:906`) is ever reached. The last-wins dict build at `:907-910` survives but is now unreachable with duplicate keys. Both orderings of the SM-02 repro produce the same `ESCALATED`/`R01_BINDING`. Covered by `test_orchestrator_policy.py:455-462`.

---

**SM-03 — `fixed`**

`_validate_finding_registry` (`:486-503`) and `_validate_registry_record` (`:410-483`) now fully validate registry structure and are wired into `_validate_ledger` at `:561`. Duplicate `finding_id` is rejected at `:420-421` rather than resolved, so `_registry_records`' last-wins collapse (`:815-820`) can no longer delete a record — no history deletion, fail-closed to `R01_BINDING`. Covered by `test_orchestrator_policy.py:464-474`, `:550-570`.

---

**SM-04 — `fixed`**

`_validate_terminal_decision` (`:943-974`) enforces an exact key set (`:947`, against `DECISION_REQUIRED_KEYS` `:39-50`), document type, schema version, `outcome ∈ OUTCOMES`, `rule_id`, container types, `input_digests` equality (`:963`), and recomputes the decision digest over the record's own content (`:971-973`). On failure `_invalid_terminal_decision` (`:1124-1125`) returns `ESCALATED`/`R01_BINDING`/`TERMINAL_DECISION_INVALID` — the stored object is never echoed. The additional `terminal != derived` check (`:1158`) means only a decision the engine independently re-derives from validated inputs can be replayed.

Both halves of the original repro are closed: the forged-digest half fails at `:971-973`; the "mutate the ledger and re-stamp `input_digests`" half never reaches `:1154` because the invalid ledger is rejected at `:1140-1142`. Covered by `test_orchestrator_policy.py:476-503`.

---

**SM-05 — `fixed`**

`REGISTRY_STATUSES`/`REGISTRY_SEVERITIES` (`:37-38`) are enforced against ledger registry records at `:424-429` and against history entries at `:477-478`. An unknown severity (`"critical"`) or off-case status (`"Open"`) is now a validation error → `R01_BINDING`, so the rank-0 defaults at `:859` and `:900` can only ever see values already in `SEVERITY_RANK`. `RANK_SEVERITY` (`:35`) round-trips `{info,nit,major,blocker}`, and `effective_rank = max(prior, observed)` (`:859-860`) cannot downgrade a validated prior. Covered by `test_orchestrator_policy.py:505-512`, `:550-570`.

---

**SM-06 — `fixed`**

Two independent guards. `_validate_task_policy:363-366` puts the duplicate check behind `elif`, so `_has_duplicate_strings` (which skips non-strings, `:258-266`) is only reached for an all-string list — the `set(gates)` construction that raised `TypeError: unhashable type` is gone. Independently, the whole decision body is wrapped in `try/except Exception` (`:1139-1163`) returning fail-closed `ESCALATED`/`R01_BINDING`. I checked the two statements outside that try (`_input_digests` `:1136`, `_budget_state` `:1137`) for malformed containers: `_safe_canonical_digest`/`_canonical_sort_key` (`:125-136`) absorb `TypeError`/`ValueError`, `_normalized_for_digest` sorts dict items by `str(key)`, and `_as_mapping` degrades non-dicts to `{}`. Related short-circuits verified as non-raising: `:619` (`not isinstance(value, str)` fires before `value not in GATE_STATES`) and `:559`. Covered by `test_orchestrator_policy.py:514-529`, `:627-638`.

Non-blocking note (below the severity floor, not counted against R1): `decide()` still has no depth bound of its own — `MAX_DEPTH` is enforced only in `parse_json_file`/`_walk_limits` (`:177-181`), and `_input_digests` at `:1136` sits outside the `try`, so a ~1000-deep dict passed directly to `decide()` would raise `RecursionError`. Not reachable from the CLI path (`evaluate_fixture:1190` parses through `parse_json_file`, capping depth at 32).

---

**SM-07 — `partially_fixed` — remaining `major`**

Fixed half: `_evidence_failures` now sorts requirements by `req_id` (`:912-915`) and returns `sorted(set(failures))` (`:929`), so `reason_codes` and `PROVIDE_EVIDENCE.req_ids` no longer depend on `required_evidence` list order. I also re-checked every other decision traversal against `UNORDERED_DIGEST_LIST_PATHS` and they agree: gate order is digest-ordered *and* traversal-ordered (`mandatory_gates` is deliberately absent from the unordered set), infra signatures are sorted (`:766-771`), open findings are sorted (`:903`), `changed_paths` are compared sorted/as sets (`:994`, `:940`), binding errors are sorted (`:763`).

Remaining half — `registry_digest_after` is order-sensitive for registry records the current review does not touch, while the input digest declares that order meaningless:

- `:86` adds `("ledger","finding_registry","findings","*","history")` to `UNORDERED_DIGEST_LIST_PATHS`, so `_normalized_for_digest` sorts every record's `history` in `ledger_pre` (`:284`).
- `_registry_records:815-820` deep-copies each record with its history order intact.
- `merge_finding_registry` re-sorts `history` only inside the reviewer-findings loop (`:873`); a record whose `finding_id` is not in `reviewer_report.findings` (and not in `verified_ids - current_finding_ids`, `:882`) is emitted verbatim by `:891`.
- `_make_decision:325` hashes the merged registry with plain `canonical_digest`, which preserves array order, and `_with_decision_digest:303` folds that into `decision_digest`.

*Failure scenario:* two ledgers that differ only in the array order of an untouched record's `history` have byte-identical `input_digests` but different `registry_digest_after` and different `decision_digest` — including on the `ACCEPTED` path. Operationally this also breaks terminal replay: a `terminal_decision` recorded under one history ordering fails the `terminal != derived` check at `:1158` when the ledger is re-serialized in the other ordering, returning `ESCALATED`/`R01_BINDING`/`TERMINAL_DECISION_INVALID` in place of the previously recorded `ACCEPTED`.

*Minimal repro* (helpers from `tests/test_orchestrator_policy.py`; each history entry is validation-clean — unique `occurrence_id`, unique `(review_id, occurrence_id)`, `occurrence_count == len(history)`):
```python
h1 = {"review_id": "review-a", "occurrence_id": "occ-1", "severity": "major",
      "path": "implementation/orchestrator_policy.py", "tree_digest": digest("b")}
h2 = {"review_id": "review-b", "occurrence_id": "occ-2", "severity": "major",
      "path": "implementation/orchestrator_policy.py", "tree_digest": digest("b")}

def reg(history):
    return {"document_type": "finding_registry", "schema_version": "1.0.0",
            "findings": [{"finding_id": "fnd_done", "status": "resolved_verified",
                          "effective_severity": "major", "occurrence_count": 2,
                          "resolved_at": {"review_id": "review-b", "tree_digest": digest("b")},
                          "history": history}]}

b1 = base_bundle(); b1["ledger"]["finding_registry"] = reg([h1, h2])
b2 = base_bundle(); b2["ledger"]["finding_registry"] = reg([h2, h1])
d1, d2 = decide(b1), decide(b2)

d1["input_digests"] == d2["input_digests"]            # True  (history sorted at :86/:146)
d1["outcome"] == d2["outcome"] == "ACCEPTED"          # True
d1["registry_digest_after"] == d2["registry_digest_after"]   # False  <-- :325 hashes raw order
d1["decision_digest"] == d2["decision_digest"]        # False
```
*Static proof of the two key steps:* (a) `_canonical_sort_key` orders the normalized entries by canonical bytes, which begin `{"occurrence_id":"occ-1"…}` vs `{"occurrence_id":"occ-2"…}`, so both permutations normalize to `[h1, h2]` — identical `ledger_pre`. (b) With `reviewer_report["findings"] == []` and `review_mode == "final_full"`, neither the loop at `:838-875` nor the resolution block at `:878-889` executes, so `records["fnd_done"]["history"]` is exactly the input list, and `:891` → `:325` hashes `[h1,h2]` vs `[h2,h1]`.

*Violates:* AC-SM03 and the R1 requirement at `CODEX_STATE_MACHINE_REWORK_1.md:31-33` ("semantically equivalent permutations must yield identical decision JSON"). Existing coverage does not reach it: `test_sm07_required_evidence_permutation_yields_identical_decision` (`test_orchestrator_policy.py:531-540`) permutes only `required_evidence`.

*Minimal fix direction:* sort `history` for every record on the merge output path (not only for records touched by the current review), or digest the merged registry through `_normalized_for_digest` with the same path set.

---

**Evidence-rework no-progress inconsistency — `fixed`**

`:1069` now reads `if _rework_available(...) and not _no_progress_trip(...)`, and `:1080` selects `"NO_PROGRESS"` vs `"REWORK_BUDGET_EXHAUSTED"` — byte-for-byte the same shape as the gate branch (`:1033`/`:1044`) and the findings branch (`:1052`/`:1063`). Covered by `test_orchestrator_policy.py:542-548`.

---

# Rework-introduced issues in scope

No introduced blocker/major beyond the SM-07 residue above. One below-floor observation, reported once and not pursued further:

- `:469-471` (new in R1) requires `occurrence_id` to be unique across a record's entire `history`, but `merge_finding_registry:864-872` keys deduplication on `(review_id, occurrence_id)` and `_validate_reviewer_report:733-735` enforces uniqueness only within a single reviewer report. A reviewer that reuses an `occurrence_id` across two reviews of the same finding causes the engine to write a registry it will reject on the next invocation, pinning the run at `ESCALATED`/`R01_BINDING`. Fail-closed, no false `ACCEPTED` and no silent finding loss, so it does not meet the stated severity floor — but the merge path and the new validator should be made to agree on whether `occurrence_id` is globally or per-review unique.

---

SM-01 `fixed`; SM-02 `fixed`; SM-03 `fixed`; SM-04 `fixed`; SM-05 `fixed`; SM-06 `fixed`; SM-07 `partially_fixed` (one remaining `major`); evidence no-progress consistency `fixed`.

I could not execute the repro above (Bash denied), and I claim no authority to accept or reject this implementation — the coordinator owns tests and gates.

TARGETED_REWORK
