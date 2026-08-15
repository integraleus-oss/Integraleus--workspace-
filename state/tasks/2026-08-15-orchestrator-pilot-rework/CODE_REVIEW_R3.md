# Independent final review (R3) — uncommitted diff only

**Scope:** the 12 modified tracked files (`git diff`). Untracked `state/tasks/2026-08-15-orchestrator-pilot-rework/` read only as the claim set, plus two referenced live-drill artifacts.

**Verification caveat:** `python3` execution was denied in this session (`don't ask` mode), so I could not rerun the suites. Static method counts do match the report exactly — 94 `def test_` in `2026-08-12-orchestrator-integration/tests/`, 87 in `2026-08-11-.../implementation/tests/` — so `94/94` and `87/87` are at least arithmetically consistent; pass/fail is unverified here.

## What holds up

- **No fail-open path.** `INTERRUPTED` is terminal and non-accepting at every introduction point (`managed_one_cycle.py:53-55,59-63,73-78,99-102`; `live_review_cycle.py:83,131-135,171-175,200-205`; `production_cycle_cli.py:251-252,297-299`). It is not child-spoofable: `agent_launcher.py:138` keys off the local `interrupted` flag, so a wrapper exiting `130` still yields `FAILED`.
- **R2's four MEDIUMs are genuinely closed.** Builder completeness is now enforced at the builder (`trusted_review_builder.py:320-331`), SIGINT restoration is guaranteed by `finally` (`agent_launcher.py:154-156`), the repeated-interrupt test is now deterministic rather than timer-raced (`tests/test_agent_launcher.py:95-119` asserts `SIG_IGN` was installed *during* teardown and restored after), and negative tests exist for both the builder and the validator.
- **Allowlist is closed.** `PRIOR_FINDING_DETAIL_KEYS` (`validate_review_verdict.py:38-43`) equals the schema's `$defs.finding` properties (`review-verdict.schema.json:946-1047`) plus `status` — no unsupported key can ride through, and the minimal `{finding_id,status}` contract still validates (`:378`).
- **Detail fields are inert to policy.** `_prior_open_ids` (`validate_review_verdict.py:349-354`) reads only `finding_id`/`status`, so the richer records cannot move a rule outcome.
- **Digest binding is mandatory, not opt-in.** `production_cycle_cli.py:52` rejects a non-`str` digest, closing R2's LOW.
- **Live evidence checks out.** `pilot-interrupt-claude-r1/live-review/claude-launch/launch-result.json` is a real `INTERRUPTED`/`130` record, and `pilot-t02-targeted-replay-r5/review-inputs/prior-findings.json` is a real three-finding detailed carry that satisfies both the builder and validator contracts.

## Findings

**MEDIUM — the validator's detailed contract is looser than the schema it mirrors**
`validate_review_verdict.py:44-47` requires only `{finding_id,status,fingerprint,title,severity,category,criterion_id}`, omitting `occurrence_id`, `confidence`, `proposed_disposition` — all schema-mandatory (`review-verdict.schema.json:935-945`). The blocker/major branch (`:390-396`) checks `rationale`/`evidence`/location but never `failure_scenario` or `reproduction`, which the schema requires (`:1093-1099`), and nothing enforces the category→severity rule (`:1049-1078`): a record with `category: "security"` can be labelled `severity: "nit"` and skip every major-only requirement. The builder is *stricter* than the validator (`trusted_review_builder.py:25-42`), so the trust boundary is the weaker of the two enforcement points. Not reachable through the orchestrator's own path (input is always an already-admitted verdict), and detail fields cannot alter policy — but the validator is the standalone gate for coordinator-supplied prior findings, and REPORT.md:20-22 calls this "the sealed detailed prior-finding contract," implying parity that does not exist.

