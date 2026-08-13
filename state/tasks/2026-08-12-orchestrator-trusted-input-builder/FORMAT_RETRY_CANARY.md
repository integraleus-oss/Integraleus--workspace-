# Bounded format-only retry canary

Status: FORMAT_RETRY_PROVEN; CONTRACT_ADMISSION_BLOCKED
Date: 2026-08-13

## Result

- Fresh isolated repository: `trusted-builder-two-attempt-r5`.
- Attempt 1 Codex changed only `src/calc.py` as instructed.
- Initial Claude review returned substantively useful review JSON wrapped in prose.
- Exact-JSON extraction rejected the initial response and policy did not run.
- Exactly one `claude-format-retry` leg ran without a second Codex invocation.
- Seal verification ran before the retry and again before verdict extraction.
- The retry returned exact JSON and produced `verdict-extraction.json`.
- Contract projection then rejected the verdict as not contract-valid; policy did
  not run and the managed cycle ended `ESCALATED` after one Codex attempt.

## Verification

- Focused format-retry/production tests: 21/21 PASS.
- Full integration suite: 77/77 PASS.
- Accepted core regression suite: 84/84 PASS.
- `py_compile`: PASS.
- `git diff --check`: PASS.

## Next blocker

The transport retry is bounded and fail-closed as required. The fresh canary
exposed a separate reviewer-contract blocker: exact JSON can still be schema-
invalid. Diagnose the concrete contract mismatch, tighten the format-only retry
prompt/fixture without weakening validation, add a regression, then repeat in a
new clean run.

## Follow-up canaries

- r6: exact JSON on the first Claude leg; derived IDs normalized correctly;
  rejected only because `gate_artifact` lacked its required digest-bound
  `artifact_ref`.
- r7: evidence-kind instruction corrected that mismatch, but contract transport
  rejected a decoded newline (`U+000A`) inside a JSON string value. Policy did
  not run. Claude also independently confirmed that the sealed inputs expose
  only the acceptance-criterion digest, not its authoritative plaintext.

Next change must bind criterion plaintext into the sealed reviewer packet and
forbid decoded control characters in verdict string values. Then repeat in a
fresh r8 run.

- r8: both changes worked. Claude evaluated the sealed AC-1 plaintext as
  violated and transport accepted its strings. Contract validation rejected a
  secondary nit finding because it omitted required `finding_id` and
  `fingerprint`; no policy execution occurred.
- r9: all required fields were present; rejected only because one
  `fingerprint.normalized_title` contained a hyphen forbidden by the schema.
- r10: full first-leg closure succeeded. Exact JSON, contract validation,
  trusted projection, deterministic policy and finding registry all passed;
  policy returned `REWORK / R11_OPEN_FINDINGS` with a single blocker and a
  policy-authenticated rework packet for `src/calc.py`. Attempt 2 then hit the
  hard 300-second Codex timeout and the cycle escalated fail-closed without a
  second review.

The remaining live-canary blocker is now Codex rework latency/capacity, not
review transport or contract admission. Repeat from a clean repository with a
bounded 600-second Codex timeout before changing controller semantics.

- r11: clean baseline and 600-second Codex bound were configured correctly.
  Attempt 1 Codex completed in about 40 seconds and the initial Claude response
  again triggered the single format-only retry. The retry returned exact JSON,
  but used an unrelated `trusted_review_verdict` schema rather than the sealed
  `review_verdict` contract. Projection therefore failed closed before policy;
  attempt 2 never started. The 600-second rework-latency hypothesis was not
  exercised. This exposes reviewer schema selection as nondeterministic even
  after r10's successful admission.
- r12: sealed schema made attempt-1 admission deterministic and the 600-second
  limit was sufficient; attempt 2 completed in 35 seconds. However, Codex
  followed the conflicting original task prose and preserved subtraction, so
  the rework remained open. The targeted verdict then failed on one omitted
  nullable-required conclusion field.
- r13: the attempt-2 authority boundary was corrected by sending only the
  policy-authenticated rework directive. Codex changed `src/calc.py` to
  `return left + right`. The targeted verdict was schema-valid but semantic
  admission failed closed: it used the file-byte digest rather than the
  canonical JSON digest for prior findings, and its `appears_fixed` evidence
  used weak excerpts rather than command output or a digest-bound artifact.
