I read the four in-scope findings against the current tree. Bash is denied in this session, so — as in R1/R2 — I executed nothing; every claim below is a line-exact static derivation, with runnable repros for the coordinator.

# Targeted closure review R3 — state machine

## Closed

**FF-03 — closed.** `orchestrator-state-machine.schema.json:318-437` now declares `payload` (`:433`, `true`) and `payload_digest` (`:434-436`, `$defs/sha256`) as optional properties with two-way `dependentRequired` (`:321-328`), matching `_validate_execution_report:688-689, 743-746`. The two artifacts now define the same input language, and where they differ the schema is strictly narrower (`sha256` pattern vs. non-empty string), so nothing the schema admits can reach a different outcome than `decide()`; a non-sha256-shaped digest can never equal `canonical_digest(payload)` and falls to `R04_INCOMPLETE` (`:1152-1155`). Coverage is real and CLI-level: `fixtures/policy/valid/accepted_with_payload.json` (paired, ACCEPTED), `fixtures/policy/valid/payload_digest_mismatch.json` (ESCALATED/R04), `fixtures/policy/invalid/missing_payload_digest.json` (schema-rejected), all driven through the real CLI by subprocess in `tests/test_orchestrator_policy.py:681-704`.

**FF-04 — closed.** `STATE_MACHINE.md:24-40` now states the safe order (malformed/binding → replay → stale → incomplete → fresh derivation → terminal equality) and explicitly says replay is not a short-circuit. This matches `decide():1295-1320` exactly: validation `:1299`, reviewer contract `:1302`, binding `:1306`, full derivation `:1310`, terminal read `:1313`. The new early return at `:1311-1312` keeps R02/R03/R04 ahead of the terminal branch, consistent with documented items 2-4. `test_documented_precedence_matches_safe_source_order:706-715` is a real lock — it fails if the source is reordered back to replay-first.

**FF-01 — behavior closed, regression not locked.** `_enforce_decide_input_limits:328-340` runs at `:1296`, inside the `try` and before `_input_digests:1297`; `_walk_limits:183-210` self-bounds at `MAX_DEPTH` before recursing further, so a 3000-level document raises `PolicyInputError("too_deep")` at depth 33 and returns `ESCALATED`/`R01_BINDING` via `:1321-1323`, whose fallback `_json_safe_shape:104-105` is likewise depth-bounded. Moving the digest computation inside the `try` closes the residue independently. The review's exact repro no longer raises. The regression test, however, locks nothing — see R3-02.

**FF-02 — mechanically effective inside the engine, not closed end-to-end.** `_apply_no_progress_transition:931-939` now writes `budgets_after["no_progress_streak"]` on all three rework branches (`:1186`, `:1206`, `:1224`), advancing on a matching prior identity, resetting to 0 otherwise, and tripping at the configured limit (`:921-928`). `prior_attempts` is now strictly validated (`:639-664`), so no prose judgment is involved. The residual gap is R3-01.

---

# Findings

**R3-01 — major — `implementation/orchestrator_policy.py:897-906` and `:927`, vs `implementation/STATE_MACHINE.md:46-50`**

*Violated criterion:* FF-02 fix requirement "make `no_progress` mechanically effective … define **and document** a deterministic progress identity"; the review requirement that documentation agrees with the implementation.

The streak advances only when `prior_attempt["progress_identity"] == _progress_identity(execution_report)` (`:927`). `_progress_identity:897-906` hashes the canonical JSON of the wrapper object `{"subject":{"changed_paths":[sorted…],"tree_digest":"…"}}` (`canonical_digest:76-77`: `sort_keys`, `(",",":")` separators, `ensure_ascii=False`, `"sha256:"` prefix). That value is emitted nowhere: `_make_decision:398-408` produces exactly `DECISION_REQUIRED_KEYS:39-50`, which contains no `progress_identity`, and no public function exposes it. `STATE_MACHINE.md:48-49` nevertheless tells the integrator that "`ledger.prior_attempts` records prior decision **outputs** with this explicit `progress_identity`", and `:46-47` defines it only as "the SHA-256 digest of the current execution subject's `tree_digest` plus sorted `changed_paths`" — a prose description that does not determine the preimage (no wrapper object, no canonical serialization, no prefix rule).

*Failure scenario:* a ledger writer implements the documented contract literally — `sha256(tree_digest + "".join(sorted(changed_paths)))` — and records it. The value is a well-formed digest, so `_validate_ledger:658-660` accepts it, but it never equals `_progress_identity(...)`. `:927` therefore takes the else-branch on every round, `next_streak` is pinned to 0, `NO_PROGRESS` at `:1198`/`:1218`/`:1236` stays unreachable, and a run repeating the identical failing tree burns the whole rework budget and escalates as `REWORK_BUDGET_EXHAUSTED`. That is FF-02's consequence 2 unchanged in effect — the counter moved from "never written" to "written from an unpublished formula".