**LOW — one unbounded wait remains inside the SIGINT-ignored window**
`agent_launcher.py:37`: on `ProcessLookupError`, `_terminate_process_group` calls `process.communicate()` with no timeout, unlike both sibling calls (`:39,45`). In the KeyboardInterrupt path SIGINT is already `SIG_IGN` (`:112,120`), so a descendant that escaped the group while holding the inherited pipes would hang `launch()` with the operator's Ctrl-C disabled. In practice near-unreachable — an unreaped child (alive or zombie) keeps the group signalable, so `ESRCH` should not occur while `communicate()` is in flight — but it is the only unbounded wait in the interruption path and the fix is one keyword argument.

**LOW — teardown is not guaranteed against a second Ctrl-C in the handler-entry window**
`agent_launcher.py:110-112` / `:118-120`: between `interrupted = True` and `signal.signal(SIGINT, SIG_IGN)`, a second SIGINT raises `KeyboardInterrupt` inside the handler. From the inner handler it is re-caught by the outer one (fine); from the outer handler it escapes `launch()` with no teardown call and no `launch-result.json`, leaving the wrapper's process group alive. The report's "no orphaned pilot process" (REPORT.md:88) is demonstrated for single Ctrl-C only. Installing `SIG_IGN` as the first statement of each handler, or moving teardown into a `finally`, closes it.

**LOW — builder "completeness" is key-presence, not value-validity**
`trusted_review_builder.py:37` uses `PRIOR_DETAIL_MAJOR_REQUIRED.issubset(value)`, so `reproduction: []`, `evidence: []`, or `rationale: ""` all pass. The new fixture encodes exactly that: `tests/test_trusted_review_builder.py:230` carries `"reproduction": []` on a `major` finding, a shape the sealed schema forbids (`minItems: 1`). Unreachable from an admitted verdict, but the fixture teaches the wrong shape and REPORT.md:18-19's "complete record" is stronger than what runs.

**LOW — the ID-normalization step the whole carry depends on is mocked out**
`tests/test_production_cycle_cli.py:55` patches `normalize_derived_review_ids` and asserts against its own stub return value. Nothing in this diff exercises the real reviewer-ID → canonical-ID mapping that makes `detail_by_id` keys line up with registry IDs — the single mechanism whose absence caused a failed replay per REPORT.md:76-78. A fixture-driven test through the real function would be worth more than this one.

**LOW — remaining fail-closed branches untested**
No coverage for `trusted_review_builder.py:324` (non-dict `prior_finding_details`) or `:328` (open registry ID absent from details), nor for `production_cycle_cli.py:61` (verdict with no `findings` list) or `:66` (duplicate `finding_id`). The one builder negative assertion also shares a method with the happy path (`tests/test_trusted_review_builder.py:244-248`), so a regression there masks the positive assertions below it.

**LOW — Ctrl-C outside the launch window still has no structured result**
Two gaps carried unfixed from R2: `production_cycle_cli.py:300` catches `Exception`, so an interrupt during `load_packet` or the final `print` exits `1` with a traceback and no JSON line — REPORT.md:32's "returns exit code 130 for this terminal state" holds only when the interrupt lands inside `run_managed_cycle`. And `live_review_cycle.py:211` (`except Exception`) is bypassed by `KeyboardInterrupt` during `local_orchestrator_runner.run` (`:141`, `:210`), skipping the cleanup at `:212` and leaving the generated verdict inside the bundle directory, which then permanently blocks reuse of that bundle at `:103-104`. The managed cycle still records `INTERRUPTED`, so both are fail-closed, and the policy leg is milliseconds against a multi-minute launch — low exposure, incomplete claim.

**LOW — interrupted-retry cycle results reshape the evidence document**
`live_review_cycle.py:132-133`, `:172-173`, `:201-203` place the *retry* launch under `"launch"` and omit `format_retry_launch`/`contract_retry_launch`/`contract_format_retry_launch`, so `cycle-result["launch"]` denotes something different than in `DECIDED`/`FAILED_LAUNCH`. On-disk per-launch evidence is intact.

