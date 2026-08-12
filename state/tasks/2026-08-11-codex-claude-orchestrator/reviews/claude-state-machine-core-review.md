Bash execution is denied in this session, so I could not run the repro scripts I drafted; every finding below is confirmed by line-exact reading of the source, and each repro is written so you can run it directly against `decide()`. Repros use `base_bundle()` from the test file (which the suite asserts yields `ACCEPTED`/`R17_ACCEPT` at line 167).

# Confirmed findings

All line references are `implementation/orchestrator_policy.py` unless noted.

---

**SM-01 — blocker — `orchestrator_policy.py:66-84` (+ `:747-751`, `:780`)**
Digest normalization is lossy in a way the decision logic is not: `_normalized_for_digest` sorts *any* list whose parent key name is in the fixed set (`findings`, `evidence_artifacts`, …) at *any* depth — including inside the free-form `execution_report.payload` — while the R04 payload check at line 780 hashes the payload raw. Two documents with different payload bytes therefore share `input_digests`, and the terminal-replay shortcut at 747-751 keys only on `input_digests`, so a document whose payload contradicts its `payload_digest` is served a cached `ACCEPTED` instead of `R04_INCOMPLETE`.

*Failure scenario:* run A is legitimately accepted and the orchestrator records its decision in `ledger.terminal_decision`. A later submission with the payload's inner array reordered (so `canonical_digest(payload) != payload_digest`) is returned as `ACCEPTED` without any validation.

*Minimal repro:*
```python
a = base_bundle()
a["execution_report"]["payload"] = {"findings": [{"x": 1}, {"y": 2}]}
a["execution_report"]["payload_digest"] = policy.canonical_digest(a["execution_report"]["payload"])
first = decide(a)                                  # ACCEPTED / R17_ACCEPT

b = copy.deepcopy(a)
b["ledger"]["terminal_decision"] = first
b["execution_report"]["payload"] = {"findings": [{"y": 2}, {"x": 1}]}   # payload_digest left stale
decide(b)      # returns ACCEPTED; without the terminal_decision it is ESCALATED / R04_INCOMPLETE
```
*Violates:* AC-SM04 (no mismatched/incomplete input reaches `ACCEPTED`); the collision itself contradicts AC-SM03's premise that `input_digests` identify semantic inputs.

---

**SM-02 — blocker — `orchestrator_policy.py:704-707` (validation gap `:436-451`)**
`_evidence_failures` builds `artifacts[req_id] = artifact` last-wins, and `_validate_execution_report` never rejects duplicate `req_id`s in `evidence_artifacts` (unlike `required_evidence`, which is deduped at 309-311). A digest-mismatched artifact is silently ignored when a duplicate entry follows it, and the outcome flips with array order that `_normalized_for_digest` (line 71-81) declares meaningless.

*Failure scenario:* an execution report carrying a required artifact with the wrong digest plus a duplicate entry with the right digest is `ACCEPTED`; the byte-identical-by-digest permutation is `REWORK`.

*Minimal repro:*
```python
good = {"req_id": "schema-log", "digest": digest("c"), "bytes": 100}
bad  = {"req_id": "schema-log", "digest": digest("f"), "bytes": 100}
unit = {"req_id": "unit-log",   "digest": digest("d"), "bytes": 200}

b1 = base_bundle(); b1["execution_report"]["evidence_artifacts"] = [unit, bad, good]
b2 = base_bundle(); b2["execution_report"]["evidence_artifacts"] = [unit, good, bad]
decide(b1)   # ACCEPTED / R17_ACCEPT
decide(b2)   # REWORK / R13_EVIDENCE
# decide(b1)["input_digests"] == decide(b2)["input_digests"]
```
*Violates:* AC-SM04 (digest-mismatched evidence reaches `ACCEPTED`) and AC-SM03 (identical canonical inputs, divergent decisions/digests).

---