*Minimal reproduction:*
```python
import copy, hashlib
from tests.test_orchestrator_policy import base_bundle, decide

b = base_bundle()
b["task_policy"]["budgets"]["no_progress"] = 1
b["execution_report"]["gate_results"]["unit_tests"] = "FAIL"
d1 = decide(b)

s = b["execution_report"]["subject"]                       # integrator follows STATE_MACHINE.md:46-47
identity = "sha256:" + hashlib.sha256((s["tree_digest"] + "".join(sorted(s["changed_paths"]))).encode()).hexdigest()

b2 = copy.deepcopy(b)
b2["ledger"]["counters"] = d1["budgets_after"]
b2["ledger"]["prior_attempts"] = [{"attempt_epoch": 1, "progress_identity": identity,
                                   "decision_digest": d1["decision_digest"],
                                   "outcome": d1["outcome"], "rule_id": d1["rule_id"]}]
b2["ledger"]["last_epoch"] = 1
b2["ledger"]["seen_nonces"] = ["nonce-old", "nonce-new"]
b2["execution_report"]["attempt_epoch"] = 2
b2["execution_report"]["nonce"] = "nonce-repeat"
b2["reviewer_report"]["attempt_epoch"] = 2
d2 = decide(b2)
assert d2["budgets_after"]["no_progress_streak"] == 0      # never advances
assert d2["rule_id"] == "R09_GATE_FAIL"                    # NO_PROGRESS never fires
```
Swapping `identity` for `policy._progress_identity(b["execution_report"])` flips both assertions — that is the whole gap.

*Evidence:* the only reproduction of the exact identity in the tree is the private helper, and the suite itself must reach through the private name to build a ledger (`tests/test_orchestrator_policy.py:160`). Grep confirms `progress_identity` appears only at `:648`, `:658`, `:897`, `:927` — never in a decision payload.

---

**R3-02 — major — `implementation/tests/test_orchestrator_policy.py:148-154` and `:665-679`**

*Violated criterion:* R3 packet regression requirement "**Exact** deep-nesting reproductions under `ledger.prior_attempts` and `execution_report.payload`, both through `decide()`"; targeted-review check 5 (regression tests must be meaningful).

`deeply_nested_dict(depth=128)` (`:148-154`) nests 128 levels; the reported defect needs nesting past the interpreter recursion limit (the FF-01 repro used 3000). At 128 nothing in the pre-fix path raises: `_normalized_for_digest:145-154` costs ≈1 frame per level, `copy.deepcopy:285` ≈2, and the C JSON encoder's recursion budget is ≥1000. Worse, both injected shapes independently fail ordinary field validation and produce the asserted result on their own — `("execution_report","payload")` leaves `payload` unpaired and trips `_validate_execution_report:743-744`; `("ledger","prior_attempts") = [{"n": …}]` trips `_validate_ledger:648-664` on unknown field, epoch, digests, outcome and rule id. The assertion at `:678` is therefore satisfied by `R01_BINDING` from schema validation, not by any depth guard.

*Failure scenario:* the FF-01 fix is unprotected. Delete `_enforce_decide_input_limits` (`:1296`) and move `input_digests = _input_digests(...)` back outside the `try` — i.e. restore the exact pre-R3 arrangement the review flagged — and both subtests still pass green, while `decide()` again raises `RecursionError` on the review's 3000-level input. A future refactor reintroduces the defect with a green suite.

*Minimal reproduction:*
```sh
# 1. comment out line 1296 and hoist line 1297 above the `try:` at 1295
python3 -m unittest tests.test_orchestrator_policy.OrchestratorPolicyTests.test_deep_prior_attempts_and_payload_fail_closed_through_decide
# OK — the reverted defect is invisible
# 2. the shape that actually discriminates (schema-valid, depth beyond the limit):
python3 - <<'PY'
import orchestrator_policy as policy
from tests.test_orchestrator_policy import base_bundle
b = base_bundle(); deep = {}; node = deep
for _ in range(3000): node["n"] = {}; node = node["n"]
b["ledger"]["prior_attempts"] = [deep]
print(policy.decide(b["task_policy"], b["ledger"], b["execution_report"], b["reviewer_report"])["rule_id"])
PY
```

*Secondary, same test:* the "resets on changed identity" half (`:656-663`) starts from `repeated`, whose counters carry `no_progress_streak == 0`, so `assertEqual(..., 0)` at `:663` holds even if the reset branch at `:927` returned `current_streak` instead of `0`. The reset is not actually covered; a reset case must start from a streak ≥ 1 with `no_progress` ≥ 2.

*Evidence:* `EVIDENCE.md:294-303` records these four tests passing, which is consistent — they pass under both the fixed and the unfixed arrangement.

---

# Below the reporting floor (no action required, listed for completeness)

- `decide()` now enforces depth/cardinality/string limits on already-parsed inputs, but `STATE_MACHINE.md:76-77` still attributes those caps to the CLI parser only.
- `budgets: {"no_progress": 0}` trips `NO_PROGRESS` on the first rework branch via the `current_streak >= limit` early return (`:923-924`) even with no prior attempt; degenerate config, fail-closed direction. The documented boundary semantics ("budget N ⇒ escalate on the Nth repeat") are also not stated numerically.
- `STATE_MACHINE.md:26-36` omits the reviewer-contract step (`R08`, `:1302-1304`) which sits between documented items 1 and 2.

# Scope and authority

I read only the files named in the read scope and edited nothing. I executed nothing (Bash denied), so I claim no test-run, schema-check or fixture-check evidence for this round; the outputs in `EVIDENCE.md:294-541` — including the `accepted_with_payload.json` digest correctness, which I cannot compute statically — are unverified by me. This is advisory observation data: I cannot accept, close, downgrade or waive anything. FF-03 and FF-04 are closed; FF-01 is behaviorally closed but its regression does not lock the fix; FF-02's closure is incomplete. Two `major` findings open, no `blocker`.

**TARGETED_REWORK**
