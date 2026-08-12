Bash execution is denied in this session (as in the R1 and R2 rounds), so I ran no commands. Every finding below is a line-exact static control-flow proof against the in-scope files, with a runnable repro written so the coordinator can execute it directly.

# Final-full review: deterministic state machine slice

## Verified as satisfied (no finding)

I re-derived the acceptance path end-to-end and could not reach `ACCEPTED` through any malformed, stale, replayed, mismatched, or hostile input. Specifically confirmed in the current tree: SM-01…SM-06 remain fixed; the SM-07 residue is closed by the unconditional history normalization at `orchestrator_policy.py:895-897`; every path in `UNORDERED_DIGEST_LIST_PATHS:80-93` has an order-insensitive decision traversal (`762-765`, `801-807` ordered by design, `877/896`, `898`, `903-910`, `919-936`, `947`, `993`, `1001`); reviewer data cannot accept, downgrade (`858-859`), close by prose or absence (`882-893`), or classify infrastructure (`761-766` reads only `execution_report.failure_signatures` against `task_policy.infra_signature_allowlist`, with `_validate_reviewer_report:663-690` blocking authority keys and unknown fields); targeted closure alone cannot accept (`939-941` requires `review_mode == "final_full"`); infra total/per-signature budgets are independent (`769-776`) and separate from rework (`787-788`) and full-review (`796-797`); the merged registry round-trips its own validator (`849-897` vs `410-498`).

---

# Findings

**FF-01 — major — `implementation/orchestrator_policy.py:1143` (with `:139-148`, `:269-273`, `:1146`)**

*Violated criterion:* task packet "Malformed, incomplete, stale, mismatched, or replayed trusted inputs fail closed to `ESCALATED` or a typed tool-input error"; `CODEX_STATE_MACHINE_REWORK_1.md:46-47` ("public `decide()` is total for representative malformed dict/list/scalar containers and never throws outside process-fatal exceptions").

`decide()` computes `input_digests = _input_digests(...)` at `:1143`, which is **outside** the `try` that begins at `:1146`. `_input_digests` recurses without any depth bound: `_normalized_for_digest:139-148` recurses once per nesting level, and `_ledger_for_digest:270` calls `copy.deepcopy` (≈4 frames per level). `MAX_DEPTH` is enforced only inside `parse_json_file`/`_walk_limits:177-181` and inside the exception-fallback shaper `_json_safe_shape:105`. `_safe_canonical_digest:132-136` catches only `TypeError`/`ValueError`, and in any case the `RecursionError` is raised while evaluating the argument, before that helper is entered.

*Failure scenario:* any embedder that calls the documented adjudication entry point (`STATE_MACHINE.md:3-6`: "`decide(...)` is the only adjudication entry point") with already-parsed JSON — an IPC/queue front end, a future coordinator, or the test suite itself — hands `decide()` a structurally hostile document with ~250+ levels of nesting under `ledger.prior_attempts` (validated only as `isinstance(list)` at `:557`, and only *after* the crash point) or under `execution_report.payload`. The engine raises `RecursionError` and returns no decision at all, instead of a machine `ESCALATED`/`R01_BINDING` record.

*Minimal reproduction:*
```python
import orchestrator_policy as policy
from tests.test_orchestrator_policy import base_bundle

b = base_bundle()
deep = {}
node = deep
for _ in range(3000):
    node["n"] = {}
    node = node["n"]
b["ledger"]["prior_attempts"] = [deep]          # or: b["execution_report"]["payload"] = deep
policy.decide(b["task_policy"], b["ledger"], b["execution_report"], b["reviewer_report"])
# RecursionError propagates out of decide(); expected ESCALATED / R01_BINDING
```

*Why current tests do not prevent it:* `test_public_decide_is_total_for_representative_malformed_containers` (`tests/test_orchestrator_policy.py:690-701`) and `test_sm06_malformed_nested_scalar_containers_do_not_throw` (`:514-529`) exercise only one-level malformed containers (`[]`, `"bad"`, `[{"gate": …}]`, `{"SIG_RUNNER_OOM": []}`). No test passes a deeply nested value, and no test asserts that `decide()` is total for depth. The two prior rounds noted this as a below-floor observation on the grounds that the CLI caps depth; the CLI is not the contract boundary the R1 regression requirement was written against, and the defect is reproducible in the current tree.

---

**FF-02 — major — `implementation/orchestrator_policy.py:290-298`, `:791-793`, `:557-558`**

*Violated criterion:* deterministic requirement "Rework iterations have a bounded budget; exhaustion escalates" as implemented via the `no_progress` budget; AC-SM02 (`budgets_after` = budgets after the transition); AC-SM06.