**SM-03 — blocker — `orchestrator_policy.py:612-617` (validation gap `:380-381`)**
`_registry_records` collapses the ledger registry into a dict last-wins on `finding_id`, and `_validate_ledger` checks only that `finding_registry` is a dict — its contents are never validated. Two records for the same `finding_id` mean one is deleted outright from `merged_registry`; which one survives depends on list order that `ledger_pre` normalization sorts away.

*Failure scenario:* a registry holding an `open` `blocker` record and a stale `resolved_verified` record for the same ID drops the open blocker entirely, yielding `ACCEPTED` and a `registry_digest_after` from which the blocker has vanished.

*Minimal repro:*
```python
open_rec = registry_with("fnd_x", "blocker", "open")["findings"][0]
res_rec  = registry_with("fnd_x", "blocker", "resolved_verified")["findings"][0]
reg = lambda items: {"document_type": "finding_registry", "schema_version": "1.0.0", "findings": items}

b1 = base_bundle(); b1["ledger"]["finding_registry"] = reg([open_rec, res_rec])
b2 = base_bundle(); b2["ledger"]["finding_registry"] = reg([res_rec, open_rec])
decide(b1)   # ACCEPTED / R17_ACCEPT   <- open blocker silently deleted
decide(b2)   # REWORK / R11_OPEN_FINDINGS
# input_digests identical (list under key "findings" is sorted at line 71-81)
```
*Violates:* AC-SM09 (registry deduplicates without loss, no deletion — packet "Finding registry rules": *No deletion*), AC-SM04, AC-SM03.

---

**SM-04 — major — `orchestrator_policy.py:747-751`**
The terminal-replay shortcut runs before `_validate_task_policy`/`_validate_ledger`/`_validate_execution_report`/`_validate_reviewer_report` and returns the stored object verbatim: no re-derivation, no check that `terminal["decision_digest"]` matches its own content, no cross-check of `outcome`/`budgets_after`/`registry_digest_after`. The only gate is that `terminal["input_digests"]` equals digests computed from the same caller-supplied documents — a value any ledger writer can recompute with the module's own pure helpers. This is the enabling mechanism for SM-01.

*Failure scenario:* a ledger that `_validate_ledger` would reject (unknown field, bool/negative counter, missing `expected_subject`) is never inspected; whatever decision object it carries becomes the engine's output, including an `ACCEPTED` whose `decision_digest` is unverifiable.

*Minimal repro (no hash math needed for the echo half):*
```python
b = base_bundle()
first = decide(b)
b["ledger"]["terminal_decision"] = {**first, "budgets_after": {"rework_used": 999},
                                    "decision_digest": "sha256:" + "0" * 64}
decide(b)    # returned verbatim: ACCEPTED with a decision_digest that does not match its content
```
For the invalid-ledger half, mutate any ledger field and re-stamp `terminal_decision["input_digests"] = policy._input_digests(tp, ledger, er, rr)`; `decide` returns `ACCEPTED` with no validation performed.
*Violates:* AC-SM04 (invalid input must not reach `ACCEPTED`) and AC-SM02 (decision digest must be deterministically derived from the decision).

---

**SM-05 — major — `orchestrator_policy.py:697-698` and `:656-657`**
Unrecognized registry state fails open. `_open_blocking_findings` maps any unknown `effective_severity` to rank 0 (`info`) and treats any `status` other than the exact string `"open"` as non-blocking; `merge_finding_registry` line 656 applies the same rank-0 default to the *prior* record, so an unknown prior severity is overwritten by a lower observed one. Nothing validates the ledger's `finding_registry` contents (only `--check-schema` self-validates `finding-registry.schema.json`; it is never applied to input).

*Failure scenario:* an open finding recorded with a severity label outside `SEVERITY_RANK` (or `"Open"` instead of `"open"`) is treated as advisory, and a subsequent `nit` observation rewrites its `effective_severity` down to `"nit"` in the persisted registry.

