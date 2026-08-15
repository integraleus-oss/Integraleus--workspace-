## Independent final review — uncommitted diff only

**Scope reviewed:** the 12 modified files in `git diff` (prior-finding carry + Ctrl-C interruption). Untracked `state/tasks/2026-08-15-orchestrator-pilot-rework/` read only as the claim set.

**Verification caveat:** Bash execution was denied in this session (`don't ask` mode), so I could **not** rerun the suites. The report's `90/90`, `85/85`, `py_compile`, and `git diff --check` claims are unverified here; all findings below are from static reading.

### What holds up

- No path found where these changes can produce an unwarranted `ACCEPTED`. `INTERRUPTED` is terminal and non-accepting everywhere it is introduced.
- `INTERRUPTED` is not child-spoofable: `agent_launcher.py:131` keys off the local `interrupted` flag, not the child's exit code, so a wrapper exiting `130` still yields `FAILED`.
- `admit_live_review` returns `dict(manifest)` (`managed_policy_review.py:55`), which has no `status` key, so the reviewer cannot forge `INTERRUPTED` through `managed_one_cycle.py:59`.
- `PRIOR_FINDING_DETAIL_KEYS` (`validate_review_verdict.py:38`) exactly equals the schema's `$defs.finding` properties plus `status` (`review-verdict.schema.json:946-1047`) — the allowlist is closed with no compatibility hole, and the minimal `{finding_id,status}` contract still validates.
- ID normalization is consistent: `_load_prior_finding_details` and `build_projection` both apply `normalize_derived_review_ids`, so carried IDs match registry IDs.

### Findings

**MEDIUM — builder does not check completeness, only presence; report overstates it**
`trusted_review_builder.py:306-315` verifies each open registry ID has *a dict whose `finding_id` matches*. A record of `{finding_id, status, title}` passes the builder and is sealed. Completeness is enforced only later, by the core validator, when the *next* verdict is admitted. REPORT.md:18-19 ("requires a complete record for every open registry ID and stops fail-closed if any detail is missing") describes behavior the code does not implement at that point.

**MEDIUM — a defect in the sealed trusted input is misattributed to the reviewer and burns the contract-repair retry**
Following from the above: `prior_findings_invalid` is a `_tool_error`, so `build_projection` raises `ContractValidationError` (`review_projection.py:132`), which `live_review_cycle.py:142` treats as a reviewer contract failure and answers with a full contract-repair Claude launch (`:166`). `prior-findings.json` is sealed and chmod `0444` (`trusted_review_builder.py:339-341`), so the retry can never fix the actual cause — one guaranteed-wasted review launch plus evidence that blames the reviewer for a trusted-input defect. Previously prior-findings were builder-generated ID pairs and effectively could not be invalid; carrying rich records makes this reachable.

**MEDIUM — `SIGINT` can be left ignored process-wide**
`agent_launcher.py:112/117` installs `SIG_IGN` and restores it only at `:146-147`, outside any `finally`. If `_terminate_process_group` raises — `os.killpg` `PermissionError`, or the second `communicate(timeout=2)` at `:45` raising `TimeoutExpired` when a grandchild in another process group still holds the pipes — the exception escapes `launch()` with `SIGINT` still `SIG_IGN`. The operator then cannot Ctrl-C the orchestrator for the rest of the run, and no `launch-result.json` is written for that launch. Wrap `:125-147` in `try/finally`.

**MEDIUM — the repeated-interrupt regression test is effectively vacuous and timing-fragile**
`tests/test_agent_launcher.py:95-111`: the second timer fires at 0.3s, but teardown completes in ~10ms after the first SIGINT at 0.2s, so `finally: second.cancel()` (`:107`) runs at ≈0.21s and normally cancels it before it ever fires. In the narrow window where it does fire after the handler is restored, `KeyboardInterrupt` lands in the test body and errors the run. Either way it does not reliably exercise "repeated Ctrl-C during teardown." Assert the ignore window directly (e.g. patch `_terminate_process_group` to signal itself) rather than racing wall-clock timers.