`no_progress_streak` is **read** at `_budget_state:297` and `_no_progress_trip:793` and is **never written anywhere in the module**. Grep over `orchestrator_policy.py` for `no_progress` yields only reads (`:297`, `:399`, `:401`, `:548`, `:550`, `:792-793`, `:1040`, `:1051`, `:1059`, `:1070`, `:1076`, `:1087`) — no assignment or increment, unlike `rework_used` (`:1041`, `:1060`, `:1077`), `infra_total_used`/`infra_used_by_signature` (`:780-784`), and `final_full_used` (`:1100`). `ledger.prior_attempts`, the only input that could support a progress predicate, is validated at `:557-558` and then never read by any function.

Consequences, both statically provable:
1. `budgets_after["no_progress_streak"]` is echoed unchanged on every `REWORK`, so it is not a post-transition counter, contradicting `STATE_MACHINE.md:42-44` and AC-SM02.
2. The `no_progress` budget — declared `required` in both `orchestrator-state-machine.schema.json:144-150` (task policy) and `:244-250` (counters) — is inert in any loop driven by this engine: an orchestrator that applies `budgets_after` verbatim (the only propagation mechanism the slice defines, and the one that carries `rework_used`) will hold the streak at its initial value forever, so `_no_progress_trip` can never become true and the `NO_PROGRESS` reason code at `:1051`/`:1070`/`:1087` is unreachable.

*Failure scenario:* a task policy sets `budgets: {"rework": 8, "no_progress": 2, …}`, intending escalation after two unproductive attempts. The implementer resubmits the identical failing tree three times. Each call returns `REWORK`/`R09_GATE_FAIL` with `budgets_after["no_progress_streak"] == 0`; the run consumes all 8 rework units and finally escalates as `REWORK_BUDGET_EXHAUSTED` instead of `NO_PROGRESS` after 2. The configured no-progress bound is never enforced.

*Minimal reproduction:*
```python
b = base_bundle()
b["task_policy"]["budgets"]["no_progress"] = 1
b["execution_report"]["gate_results"]["unit_tests"] = "FAIL"
d1 = decide(b)
assert d1["budgets_after"]["no_progress_streak"] == 0        # never advanced

b["ledger"]["counters"] = d1["budgets_after"]                 # apply budgets_after, as documented
b["ledger"]["seen_nonces"] = ["nonce-old"]; b["execution_report"]["nonce"] = "nonce-2"
b["ledger"]["current_epoch"] = 2; b["ledger"]["last_epoch"] = 1
b["execution_report"]["attempt_epoch"] = 2; b["reviewer_report"]["attempt_epoch"] = 2
d2 = decide(b)
assert d2["rule_id"] == "R09_GATE_FAIL"                       # still REWORK, never NO_PROGRESS
```
*Static proof if you prefer not to run it:* there is no assignment statement whose target is `no_progress_streak` anywhere in `orchestrator_policy.py`.

*Why current tests do not prevent it:* `test_no_progress_escalates_gate_failure` (`:296-302`) and `test_evidence_no_progress_escalates_instead_of_rework` (`:606-612`) both hand-write `ledger["counters"]["no_progress_streak"] = 2` into the input and then assert the consumption branch. They mirror the implementation's read side and never assert the produced `budgets_after["no_progress_streak"]`, so the absent increment is invisible to the suite. No test drives two successive decisions through `budgets_after`.

---

**FF-03 — major — `implementation/orchestrator-state-machine.schema.json:293-309` (with `:295`) vs `implementation/orchestrator_policy.py:569-584`, `:637-640`, `:1006-1009`**

*Violated criterion:* AC-SM01/AC-SM12 and the review requirement that schema, implementation, fixtures and tests agree; the packet's digest-bound-input requirement (precedence item 5, `STATE_MACHINE.md:32`).

`$defs/execution_report` sets `"additionalProperties": false` (`:295`) and lists neither `payload` nor `payload_digest` in `required` (`:296-309`) or `properties` (`:310-399`). The Python contract does the opposite: `_validate_execution_report`'s `allowed` set includes `"payload"` and `"payload_digest"` (`:582-583`), `:637-640` enforces their pairing and type, and rule `R04_INCOMPLETE` (`:1006-1009`) is defined entirely in terms of them. So the two artifacts define different input languages for the same document: a document that `_validate_execution_report` accepts is rejected outright by the shipped schema.