**NIT — `has_details` mislabels a malformed minimal record**
`validate_review_verdict.py:378`: `{"finding_id": X}` with `status` missing now trips the detailed branch and emits four spurious "detailed prior finding …" errors alongside the correct status error. Still fail-closed; only the operator-facing report becomes misleading.

**NIT — residual timing sensitivity in the first interrupt test**
`tests/test_agent_launcher.py:82-88`: the 0.2 s timer fires unconditionally; if the process is starved before `agent_launcher.py:89`, `KeyboardInterrupt` lands outside the guarded region and errors the test. Small window, but the sibling test at `:95-119` shows the deterministic pattern.

**INFO — the trust-boundary widening is real; the mitigation is prompt-level only**
The diff converts prior-findings from an ID+status list into a carrier for reviewer-authored prose. The replay artifact makes this concrete: `pilot-t02-targeted-replay-r5/review-inputs/prior-findings.json` carries ~2 KB rationales and instruction-shaped `suggested_remediation` text ("Derive the project root … for example const projectRoot = fileURLToPath(…)"), plus `evidence[].excerpt` quoting Codex-authored source, into inputs the next reviewer is told are trusted. Integrity is bound (seal at `trusted_review_builder.py:349-355`, `prior_findings_canonical_digest` at `:341`); provenance is not structurally enforced. The mitigation is one sentence in the launch prompt (`production_cycle_cli.py:233`) — and it sits in the constructed prompt, not in the manifest-digest-bound `review-instructions.md`. REPORT.md:118-120's "addressed" overstates a prompt-only defense.

**INFO — carry is replace-not-merge**
`production_cycle_cli.py:270-279` rebuilds `prior_finding_details` from the newest verdict only. Safe solely because `managed_one_cycle.py:38` hard-rejects `max_attempts != 2`, so the carry happens once from an `initial_full` verdict that lists every open finding. A third attempt would hit `BuilderError` at `:328` for any registry finding that stayed open without being re-reported — fail-closed, but as an exit-2 `ERROR` rather than a classified terminal state.

**INFO — fail-closed builder leaves a partial input directory**
`trusted_review_builder.py:313-315` writes `policy.json`, `review-instructions.md`, etc. before the completeness checks at `:327-331`, so a rejection leaves an unsealed half-built directory (the new test creates one at `attempt-2-incomplete`). Not exploitable — `verify_seal` requires `seal.json` — but it is residue.

## Report accuracy

Broadly faithful and correctly hedged on non-activation; the drill and replay artifacts I could read match their claims. Three phrasings to soften:

- REPORT.md:18-19 — "requires a complete record … if any detail is missing": enforcement is key-presence, not value-validity (LOW #4).
- REPORT.md:32 — "The production CLI returns exit code `130` for this terminal state": true only for interrupts landing inside the managed cycle (LOW #7).
- REPORT.md:118-120 — the provenance concern is *mitigated by a prompt line*, not "addressed" (INFO).

One smaller point: REPORT.md:26-27 claims the launcher "preserves stdout/stderr"; in the Claude-leg drill both digests are the empty-string SHA-256, so the drill demonstrates the mechanism ran, not that partial output survives. The code path does capture buffered output via `communicate()`, so the capability is real — it is just not what that evidence shows.

## Verdict

**ACCEPT.**

The two scoped fixes do what they claim, fail closed at every boundary I could reach, introduce no path to an unwarranted `ACCEPTED`, and close all four of R2's MEDIUMs with real (not vacuous) tests plus corroborating live artifacts. The one remaining MEDIUM is defense-in-depth on a standalone validator whose detail fields cannot influence any policy outcome, and every other item is LOW/INFO. None of it blocks the stated scope of a local, non-activated manual pilot.

Recommended before any further use, in priority order: tighten `PRIOR_FINDING_DETAIL_REQUIRED` and the major branch to schema parity; add `timeout=2` at `agent_launcher.py:37`; install `SIG_IGN` as the first statement of both interrupt handlers; replace the `reproduction: []` fixture and unmock the normalization test; soften the three report claims above.
