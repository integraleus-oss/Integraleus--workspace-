## Verification method

Bash execution was denied again (`don't ask mode`), so the suites were **not run** — the "58 integration / 84 core tests green" criterion remains unverified. Everything below is static tracing of the current files against the accepted core (`orchestrator_policy.py`, `validate_review_verdict.py`, `review-verdict.schema.json`, `review_projection.py`, `local_orchestrator_runner.py`).

## Confirmed closed

| Claim | Result |
|---|---|
| Post-gate HEAD recheck | **Closed** — `trusted_review_builder.py:181` now re-checks `_head(root)` alongside paths/tree/ignored state. |
| Prompt requests exact JSON | **Closed** — `production_cycle_cli.py:190-192` asks for "the exact review-verdict JSON as your final response"; no path is named, and the builder-leg base prompt is the manifest-bound `review-instructions.md` (`:139`). |
| Builder bundle reaches real projection + policy → `R17_ACCEPT` | **Closed** — `tests/test_trusted_review_builder.py:133-162` builds an attempt-2 bundle over a real repo, runs `VALIDATOR.validate_document` against the builder manifest, then `local_orchestrator_runner.run` → real `build_projection` + `POLICY.decide`, asserting `("ACCEPTED", "R17_ACCEPT")`. I traced the path end-to-end: identities bind (`_binding_errors:870-881`), `attempt_epoch 2 > last_epoch 1`, nonce unseen, gates `PASS`, nit-only finding is below `BLOCKING_RANK`, evidence `bytes>0`/digest matches (`_evidence_failures:1096-1119`), and `_final_full_ok:1122-1130` holds. Unexecuted, but the assertion is now the decisive one. |
| Generated identifiers vs reviewer schema | **Closed except one edge** (Major 3 below) — `run_id` is now `run_…`, `gate_run_id_pre="run_builder-baseline"`, `AC-[0-9]{1,3}` and slug checks are enforced at `:161-165`, `:196-201`; the manifest subject key set matches `REQUIRED_MANIFEST_SUBJECT_KEYS` exactly. |

## Blocker 1 — the carried `prior_attempts` entry is schema-invalid; every attempt 2 returns `R01_BINDING`

`trusted_review_builder.py:255-257` appends `{"attempt_epoch": attempt - 1, "progress_identity": …}` and nothing else.

`_validate_ledger` (`orchestrator_policy.py:665-681`) requires each prior-attempt entry to carry **`decision_digest` (sha256), `outcome` ∈ `OUTCOMES`, and `rule_id` starting with `R`** in addition to those two. Three schema errors are produced, and `decide()` (`:1372-1374`) short-circuits any schema error to `R01_BINDING` → `ESCALATED` before rules are evaluated.

So the carry is self-defeating: with no `prior_context`, `prior_attempts` stays `[]` and the cycle works; the moment attempt 1 REWORKs and `production_cycle_cli.py:206-211` populates `progress_identity`, attempt 2 escalates unconditionally. All three missing fields are already present in `decision.json` (`local_orchestrator_runner.py:103`, `_make_decision:400-412`), so this is a fill-in, not a redesign.

The counters/nonce/registry halves of the carry are correct: `budgets_after` keys match the ledger's allowed counter set exactly (`:647-654`), and the carried nonce string `run_{task_id}.attempt-1-nonce` matches what the builder mints at `:269`.

## Blocker 2 — with the registry carried, acceptance after a rework is structurally unreachable

`trusted_review_builder.py:212` hard-codes attempt 2 to `final_full`, and `:281` always sets `prior_findings: None`.

In builder mode the only reachable REWORK is `R11_OPEN_FINDINGS` — gate failures raise `BuilderError` before review, evidence always matches what the builder minted, and the mode is always full (so `R09`/`R13`/`R15` cannot fire). `R11` fires on the **merged** registry (`:1224`, `:1254`), and `merge_finding_registry` only clears an open record under `review_mode == "targeted_verification"` with a matching tree digest (`:1064-1076`). A `final_full` attempt-2 verdict therefore inherits the attempt-1 blocking finding as still-open, `_rework_available` is now false (`rework_used=1` = budget), and the decision is `R12_FINDINGS_EXHAUSTED` → `ESCALATED`.

Net: fixing Blocker 1 alone still leaves the CLI's advertised "one authenticated rework, then accept" path (`tests/test_production_cycle_cli.py:112-123`, mocked) unreachable whenever the builder is driving. This is fail-closed, not unsafe — but the second leg of the packet's goal is still not demonstrated.

## Major 3 — `run_id` can overflow the reviewer schema; no builder-side check

`:204` mints `run_id = f"run_{task_id}.attempt-{attempt}"`, while `:162` accepts any slug matching `^[a-z0-9][a-z0-9._-]{1,63}$` — up to 64 characters. The schema's `run_id` is `^run_[0-9A-Za-z._-]{1,64}$` (`review-verdict.schema.json:618-621`), so any `task_id` longer than 54 characters yields a `run_id` that fails schema validation → `contract_valid: false` → `ProjectionError` → `ESCALATED`, with no builder error naming the cause. This is the same failure class as the identifier blocker just closed, only configuration-dependent. Validate the minted `run_id` against the schema pattern at build time rather than validating only its inputs.

## Major 4 — no test exercises the attempt-2 carry path

`tests/test_trusted_review_builder.py` never passes `prior_context`, and the CLI builder test (`tests/test_production_cycle_cli.py:172-219`) returns `ACCEPTED` on attempt 1, so `production_cycle_cli.py:201-211` never executes. Blockers 1 and 2 both live entirely in that uncovered path — the same coverage gap that let the previous two blockers survive, moved one leg down. A test that drives attempt 1 → `REWORK` → attempt 2 through the real `POLICY.decide` would catch both.

## Minor, carried forward unchanged

Basename-only gate allowlist and unsanitized gate env, advisory-only seal, unvalidated numeric config for direct callers, `_ignored_state` cost on large ignored trees, `capture_clean_baseline` outside `run_managed_cycle`'s try (`production_cycle_cli.py:153`) surfacing a dirty worktree as `ERROR`/exit 2. Also `state/tasks/2026-08-12-orchestrator-trusted-input-builder/EVIDENCE.md` still reads "Pending implementation, tests, canary, and independent closure", and `TASK_PACKET.md` items 2–10 remain unchecked.

TRUSTED_BUILDER_FINAL_REWORK
