# Independent review — orchestrator pilot rework (uncommitted diff)

Scope: the 10 modified tracked files only. I read the diff and the surrounding call chain (`live_review_cycle`, `local_orchestrator_runner`, `managed_policy_review`, `review_projection`, `orchestrator_policy`, `review-verdict.schema.json`). I could **not** re-run the test suites — Bash execution was denied in this session — so the report's `90/90` / `85/85` counts are unverified, not disputed.

Short paths below are relative to the repo root; `2026-08-12-…` = `state/tasks/2026-08-12-orchestrator-integration/`, `2026-08-11-…` = `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`.

## Blocker

**1. The detailed prior-finding validator is stricter than the verdict contract it consumes — a carried `nit` will fail the whole targeted review.**
`2026-08-11-…/validate_review_verdict.py:374-391` requires `rationale`, non-empty `evidence`, and `location`-or-`location_absent_reason` for *every* entry that carries any detail. The review-verdict schema only requires those for `blocker`/`major` (`review-verdict.schema.json:1079-1118`); for `nit` they are optional, and `location: null` is explicitly valid (`:993-1002`). The registry marks *every* observed finding `open` regardless of severity (`orchestrator_policy.py:1043`), so `trusted_review_builder.py:306-311` will carry a nit, `production_cycle_cli.py:59` copies it verbatim (`location: null` included), and the next review then fails validation.

Failure path: attempt-1 verdict with one blocker + one advisory nit lacking evidence → `REWORK` → attempt-2 prior-findings contains the nit → `prior_findings_invalid` → `contract_valid` false → `ContractValidationError` at `review_projection.py:132` → contract retry cannot fix a *sealed input* → `FAILED_ADMISSION` → `ESCALATED`. Before this change the minimal `{finding_id, status}` entry passed. This is fail-closed, but it breaks exactly the flow the change exists to enable, and the project's own `claude-review.md:39` calls "an advisory nit with no location" the common case. Gate the strict checks on `severity in {blocker, major}` (and accept `location: null`).

## Major

**2. Ctrl-C during the review leg is classified `ESCALATED`, not `INTERRUPTED`.**
`agent_launcher.launch` now returns `status: "INTERRUPTED"`, but `live_review_cycle.py:79` maps any non-`OK` launch to `FAILED_LAUNCH`; `admit_live_review` then raises (`managed_policy_review.py:27`) and `managed_one_cycle.py:88` records `ESCALATED` (exit 4). Only the Codex leg was taught the new status (`production_cycle_cli.py:196`, `managed_one_cycle.py:52-55`). Net effect: the terminal classification depends on *where* SIGINT lands — during the Claude subprocess (the longest wall-clock window) it is indistinguishable from a genuine review failure; anywhere else in the loop it becomes `INTERRUPTED` via the broad handler. Propagate `INTERRUPTED` through `run_cycle` and the admission step.

**3. A second Ctrl-C during teardown loses all the evidence the change promises.**
`agent_launcher.py:33-39` can block up to ~4 s inside `_terminate_process_group` (`communicate(timeout=2)` twice). A second SIGINT there raises `KeyboardInterrupt` out of `launch()` entirely: no `SIGKILL` escalation, no `stdout.log`/`stderr.log`, no `launch-result.json`, and the child process group can survive. The same hole exists between `Popen` (`:84-87`) and the inner `try` (`:88`) — the new handler does not cover process creation, so an interrupt in that window orphans the group with zero record. Repeated Ctrl-C is the ordinary operator reflex, so this is reachable, not theoretical. Wrap termination + evidence write so they are not interruptible (dedicated `try/finally`, or catch `BaseException` around teardown) and extend the handler to cover `Popen`.

## Medium

**4. New behavior is under-tested; the fail-closed guards have zero coverage.**
- No negative test for any of the six new validator branches (`validate_review_verdict.py:379-391`) — only the positive case at `test_review_verdict.py:459`. Defect #1 would have surfaced from one nit-severity fixture.
- No test for the builder's new fail-closed guard (`trusted_review_builder.py:304-309`), neither the missing-detail nor the non-dict path.
- No test for `_load_prior_finding_details` failure modes (missing file, non-list `findings`, duplicate IDs) — all raise `PacketError` untested.
- `tests/test_production_cycle_cli.py:56-67` patches `normalize_derived_review_ids` outright, so nothing proves real reviewer IDs normalize onto the registry IDs the builder looks up — the exact mismatch the report says was discovered mid-replay.

## Low

**5. Finding details are read without the digest binding used one line later.** `production_cycle_cli.py:48-60` re-reads `input-review_verdict.json` with bare `json.loads` and no check against `manifest["input_digests"]["review_verdict"]`, which is available (`local_orchestrator_runner.py:113`), while the adjacent registry read is double-bound (`:249-251`). Post-admission artifact in a 0444 local run dir, so exposure is small, but it breaks the file's own re-verification pattern; also a malformed file escapes as `JSONDecodeError` rather than `PacketError`.

**6. "Complete record" is presence-only.** `trusted_review_builder.py:308` checks the ID is in the map, not that the record is well-formed, so a structurally incomplete record is sealed and only rejected later as an opaque reviewer contract error (see #1). The carried `occurrence_id` is also an attempt-1-derived ID re-presented as current-cycle prior input — allowlisted but stale.

**7. Validator edge cases.** `has_details = set(item) != {"finding_id","status"}` (`:374`) treats `{"finding_id"}` alone as "detailed" and emits ~7 cascading errors for what is a missing-`status` entry; `location_absent_reason` is accepted as any string rather than the schema enum (`:389-390`); and the location/`location_absent_reason` mutual exclusivity enforced for verdict findings (`:601`) is not applied here.

**8. Interrupt test can abort the whole run.** `tests/test_agent_launcher.py:79` fires SIGINT at the process from a 0.2 s timer; if it lands outside `launch()`, unittest treats `KeyboardInterrupt` as a run-level abort, not a single test failure. The `exit_code == 130` assertion also loses to the race where the child exits exactly at SIGINT — `killpg` then raises `ProcessLookupError`, which the outer `except OSError` (`:107`) converts to `exit_code 126` with emptied output while `interrupted` stays true.

## Does the report overstate the evidence?

Yes, in three places:

- *"Both blockers … are closed"* (`REPORT.md:7-9`) — not supported given #1 and #2.
- *"The launcher catches operator interruption, terminates the child process group, preserves stdout/stderr and launch evidence"* (`:26-28`) — holds only for a single SIGINT delivered while blocked in `communicate`; #3 breaks it. The drill's *"no orphaned pilot process"* (`:87-88`) is a one-trial observation of that one path.
- *"The managed cycle records a terminal INTERRUPTED cycle result, does not run review"* (`:29-31`) — true for the Codex leg only; presented as general.

The targeted replay (`:60-74`) is honest about what it did, but *"All three findings were supplied with title, severity, rationale, location, fingerprint…"* means all three were detail-complete records — precisely the case that cannot hit defect #1. The replay validates the happy path, not the contract.

Accurate as written: the key-allowlist claim (`:20-22`) — `PRIOR_FINDING_DETAIL_KEYS` matches the verdict `finding` property set exactly plus `status` — and the builder fail-closed claim, read narrowly as presence-only.

## Verdict

**REWORK** — one blocker (#1) that fail-closed-breaks the carry it implements, plus two majors: interruption is only half-wired (#2) and loses its own evidence under repeated Ctrl-C (#3). No files were modified.
