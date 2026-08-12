Bash is denied in this session (same as R1), so everything below is a line-exact static control-flow proof against the five in-scope files. I executed nothing.

# Targeted closure verification: State Machine R2

Line references are `implementation/orchestrator_policy.py` unless noted.

---

**1. SM-07 residue — untouched-record history order — `closed`**

The R1 defect was that `merge_finding_registry` sorted `history` only inside the reviewer-findings loop (`:877`), so a record absent from `reviewer_report.findings` and from `verified_ids - current_finding_ids` was emitted with its input array order intact.

R2 adds an unconditional normalization pass over the whole record set after both mutation blocks:

- `:895-897` — `for record in records.values(): record["history"] = sorted(_as_list(record.get("history")), key=_canonical_sort_key); record["occurrence_count"] = len(record["history"])`. `records` is the full `_registry_records` map (`:810-815`), so this covers records the current review never touched.
- `:898` — `result["findings"] = [records[key] for key in sorted(records)]` keeps record order keyed on `finding_id`.

Replaying the R1 repro: with `reviewer_report["findings"] == []` and `review_mode == "final_full"`, neither `:837-879` nor `:882-893` executes, so `records["fnd_done"]["history"]` is still the raw input list on entry to `:895`. `sorted(...)` over the same two-element multiset with the same key function yields the same list for both permutations, so `:325` (`canonical_digest(registry_after)`) and hence `:303` (`decision_digest`) are byte-identical. The previously divergent `registry_digest_after` now converges.

`_canonical_sort_key:125-129` → `_canonical_bytes:73` uses `sort_keys=True`, so the key is content-determined and independent of dict insertion order; the fallback branch is unreachable for JSON-safe entries.

---

**2. Permutation-equivalence of the complete decision — `verified`**

I traced every field of the emitted decision (`_make_decision:316-326`) for history-order dependence:

- `input_digests` — `("ledger","finding_registry","findings","*","history")` at `:86` matches the path built by `_normalized_for_digest:141-147` (`ledger → finding_registry → findings → * → history`), so `ledger_pre` is already order-insensitive; `_ledger_for_digest:269-273` strips `terminal_decision` first.
- `registry_digest_after` — closed by item 1.
- `reason_codes` / `directives` — the only registry-derived producers are `_open_blocking_findings:902-910` (`sorted(set(...))`, reads only `status`/`effective_severity`/`finding_id`) and `open_blocking[:20]` (`:1056`). No traversal reads `history` order. `_evidence_failures:919-936` sorts requirements and returns `sorted(set(...))`; `_failed_gates:800-807` walks `mandatory_gates`, which is deliberately absent from `UNORDERED_DIGEST_LIST_PATHS` and therefore order-consistent between digest and traversal.
- `budgets_after` — `_budget_state:290-298`, registry-independent.
- `outcome`/`rule_id` — `_decide_policy` reads no history.

`occurrence_count` is recomputed at `:897` but is never consumed by any decision branch, so the recomputation cannot shift an outcome; for validated input it is a no-op because `:450` already enforces `occurrence_count == len(history)`.

The regression at `tests/test_orchestrator_policy.py:542-584` is exactly the one the packet specified: one untouched `resolved_verified` record, two valid history entries reversed, asserting equal `(outcome, rule_id)`, `input_digests`, `registry_digest_after`, `decision_digest`, and `policy._canonical_bytes(decision)` — the last assertion covers "complete canonical decision JSON," not just the digest. I confirmed the fixture reaches `ACCEPTED`/`R17_ACCEPT` rather than short-circuiting: the record is `resolved_verified` so `_open_blocking_findings` returns `[]`, and `_final_full_ok:939-947` holds on the base bundle.

---

**3. Validator/merge occurrence identity — `agreed and documented`**

One invariant is chosen and stated in all three places:

- `STATE_MACHINE.md:8-12` — identity is the pair `(review_id, occurrence_id)`, unique within one finding's history, `occurrence_id` reusable by a different review, merge append-only, histories emitted canonically.
- `merge_finding_registry` docstring `:823-827` and the dedup key `:870-875` — `occurrence_key = (review_id, occurrence_id)` compared against a set built from the same pair.
- `_validate_registry_record:452,467-471` — `seen_history_keys: set[tuple[str, str]]` keyed on the same pair.

This is packet option 2, and it is not a weakening of the append-only rule: `:875` appends only when the pair is new and never rewrites an existing entry. `tests:597-600` pins that by re-merging a review whose finding differs only in `path` and asserting the history is unchanged.

