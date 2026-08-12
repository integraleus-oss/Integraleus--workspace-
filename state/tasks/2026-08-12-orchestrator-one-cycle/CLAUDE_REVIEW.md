Bash was denied in this session, so I reviewed statically — **I did not execute the tests**, and I could not verify the EVIDENCE.md counts (36/36, 84/84, `py_compile`, `git diff --check`). Everything below is from reading the five files plus a directory listing of `managed-trial-r1/` (which does contain `attempt-1/`, `attempt-2/`, `cycle-result.json`).

## Direct answers

**Is acceptance authority deterministic?** No — it is *deterministic given a verdict*, but the verdict is not policy-bound. The controller is a faithful, replay-guarded state machine over whatever `review` hands it; the decision itself is imported wholesale.

**Does the trial prove Codex → Claude → REWORK → Codex → Claude → ACCEPTED?** It proves the Codex half and the controller's sequencing/packet-carry. It does not prove the Claude half as a *decision* path, because EVIDENCE.md states both `local_orchestrator_run_result` records were coordinator-created from observed reviews rather than emitted by the review-contract projection and policy runner. That statement is honest and matches the artifact.

## Blocker

**B1 — `outcome` is trusted verbatim; `rule_id` is a shape check, not an authority check.** `managed_one_cycle.py:44-49` requires only `document_type == "local_orchestrator_run_result"` and `isinstance(rule_id, str)`. Nothing checks that `rule_id` is in the accepted rule catalog, that it is non-empty, that `schema_version` is present, or — critically — that the rule *implies* the outcome. `{"document_type": "local_orchestrator_run_result", "rule_id": "", "outcome": "ACCEPTED"}` yields `status: ACCEPTED`; so does `rule_id: "R11_OPEN_FINDINGS"` paired with `ACCEPTED`, which is precisely the inversion of the trial's own attempt-1 record. `test_untrusted_review_result_escalates` (`tests/test_managed_one_cycle.py:68`) only covers a *missing* envelope, so this gap is untested as well as unenforced. Until `rule_id → outcome` is derived rather than accepted, "deterministic acceptance authority" is not established — the open policy-binding gate in EVIDENCE.md:37-41 *is* this blocker, correctly named.

## Major

**M1 — the trial artifact cannot corroborate the Claude side.** `cycle-result.json` carries `launch_result` paths for both Codex attempts but no path to any Claude review evidence — the `review` objects are inline literals with no provenance pointer. The `attempt-N/claude/` directories exist on disk, yet nothing in the record binds a verdict to them. As proof-of-chain the artifact is one-sided: it evidences Codex, asserts Claude.

**M2 — the cited proof artifact is untested.** Every test asserts on the return value; none reads `cycle-result.json` back from disk. `_write` (`managed_one_cycle.py:15-16`), the `sort_keys`/separators serialization, and the file's existence and location are covered by zero tests, while EVIDENCE.md:34-35 leans on that exact file as the proof the controller enforces two attempts.

**M3 — an exception mid-cycle leaves a poisoned root and no terminal record.** `root.mkdir` happens at `managed_one_cycle.py:31`, but `_write` only runs at line 67 on the normal path. If `implement` or `review` raises (or the history contains anything non-JSON-serializable), the root exists with no `cycle-result.json`, and every subsequent call raises `CycleError("cycle root already exists")` at line 30. There is no deterministic terminal document for the crash case — the strongest failure mode produces silence rather than `ESCALATED`.

**M4 — the rework packet steers attempt 2 with only a non-empty-string check.** Line 52-53 validates `rework_context` as a non-empty `str` and passes it straight into the next `implement` call, which in the live trial was a real workspace-write Codex launch. No length bound, no shape, no allow-list. Same trust root as B1, but with write-side consequences.

## Nit

- `managed_one_cycle.py:51-58`: on a second `REWORK`, `final` becomes `ESCALATED` while `history[-1]["outcome"]` stays `"REWORK"` — whereas the missing-packet path (lines 54-55) rewrites the history entry. Two escalations, two different audit shapes.
- `max_attempts` is a keyword parameter that raises for every value but `2` (lines 26-27). A constant wearing a knob's clothing.
- No test for empty-string or non-`str` `rule_id`, nor for `document_type` present with `rule_id` absent as a distinct case.
- `TASK_PACKET.md:3,27` still reads `IMPLEMENTED_AWAITING_LIVE_TRIAL_AND_REVIEW` with "Run synthetic bounded end-to-end trial" unchecked, while EVIDENCE.md:3,30-36 reports that trial as done. One of the two records is stale.

## Assessment

The slice is honest about its boundary — EVIDENCE.md:37-41 names the policy-binding gap without overclaiming, and the packet correctly withholds the commit. But the review asks whether acceptance authority *is* deterministic, and it is not: B1 is the gap, and M1/M2 mean the trial artifact cannot close it by evidence either. M3 is an independent correctness hole unrelated to the stated gate.

ONE_CYCLE_REWORK
