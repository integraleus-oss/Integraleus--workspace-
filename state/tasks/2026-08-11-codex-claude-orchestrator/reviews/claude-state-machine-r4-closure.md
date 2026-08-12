I read every file in scope. Bash is denied in this session, so — as in R1–R3 — I executed nothing; every claim below is a line-exact static derivation.

# Targeted closure review R4 — state machine

## Check 1 — exact progress identity is public and machine-usable ✅

- **Public function.** `orchestrator_policy.py:914-925` `progress_identity(execution_report)` is now a non-underscored module function. It builds `{"subject":{"tree_digest":…,"changed_paths":sorted(...)}}` and returns `canonical_digest(...)` (`:77-78` → `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")`, prefixed `sha256:`).
- **Emitted in every decision.** `_make_decision:398,407` writes the field; `DECISION_REQUIRED_KEYS:39-51` includes it. Every return site passes a value: `_decide_policy:1179` computes `current_progress_identity` once and threads it through `:1181, 1191, 1194, 1196, 1209, 1218, 1222, 1240, 1251, 1270, 1281, 1298, 1309, 1323, 1333, 1344`; `decide()` uses `_safe_progress_identity:1366` for the pre-derivation escalations (`:1374, 1377, 1386, 1395, 1397, 1402, 1404`). Positional argument order matches both signatures (`_make_decision:390-399`, `_escalated:415-421`).
- **Schema-valid.** `orchestrator-state-machine.schema.json:553-619` `$defs/decision` lists exactly the same 11 keys with `additionalProperties: false`, and `:594-603` types `progress_identity` as `anyOf[sha256, null]` — matching `_safe_progress_identity`'s `str | None`. `$defs/sha256:44-47` (`^sha256:[0-9a-f]{64}$`) is what `canonical_digest` emits. `:275-305` requires `progress_identity: $defs/sha256` in `ledger.prior_attempts[*]`, agreeing with `_validate_ledger:665,675-677`. No fixture regresses: all five fixtures carry `prior_attempts: []` / `terminal_decision: null`.
- **Terminal-validated.** `_validate_terminal_decision:1137` requires the key set to equal `DECISION_REQUIRED_KEYS`, `:1151-1153` rejects a non-sha256 non-null value, and `decide():1396` requires full equality with the freshly derived decision — so a forged identity cannot be replayed.
- **Reproducible from documented bytes.** `STATE_MACHINE.md:46-62` now specifies the preimage object, the exact `tree_digest` source, the sort rule (ascending as strings, no dedup/normalization), the serialization (lexicographic key sort, `,`/`:`, non-ASCII as UTF-8), and the `sha256:` + 64-lowercase-hex format. `sort_keys=True` normalizes the literal's key order, so the documented `{"subject":{"changed_paths":…,"tree_digest":…}}` bytes are exactly what `_canonical_bytes` produces. `test_orchestrator_policy.py:179-188` reimplements that recipe independently from `hashlib`/`json.dumps` — not by calling the helper — and `:230` asserts equality with the emitted field; `:232-236` asserts permutation invariance. This is the R3-01 gap closed: an integrator can now derive the value from public output or the documented contract, without reaching for a private name.
- **Identical to the policy's value.** `_no_progress_transition:963` calls the same `progress_identity()`; `:964` compares it against `prior_attempt["progress_identity"]`. For any decision reaching `_decide_policy`, `_validate_execution_report:721-730` has already guaranteed the exact preconditions `_safe_progress_identity:932-940` checks, so the emitted value and the compared value cannot diverge.

**R3-01 — closed.**

## Check 2 — advance to boundary, reset of a nonzero streak ✅

`test_no_progress_advances_from_prior_decision_outputs_and_resets_on_changed_identity:680-733` builds each ledger from the *emitted* decision (`prior_attempt_from:191-198` copies `decision["progress_identity"]`), which is itself the contract under test. With `no_progress=2`, `rework=4`:

| stage | prior identity | `current_streak` | derived (`_no_progress_transition:953-965`) | asserted |
|---|---|---|---|---|
| `first` (`:685-688`) | none | 0 | `next=0`, not tripped | REWORK, streak 0 |
| `repeated` (`:690-700`) | same | 0 | `next=1`, `1>=2` false | REWORK, streak 1 |
| `changed` (`:702-717`) | different (`tree_digest` → `digest("f")`) | **1** | `next=0` | REWORK, streak **0** |
| `exhausted` (`:719-733`) | same | 1 | `next=2`, `2>=2` true | ESCALATED `R10`, streak 2, `NO_PROGRESS` |

The reset case now starts from a genuinely nonzero streak, so `:716` fails if `:964`'s else-branch returned `current_streak` instead of `0` — the R3-02 secondary gap. The boundary is reached mechanically at the configured limit. Replay/staleness preconditions are satisfied in each stage (`last_epoch`, `seen_nonces`, `current_epoch`, `expected_subject` all advanced), so `R02`/`R03` do not pre-empt the branch, and `decide()` does not mutate the shared `budgets_after` objects reused as ledger counters (`_budget_state:373-381` rebuilds; `:1389` deep-copies before mutation), so the staged assertions are sound.

**R3-02 primary/secondary (reset) — closed.**

## Check 3 — the two 3000-level regressions genuinely lock the recursion fix ✅