*Failure scenario:* an operator runs the documented CLI (`STATE_MACHINE.md:66-68`, `README`-style usage) on a real execution report that carries the digest-bound `payload` the implementation supports. `evaluate_fixture:1196-1204` calls `_validate_against_state_schema` first, which returns `["Additional properties are not allowed ('payload', 'payload_digest' were unexpected)"]`, so the tool prints `{"valid": false, "schema_errors": […]}` and exits `1` — reporting a *fixture* error rather than the policy decision. The entire payload-binding mechanism, including the `R04_INCOMPLETE` rule that closed blocker SM-01, is unreachable through the only shipped entry point that consumes bytes, and no fixture in `fixtures/policy/` can ever exercise it.

*Minimal reproduction:* add `"payload": {"ok": true}` and its `payload_digest` to `fixtures/policy/valid/accepted.json`, then
```sh
python3 orchestrator_policy.py --fixture fixtures/policy/valid/accepted.json
```
Exit `1` with `additionalProperties` errors, although `decide()` on the same four documents returns `ACCEPTED`/`R17_ACCEPT`.

*Why current tests do not prevent it:* every payload test bypasses the schema. `test_payload_digest_mismatch_escalates_as_incomplete` (`:218-223`), `test_sm01_terminal_replay_does_not_bypass_payload_digest_validation` (`:442-453`) and `test_opaque_payload_nested_control_key_names_are_not_digest_sorted` (`:679-688`) call `decide()` / `policy._input_digests` directly. The only schema-path coverage is `check_fixture_tree:1219-1238`, and neither `fixtures/policy/valid/accepted.json` nor `known_infra.json` carries a payload, so the divergence is never observed. `test_state_schema_rejects_unknown_fields` (`:155-159`) only probes the fixture root.

---

**FF-04 — major — `implementation/STATE_MACHINE.md:26-40` (specifically `:28`) vs `implementation/orchestrator_policy.py:1146-1167`**

*Violated criterion:* review requirement that documentation agrees with the implementation, on the exact ordering property that produced blocker SM-01 and major SM-04.

`STATE_MACHINE.md:26` asserts "The implementation follows the packet order:" and then lists "1. terminal idempotent replay" ahead of "2. malformed or binding-invalid input" and "3./4./5." replay/stale/incomplete. The implementation deliberately does the opposite, as required by `CODEX_STATE_MACHINE_REWORK_1.md:17-18` and `:23-26`: `decide()` runs `_validate_task_policy`/`_validate_ledger`/`_validate_execution_report` (`:1147`), `_validate_reviewer_report` (`:1150`), `_binding_errors` (`:1154`), then the full `_decide_policy` derivation including R02/R03/R04 and every rework/accept rule (`:1158`), and only then inspects `ledger["terminal_decision"]` (`:1161`). Moreover the terminal branch is not a short-circuit at all: `:1165` requires `terminal == derived`, so it can only ever return a value the engine has already re-derived, and any mismatch returns `ESCALATED`/`R01_BINDING`/`TERMINAL_DECISION_INVALID` (`:1131-1132`).

*Failure scenario:* an integrator building the ledger writer around this engine reads the precedence table and implements the documented contract — record `terminal_decision` and expect subsequent submissions to short-circuit to the stored outcome before validation. In the shipped engine, once `terminal_decision` is set, every submission whose inputs differ (a new attempt, a re-serialized ledger, any changed field) fails `_validate_terminal_decision:970-971` on `input_digests` and returns `ESCALATED`/`R01_BINDING` with reason `TERMINAL_DECISION_INVALID` — a reason code that blames the recorded decision rather than the new input. The integrator's replay/idempotence design is built on a documented precedence the code does not implement, on the one ordering whose earlier violation was rated blocker.

*Static proof:* `STATE_MACHINE.md:28` = "1. terminal idempotent replay;" versus the first executable guard in `decide()` at `orchestrator_policy.py:1147-1149` (`schema_errors` → `R01_BINDING`) and the terminal read at `:1161`, which is the last statement before the `return`. No conditional path reaches `:1161` before `:1147`.

*Why current tests do not prevent it:* no test asserts the documented precedence, and `test_idempotent_terminal_replay_returns_recorded_decision` (`:172-177`) passes identically under either ordering because it supplies fully valid inputs whose derived decision equals the stored record — the one input class that cannot distinguish "replay first" from "replay last". The documentation is not covered by any check in `EVIDENCE.md`.

---

# Scope and authority

I inspected only the files named in the read scope. I executed nothing (Bash denied), so I claim no test-execution, schema-check, or fixture-check evidence for this round; the counts and outputs in `EVIDENCE.md:31-93` are unverified by me. This report is advisory observation data: I cannot accept, downgrade, suppress, or close anything, and I make no claim of authority over the policy state. Four `major` findings remain open; no `blocker` found.

FINAL_FULL_REWORK