*Minimal repro:*
```python
rec = registry_with("fnd_x", "critical", "open")           # severity outside SEVERITY_RANK
b = base_bundle(); b["ledger"]["finding_registry"] = rec
decide(b)                                                  # ACCEPTED / R17_ACCEPT

b2 = base_bundle(); b2["ledger"]["finding_registry"] = rec
b2["reviewer_report"]["findings"] = [finding("fnd_x", "occ-new", "nit")]
decide(b2)["registry_digest_after"]                        # record now effective_severity == "nit"
```
*Violates:* AC-SM09 (registry prevents severity downgrade) and AC-SM04.

---

**SM-06 — major — `orchestrator_policy.py:289`**
`len(gates) != len(set(gates))` is evaluated whenever `mandatory_gates` is a list, including after line 287 has already recorded it as malformed. A list containing a non-hashable element raises `TypeError: unhashable type` out of `_validate_task_policy`, which no caller catches — `decide()` crashes instead of returning fail-closed `ESCALATED`, and `main()` (line 991) only handles `PolicyInputError`.

*Failure scenario:* a task policy whose `mandatory_gates` entries are objects or arrays aborts the engine with a traceback rather than producing an auditable `R01_BINDING` decision.

*Minimal repro:*
```python
b = base_bundle()
b["task_policy"]["mandatory_gates"] = [{"gate": "unit_tests"}]   # or [["unit_tests"]]
decide(b)    # TypeError: unhashable type: 'dict'  (expected ESCALATED / R01_BINDING)
```
*Violates:* AC-SM10 (malformed containers/types must be covered and fail closed) and AC-SM02 (every invocation must emit strict machine decision JSON). Note the fixture CLI path may mask this behind `_validate_against_state_schema`, but `decide()` is the public entry point the tests exercise directly.

---

**SM-07 — major — `orchestrator_policy.py:709-722` (with `:71-81`, `:227`)**
`_evidence_failures` emits failures in `required_evidence` list order, and that order flows into `reason_codes` and the `PROVIDE_EVIDENCE.req_ids` directive, which `_with_decision_digest` hashes positionally. But `_normalized_for_digest` sorts `required_evidence`, declaring its order semantically irrelevant — so permuting it yields identical `input_digests` and a different `decision_digest`.

*Failure scenario:* two byte-identical-by-input-digest task policies produce non-byte-identical decision JSON, breaking replay matching (SM-04's cache compares whole decisions in tests) and audit reproducibility.

*Minimal repro:*
```python
b1 = base_bundle(); b1["execution_report"]["evidence_artifacts"] = []
b2 = copy.deepcopy(b1)
b2["task_policy"]["required_evidence"] = list(reversed(b2["task_policy"]["required_evidence"]))
d1, d2 = decide(b1), decide(b2)
d1["input_digests"] == d2["input_digests"]      # True
d1["decision_digest"] == d2["decision_digest"]  # False; reason_codes order differs
```
*Violates:* AC-SM03 (identical semantic inputs must yield byte-identical canonical decision JSON/digest).

---

# Notes

- Root cause shared by SM-01/SM-02/SM-03/SM-07: `_normalized_for_digest` defines an order-insensitive semantics that `decide()` does not implement (last-wins dict builds, positional reason codes, raw payload hashing). Any fix should make the decision path canonicalize the same lists it hashes, and reject duplicate keys in `evidence_artifacts` and `finding_registry.findings` rather than resolving them.
- Existing coverage does not reach these: `test_permuted_finding_order_yields_identical_decision` (line 415) permutes only `reviewer_report.findings`, which `merge_finding_registry` explicitly sorts at line 635.
- Observed but not reported as blocker/major: the evidence branch at line 848 checks `_rework_available` without `_no_progress_trip`, unlike the gate (812) and findings (831) branches — inconsistent with packet precedence item 6, but still bounded by the rework budget.

I could not execute these repros (Bash denied), and I make no claim of authority to accept or reject this implementation — the seven items above are the confirmed defects from static review of the three files in scope. Not `TARGETED_PASS`.
