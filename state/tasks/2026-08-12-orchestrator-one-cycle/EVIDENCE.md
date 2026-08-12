# Evidence — managed one-cycle orchestrator

Status: REVIEW_REWORK_FIXED_POLICY_PROVENANCE_OPEN

Implemented `managed_one_cycle.py` with a hard two-attempt ceiling. It records
every attempt and permits only `ACCEPTED`, `REWORK`, `FAILED_INFRA`, or
`ESCALATED`. A second `REWORK`, missing rework packet, unknown outcome, unknown
implementation failure, replayed cycle root, or altered budget escalates.

Verification:

- integration suite: 40/40 passed;
- accepted policy core: 84/84 passed;
- `py_compile`: passed;
- `git diff --check`: passed.

Remaining gates:

- wire the controller callbacks to the accepted Codex launcher and
  `live_review_cycle` using a disposable synthetic repository;
- prove `REWORK -> second Codex attempt -> closure -> ACCEPTED` live;
- independent Claude closure review;
- scoped local commit only after those gates.

## Live synthetic trial

- Disposable git repository: `synthetic-repo/`, seeded with `add()` incorrectly
  subtracting and a deterministic failing unittest.
- Attempt 1: real local Codex read-only launch completed; fresh Claude review
  found the exact defect and returned `REWORK`.
- Attempt 2: real local Codex workspace-write launch changed only `calc.py`;
  coordinator-observed unittest passed 1/1; fresh Claude closure returned
  `ACCEPTED`.
- `managed-trial-r1/cycle-result.json` proves the controller enforces two
  attempts and carries the bounded rework packet into attempt 2.

Important boundary: the trial's controller replay used coordinator-created
`local_orchestrator_run_result` records derived from the observed reviews; it
did not yet generate both decisions through the full review-contract projection
and policy runner. Therefore the agent path and controller behavior are proven,
but automatic policy binding remains an open gate and no commit is allowed yet.

## Independent review rework

Claude returned `ONE_CYCLE_REWORK`: one authority blocker and four majors.
Rework completed:

- outcome is derived from the accepted `rule_id -> outcome` table and a mismatch
  escalates;
- rework packet is non-empty and capped at 8192 bytes;
- callback exceptions write a durable terminal `ESCALATED` result;
- second `REWORK` has a consistent escalated audit shape;
- cycle-result serialization is read back and asserted by tests.

Remaining honest gate: controller inputs still need automatic provenance from
the full contract/projection/policy runner rather than coordinator-created
policy-result records. This is the next bounded increment; no commit yet.

## Automatic policy admission increment

Added `managed_policy_review.py`. It accepts only a `DECIDED` live-review
result whose decision directory remains under the live cycle root, whose
durable `run-result.json` exactly matches the returned manifest, and whose
decision/projection digests match. For `REWORK`, it builds the controller's
bounded packet only from `FIX_FINDINGS` directives and matching findings in the
trusted projection. Missing, escaping, tampered, or incomplete provenance
fails closed.

The mocked-wrapper integration now exercises the complete mechanical path:
Claude envelope -> contract validation -> trusted projection -> deterministic
policy -> digest admission -> derived rework packet. A fresh real two-review
trial remains required before closure and commit.

## Fresh live provenance trial

The first fresh Claude leg completed and was admitted mechanically as
`REWORK / R11_OPEN_FINDINGS`; all launch, extraction, contract, projection,
decision, and admission artifacts are under `live-provenance-trial/review-1/`.

The closure leg correctly failed admission. Claude independently ran the
synthetic unittest (1/1 passed) but refused to emit the supplied accepted
fixture because that fixture was bound to a different repo subject, commits,
path, evidence command, and criterion. The runner preserved this as
`FAILED_ADMISSION` under `live-provenance-trial/review-2/`; no policy decision
was created. This exposed a real trial-design defect rather than an
infrastructure failure: an honest accepted verdict must be generated against a
manifest and binding derived from the actual synthetic repo and observed gate
evidence. Replaying a pre-bound unrelated fixture would undermine the
provenance guarantee.

## Honest subject-bound closure

The synthetic fix was committed inside the disposable repository as
`9d035e2`, with base `a285519`. The closure manifest binds the actual commits,
`calc.py` diff digest, changed-files digest, `calc.py`/`test_calc.py` coverage,
and observed `python3 -m unittest -v` evidence (1/1 passed).

The first honest closure response verified the facts but included Markdown
fences, so strict transport admission rejected it and produced no policy
decision. One bounded format-only retry returned exact JSON. Contract,
projection, deterministic policy, durable digest admission, and controller
admission then completed as `ACCEPTED / R17_ACCEPT`. Artifacts are under
`live-provenance-trial/honest-closure-review-r2/`.

Post-trial checks: integration 45/45; accepted core 84/84; py_compile and
whitespace passed. Independent closure review remains the final pre-commit
gate.

## Independent review rework

Bounded closure review confirmed deterministic authority, digest/path
admission, both live admitted decisions, and both fail-closed rejected closure
responses. It found one major completeness gap: `managed_policy_review.py`
derived packets only for `R11/FIX_FINDINGS`, while accepted policy also emits
`R09/FIX_GATES`, `R13/PROVIDE_EVIDENCE`, and `R15/REVIEW_ONLY_FULL` as REWORK.

The adapter now derives bounded packets for all four policy REWORK paths,
de-duplicates finding IDs, and still rejects unsupported or malformed
directives. Exact regressions cover the three added paths. Post-rework
integration suite: 46/46; py_compile passed. Targeted closure is pending.

Fresh targeted closure confirmed the major is closed and returned
`DIRECTIVE_CLOSURE_PASS`. Residual observations are non-blocking nits about
error-type normalization and one indirect unsupported-directive assertion.