`_validate_reviewer_report:728-730` additionally rejects an `occurrence_id` reused across two *different findings within one report*. That is stricter than the registry invariant requires, but it is a same-`review_id` constraint that cannot produce an emit-then-reject cycle, and it is pre-existing rather than R2-introduced. Noting it only because it falls inside the "validator and merge agree" check; it is below the reporting floor and I did not pursue it.

---

**4. Emit-then-reject on cross-review ID reuse — `closed`**

Static round-trip proof that every registry `merge_finding_registry` can emit passes `_validate_finding_registry` on the next invocation:

- Top-level keys are exactly `{document_type, schema_version, findings}` (`:829-833`) — satisfies `:485-490`.
- Record key set: new records are built with exactly the six keys at `:849-856`; carried-over records were validated against the same `allowed` set at `:414`. Mutations at `:859-861`, `:877-878`, `:889-892`, `:896-897` only write keys already in that set.
- `effective_severity` is always `RANK_SEVERITY[...]` (`:852`, `:859`), whose value set `{info,nit,major,blocker}` equals `REGISTRY_SEVERITIES:38`. Note `SEVERITY_RANK` maps `"minor"→1→"nit"`, so the reviewer-permitted `"minor"` is never emitted into a registry that would fail `:428`.
- `status`/`resolved_at` pairing: touched records get `("open", None)` (`:860-861`); the resolution block sets both together (`:889-892`); untouched records were validated at `:434-445`.
- `occurrence_count == len(history)` by construction at `:897`, satisfying `:450`.
- History entry fields: `review_id` non-empty str via `_validate_reviewer_report:691-693`; `occurrence_id` non-empty str via `:725-726`; `path` non-empty str via `:738-739`; `tree_digest` is `exec_subject["tree_digest"]`, non-empty str via `_validate_execution_report:604-605`; `severity` from `RANK_SEVERITY`. Key set matches `allowed_entry:458`.
- Duplicate-pair rejection at `:469-471` cannot fire, because `:875` refuses to append a pair already present and the input history was validated pair-unique.

The reuse case specifically: prior history holds `("review-prior","occ-reused")`; a later review `review-later` reuses `occ-reused`. `:870` computes `("review-later","occ-reused")`, which is not in `history_keys`, so it appends; `:452-471` sees two distinct pairs and returns no error. `tests:586-604` pins this end-to-end — direct `_validate_finding_registry(emitted) == []` plus a full `decide()` on a ledger carrying the engine-emitted registry.

`merge_finding_registry` is only reached at `:1035`, after `_validate_ledger`/`_validate_execution_report` (`:1147-1149`) and `_validate_reviewer_report` (`:1150-1152`) have short-circuited, so every precondition above holds on the decision path.

---

**5. R2-introduced blocker/major — none found**

The R2 delta inside these boundaries is `:823-827` (docstring), `:452/:467-471` (identity key), `:895-897` (normalization pass), `STATE_MACHINE.md:8-12`, and the two new tests. I checked each for regression:

- The `:895-897` pass writes only `history` and `occurrence_count`, both already normalized on the touched path (`:877-878`), so it is idempotent there and cannot alter any previously passing branch.
- Relaxing the history key from bare `occurrence_id` to the pair does not open an exploitable gap: history depth feeds only `occurrence_count`, which no rule in `_decide_policy:984-1128` reads. Severity monotonicity (`:858`) and duplicate-`finding_id` rejection (`:420-421`) are untouched.
- Canonical history ordering discards chronological order, but no reader depends on it (`history` is consumed only at `:862`, `:871-874`, `:896-897`), and `STATE_MACHINE.md:11-12` states it.
- `tests:636-644` still fails closed under the new identity: the appended entry is an exact copy, so its pair collides at `:469`.

The one below-floor observation carried over from R1 is unchanged and, per the packet, not counted: `decide()` has no depth bound of its own — `_input_digests` at `:1143` sits outside the `try` at `:1146`, so a deeply nested dict passed directly to `decide()` raises `RecursionError`. Unreachable from the CLI, which parses through `parse_json_file`/`_walk_limits:177-181` at depth 32.

---

All five verification items are satisfied. The two required regressions are present, exact, and match the chosen invariant. I could not execute the suite (Bash denied), so I claim no test-execution evidence and no authority to accept the slice — the coordinator owns tests and gates.

TARGETED_PASS