`test_deep_prior_attempts_and_payload_fail_closed_through_decide:735-761` uses `deeply_nested_dict(3000)` (`:149-155`, iterative) under `ledger.prior_attempts[0].progress_identity` and under paired `execution_report.payload`/`payload_digest`.

The discriminator is `:761`, `result["input_digests"][digest_key] == rejected_digest(rejected_value)`. `_rejected_input_digests` is reachable **only** from `except PolicyInputError` (`:1400-1402`); every schema-rejection return (`:1374`, `:1377`, `:1386`) carries `_input_digests(...)` instead, and the generic `except Exception` (`:1403-1404`) carries `_placeholder_input_digests()`. So ordinary field validation — `bad_prior_attempt_digest` (`:675-677`) for case 1, or the payload-pairing checks for case 2 — cannot satisfy `:761`.

Removing the fix fails the test in both flavors the R4 packet named:

- Delete `_enforce_decide_input_limits` at `:1369`: `_input_digests:1370` → `_normalized_for_digest:146-155` recurses ≥1 frame per level and raises `RecursionError` well before 3000, which is not a `PolicyInputError` → `except Exception` → placeholder digests ≠ `rejected_digest(...)` → `:761` fails. (Even had it reached `_safe_canonical_digest:139-143`, that fallback digests `{"invalid_json_shape": …}`, still ≠ `{"rejected_input": …}`.)
- Hoist `input_digests = _input_digests(...)` above the `try` at `:1368`: `RecursionError` escapes `decide()` entirely and the test errors.

With the fix, `_walk_limits:184-188` raises `too_deep` at depth 33 (self-bounded, ~33 frames), so both cases return a machine decision `("ESCALATED","R01_BINDING")` with a `decision_digest` and rejected-input digests. The test's local `json_safe_shape:158-172` is a faithful reproduction of `_json_safe_shape:105-129` for these inputs (same `depth > MAX_DEPTH` cutoff, same canonical sort key; the omitted `MAX_MAPPING_KEYS`/`MAX_LIST_ITEMS`/float/tuple branches are not triggered), so the equality is meaningful rather than vacuous. Case 2 is additionally structurally valid — `payload` is `true`-typed in the schema (`:433`) and correctly paired — so only the depth guard explains its outcome.

## Check 4 — no blocker/major regression introduced ✅

I found nothing at blocker or major severity. Specifically checked:

- **Name shadowing.** `progress_identity` is shadowed as a parameter in `_make_decision:398`, `_escalated:420`, and `_invalid_terminal_decision:1351`; each body only reads it as a value and never calls the module function, so no call resolves to a string.
- **New pre-guard work.** `_safe_progress_identity:1366` now runs before `_enforce_decide_input_limits`. It touches only two subject fields, is depth-free, and is wrapped in `try/except Exception` (`:929-943`), so it cannot make `decide()` raise or amplify cost; the CLI still applies `_walk_limits` in `parse_json_file:245` before `decide()` is reached.
- **Prior closures preserved.** FF-03 (schema/validator payload agreement: `:321-328, 433-436` vs `_validate_execution_report:705-706, 760-763`) and FF-04 (documented precedence and its lock at `test_documented_precedence_matches_safe_source_order:788-797`) are intact.
- **Totality.** `test_public_decide_is_total_for_representative_malformed_containers:875-886` still covers non-dict inputs, which `_safe_progress_identity:930-931` handles by returning `None` (schema-permitted).
- Contract tightening is fail-closed only: a terminal decision recorded before this change lacks `progress_identity` and is now rejected as `TERMINAL_DECISION_INVALID` (`:1137`), which is the mandated direction.

# Below the reporting floor (no action required)

- No test validates an emitted decision against `$defs/decision` directly; the key-set/type agreement I verified is static, and no fixture carries a `terminal_decision`, so a future schema/output drift would be caught only by inspection.
- `_no_progress_transition:960-961` still short-circuits to `tripped` when `current_streak >= limit`, so a changed identity cannot reset a streak already at the boundary. Only reachable in a ledger written after an escalation; fail-closed. Carried over from R3, unchanged.
- `budgets: {"no_progress": 0}` trips `NO_PROGRESS` on the first rework branch with no prior attempt. Degenerate config, fail-closed. Carried over from R3.
- `STATE_MACHINE.md:92-93` still attributes the depth/cardinality caps to the CLI parser only, though `decide()` now enforces them on already-parsed inputs. Carried over from R3.
- `STATE_MACHINE.md:26-36` still omits the reviewer-contract step (`R08`, `:1375-1377`) between documented items 1 and 2. Carried over from R3.

# Scope and authority

I read only the files named in the read scope (plus `fixtures/policy/**` and `orchestrator-state-machine.schema.json` regions needed to check for fixture/schema breakage) and edited nothing. I executed nothing, so I claim no test-run, schema-check, fixture-check, `py_compile`, or `git status` evidence for this round; the outputs in `EVIDENCE.md:1242-1345` and `:1453-1515` (84 tests OK, both schema self-checks, fixture check, and the `?? implementation/` scoped status) are recorded but unverified by me. This is advisory observation data: I cannot accept, close, downgrade, or waive anything. Both in-scope findings are closed by line-exact derivation; no blocker or major findings remain open.

**TARGETED_PASS**