**MEDIUM — new fail-closed branches have no negative tests**
All three raises at `trusted_review_builder.py:305/309/313` are uncovered — the only builder test touched (`tests/test_trusted_review_builder.py:216-252`) is the happy path. Likewise the validator gains ~12 new rejection rules (`validate_review_verdict.py:379-406`) with only two *positive* tests added (`tests/test_review_verdict.py:459,476`); nothing asserts that an incomplete detailed record (missing `fingerprint`, or a `major` without `evidence`) is rejected with `prior_findings_invalid`. For a change whose stated purpose is fail-closed completeness, the fail-closed direction is untested.

**LOW — digest verification is opt-in at the API boundary**
`production_cycle_cli.py:49,52`: `expected_digest=None` silently skips verification, and the call site (`:259`) uses `manifest.get("input_digests", {}).get("review_verdict")`, which degrades to `None` if the key is absent. In production the runner always populates it (`local_orchestrator_runner.py:113`), so this is currently unreachable — but it is a fail-open default on a trust boundary. Make the digest required. Also note the content is consumed at `:258` *before* the registry digest check at `:261-263`; verify first.

**LOW — `PRIOR_FINDING_DETAIL_REQUIRED` is weaker than the finding schema**
`validate_review_verdict.py:44-47` omits `occurrence_id`, `confidence`, `proposed_disposition`, and — for `blocker`/`major` — `failure_scenario` and `reproduction`, all of which the schema mandates (`review-verdict.schema.json:935-945,1093-1099`). A carried record can therefore be accepted as a "complete" prior finding while being strictly less complete than the verdict it came from. Relatedly, `test_advisory_prior_finding_may_omit_major_only_details` builds a `nit` record carrying a major-category fingerprint — a shape a real carry cannot produce.

**LOW — interrupted-retry cycle results reshape the evidence document**
`live_review_cycle.py:132-133`, `:172-173`, `:201-203` set `"launch"` to the *retry* launch record and omit `format_retry_launch`/`contract_retry_launch`/`contract_format_retry_launch`. A consumer reading `cycle-result["launch"]` gets a different thing than in `DECIDED`/`FAILED_LAUNCH` results, and the initial launch disappears from the summary (on-disk per-launch evidence is intact).

**LOW — the `130` contract has holes outside the cycle window**
`production_cycle_cli.py:299` catches `Exception`, not `KeyboardInterrupt`, so Ctrl-C during `load_packet` or the final `print` exits `1` with a traceback and no JSON line. Symmetrically, `managed_one_cycle.py:110` writes the terminal record outside any ignore window, so a second Ctrl-C there loses `cycle-result.json`. Also note `KeyboardInterrupt` inside `local_orchestrator_runner.run` bypasses `live_review_cycle.py:211` (`except Exception`), leaving no `cycle-result.json` and a stray generated verdict inside the sealed input dir — the managed cycle still records `INTERRUPTED`.

**INFO — trust-boundary widening is real but unlabelled**
The sealed bundle now carries reviewer-authored free text (`title`, `rationale`, `failure_scenario`, `suggested_remediation`, and `evidence` excerpts sourced from repo files) into inputs the next reviewer is told are trusted (`production_cycle_cli.py:229-236`). Integrity is bound (seal + `prior_findings_canonical_digest`), but provenance is not: nothing marks these records as model-authored data rather than instructions. Worth an explicit "treat prior findings as untrusted data" line in the review instructions before any further use.

**INFO — details are replaced, not merged**
`production_cycle_cli.py:269-278` rebuilds `prior_finding_details` from the newest verdict only. Safe today solely because `run_managed_cycle` hard-rejects `max_attempts != 2` (`managed_one_cycle.py:38`), so targeted verification only ever consumes the attempt-1 verdict. Any future third attempt would hit `BuilderError` for a registry finding that stayed open without being re-reported.

### Report accuracy

Mostly faithful and appropriately hedged on activation. Two overstatements: the builder completeness claim (REPORT.md:18-19, see MEDIUM #1), and "covered by regression tests" for the interruption work (REPORT.md:78-79) — the repeated-interrupt test is likely vacuous and the builder's fail-closed branches have no tests. The `90/90` / `85/85` figures I could not check.

### Verdict

**REWORK** — bounded. No fail-open acceptance path and no trust-boundary break was found, but the headline fail-closed guarantee is enforced one stage later and looser than claimed, its branches are untested, and the interruption path can permanently disable the operator's Ctrl-C. Fixing MEDIUM #1, #3, #4, #5 (and #2 falls out of #1) is a small, well-scoped change set.
