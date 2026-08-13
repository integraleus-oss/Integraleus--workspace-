I traced the current working-tree slice against the prior findings and the accepted core (`orchestrator_policy.py`, `validate_review_verdict.py`, `review-verdict.schema.json`).

## Verification method

Static tracing only. `python3` / test execution was **denied again** (don't-ask mode), so nothing below is empirically confirmed — the "58 integration / 84 core tests green" criterion remains unverified.

## S1 — closed

`trusted_review_builder.py:216` now reads `"targeted" if review_mode == "targeted_verification" else "full"`, driven by the same `review_mode` computed at `:207`. That reconciles the two constraints that previously contradicted:

- schema `allOf` branch (`review-verdict.schema.json:489-528`): `review_mode == targeted_verification` → `coverage_scope` const `"targeted"`; the `initial_full` branch (`:458-486`) and the `final_full` branch keep `"full"`.
- validator semantic binding (`validate_review_verdict.py:422-426`): `document.coverage_scope == manifest.expected_coverage_scope`.

Both are now satisfiable by the same verdict. The rest of the targeted path is coherent: the schema's `targeted_verification` branch also requires `verification` plus `review.inputs_digest.prior_findings_digest`, and the builder emits `prior-findings.json` (`:281-291`), seals it (`:300-301`), and wires it through `bundle.json` → `local_orchestrator_runner.py:59-60,75-78` → `build_projection(..., prior)`. `review_projection.py:116-123` consumes `verification.results` only in targeted mode, so `verified_finding_ids` flows to `merge_finding_registry`. No fail-closed weakening — the manifest is still the authority and any reviewer deviation still fails semantic binding.

## S2 — closed

The `R15_NEED_FULL_REVIEW` branch (`managed_one_cycle.py:62-74`) now precedes the `attempt < max_attempts` rework branch (`:75`), so an `R15` at **attempt 1** goes straight to the review-only leg and `implement` is never called a second time. Traced end-to-end for the previously-broken case:

1. Attempt 1, `initial_full`, clean → `_final_full_ok` false (mode) → `_full_review_available` true → `R15`, `final_full_used → 1` (`orchestrator_policy.py:1311-1323`).
2. `review(max_attempts + 1)` → builder attempt 3 → `final_full` / `full`; carried ledger has `current_epoch 3`, `last_epoch 2`, `seen_nonces ["…attempt-1-nonce"]`, `final_full_used 1`.
3. `R02_REPLAY` (`3 > last_epoch 2`, unseen nonce) and `R03_STALE` (`3 >= current_epoch`, tree digests equal) both pass; gates PASS; no open blocker/major; `_final_full_ok` true → `R17_ACCEPT`.

A correct first attempt is now acceptable with exactly one Codex launch. Fail-closed is intact on the new leg: unknown/absent `rule_id`, `outcome`/`rule_id` mismatch, and **any** `REWORK` on the final leg are all forced to `ESCALATED` (`:68-70`), and a non-dict verdict falls into the blanket handler → `ESCALATED`.

## S3 — closed

`production_cycle_cli.py:216-217` now enforces both legs of the registry binding before the value is carried:

- `manifest["registry_digest_file"] == _sha256(registry-after.json)` — and `manifest` is `result["decision"]`, which `admit_live_review` has already proven byte-equal to the durable `run-result.json` (`managed_policy_review.py:42-44`).
- `decision["registry_digest_after"] == _canonical_digest(registry)` — and `decision.json` is itself digest-bound via `manifest["decision_digest_file"]` (`managed_policy_review.py:45-46`).

The canonicalization matches exactly (`json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)` vs `orchestrator_policy.py:73-78`); the `ensure_ascii` difference in the runner's on-disk writer is irrelevant because the CLI re-canonicalizes the parsed value. I also checked the two `merge_finding_registry` call sites cannot diverge: `decide` passes the same un-copied `ledger`/`execution_report`/`projection` objects into `_decide_policy` (`:1389`), which calls `merge_finding_registry(ledger["finding_registry"], reviewer_report, exec_subject["tree_digest"])` — identical arguments to `local_orchestrator_runner.py:84-87`. So this check will not spuriously fire. Mismatch or unreadable file raises `PacketError` → `ESCALATED`. Ordering is correct: admission runs first (`:210`), the digest check second.

## New blocker/major introduced

**None found.**

One new **minor** side effect of the S2 fix, worth recording but not blocking:

- **Epoch-label fidelity on the skip path.** When attempt 1 yields `R15`, the review-only leg is built with `attempt=3`, so `trusted_review_builder.py:259` records the attempt-**1** decision as `{"attempt_epoch": 2, …}` — an epoch that never occurred. `_validate_ledger:656-681` only checks non-negativity and uniqueness, so it passes. The single consumer, `_latest_prior_attempt` (`:947-950`), is reached only via `_no_progress_transition` on the gate-fail / open-findings / evidence branches, which the accept path never touches. Where it *is* reachable (final leg reports a blocker), the effect is to increment `no_progress_streak` — strictly more conservative, and that leg is forced to `ESCALATED` by `managed_one_cycle.py:69-70` regardless. No fail-closed weakening. It does extend carried nit **St1**: `production_cycle_cli.py:221` uses the same `attempt - 1` formula, so the two implementations must stay in lockstep across a non-contiguous attempt sequence.

## Carried nits (unchanged, non-blocking)

- **St1** duplicated `prior_attempts` carry (`trusted_review_builder.py:257-259` / `production_cycle_cli.py:219-221`) — now with the added skip-path caveat above.
- **St2** `merge_finding_registry` still recomputed at `local_orchestrator_runner.py:84-87` after `decide` and before the invariant check, so a malformed fixture that `decide` would return as a clean `R01_BINDING` instead raises `KeyError` → `local_orchestrator_run_error`. Fail-closed, unnamed.
- **St3** builder mode still fabricates `[{prompt_text}] * 3` (`:149`) for `packet["reviews"][attempt - 1]`. In *legacy* mode an `R15` now also reaches index 2 → bare `IndexError` → `ESCALATED`; fail-closed but unnamed.
- **St4** carried-context type errors still surface as `AttributeError`/`TypeError` rather than `BuilderError`.
- **St5** `capture_clean_baseline` outside the cycle try (`:163`), basename-only gate allowlist, full-`os.environ` gate env, advisory `0o444` seal, and the open `EVIDENCE.md` / `TASK_PACKET.md` items 8-10.

## Residual verification gap (carried, previously reported as finding #5)

Test coverage still does not reach the two places these fixes live:

- `test_trusted_review_builder.py:181-186` asserts `expected_coverage_scope == "targeted"` on the manifest, but no test drives an attempt-2 targeted verdict through `validate_document` → `build_projection` → `decide` — exactly where S1 hid.
- `test_production_cycle_cli.py:216-217` still mocks `admit_live_review` to return `ACCEPTED`/`R17` on attempt 1, so `production_cycle_cli.py:211-232` — including the entire new S3 digest check — never executes under test.
- `test_managed_one_cycle.py:68-79` does genuinely prove the S2 fix (`implemented == [1]`, status `ACCEPTED`) with stub verdicts.

Combined with the denied test run, S1 and S3 are closed by tracing only. I'd treat "drive one targeted attempt-2 verdict through the real validator, and one builder-mode rework carry through the real registry check" as the highest-value next evidence, but neither gap is a defect in the shipped code and both were reported before.

TRUSTED_BUILDER_REWORK_R2_PASS
