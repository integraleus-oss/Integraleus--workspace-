# Evidence

Status: accepted; live three-leg policy chain reached `R17_ACCEPT`

## Scope

- Task packet created before implementation.
- Pre-existing dirty-worktree files remain outside this slice.

## Verification

- Integration suite after current rework: 83/83 passed.
- Accepted core regression suite: 84/84 passed.
- Python compile and `git diff --check`: passed before final review.
- Synthetic builder canary: `CANARY_BUILDER_R2_PASS` before identifier rework;
  builder-generated real projection/policy admission is now covered by an
  automated `R17_ACCEPT` test.
- Independent reviews:
  - initial: `TRUSTED_BUILDER_REWORK`;
  - targeted: `TRUSTED_BUILDER_CLOSURE_REWORK`;
  - final targeted: `TRUSTED_BUILDER_FINAL_REWORK`.

## Closed live chain

- A real two-attempt rework path must preserve the finding registry, perform
  targeted verification, then execute one bounded review-only final-full leg.
- The carried `prior_attempts` record also needs decision digest, outcome, and
  rule id. Current code does not yet supply those fields.
- Fresh `r5` canary proved exactly one format-only Claude retry and no second
  Codex attempt. The retry produced exact JSON, but projection rejected it as
  not contract-valid before policy execution. See `FORMAT_RETRY_CANARY.md`.
- r6 narrowed the mismatch to evidence-kind semantics. r7 then reached strict
  transport validation and failed closed on a decoded `U+000A` in a string.
  It also exposed that criterion plaintext is not present in the sealed packet.
- r10 proved the complete attempt-1 chain through `R11_OPEN_FINDINGS` and a
  policy-authenticated rework packet. Attempt-2 Codex timed out at the hard
  300-second boundary; no second review or acceptance occurred.
- r11 configured a clean repository and a 600-second Codex bound, but did not
  reach attempt 2. The bounded format retry returned exact JSON in an unrelated
  verdict schema; trusted projection rejected it before policy execution. The
  cycle remained fail-closed and no acceptance was inferred.
- r12 proved the sealed schema and first policy leg, and showed that attempt-2
  Codex completes well inside 600 seconds. It also exposed that repeating the
  original conflicting task prose lets it override the authenticated rework.
- r13 removed that authority conflict; attempt 2 correctly produced
  `return left + right`. Targeted review was schema-valid but failed semantic
  admission on canonical prior-findings digest and strong-evidence rules. No
  final-full review or acceptance occurred.
- r14 proved the canonical prior-findings and strong-evidence fixes in the live
  targeted verdict: Claude copied the sealed canonical digest into both required
  fields and supplied command-output evidence for `appears_fixed`. Admission
  still failed closed before policy because the otherwise exact JSON omitted the
  schema-required `conclusion.unable_to_complete_reason` property. The validator
  reported `schema_validation` at `/conclusion`; no final-full review or
  acceptance occurred. This is a bounded contract-format blocker, not a digest,
  authority, latency, or review-substance blocker.
- r15 exposed and closed an ordering defect in contract repair: the generated
  verdict had to be moved outside the sealed input directory before the repeat
  seal check. A regression now requires that invariant.
- r16 proved the repaired live path end to end for targeted verification. The
  initial targeted response required the existing format retry; its exact JSON
  then failed schema validation; one contract-only retry received the exact
  validator report, passed seal checks and admission, resolved the prior finding,
  and produced `R15_NEED_FULL_REVIEW`. No third Codex attempt ran. The review-only
  final-full response also required contract repair, but that one bounded repair
  returned non-exact JSON and was rejected fail-closed before policy. Acceptance
  and commit remain blocked on this final transport edge.
- The final transport edge now has a distinct one-shot
  `contract-repair-format-only` retry. Automated tests prove both exact-JSON
  recovery and a second malformed response failing closed without policy.
- Fresh r17 started from clean baseline `96e821e`. Attempt 1 produced
  `R11_OPEN_FINDINGS`; attempt 2 Codex completed in 47.243 seconds and fixed
  `src/calc.py` to return `left + right`; targeted admission produced
  `R15_NEED_FULL_REVIEW`; the separate review-only final-full leg produced
  `ACCEPTED / R17_ACCEPT`. Its implementation record is
  `SKIPPED_REVIEW_ONLY`, proving no third Codex attempt ran.
- r17's targeted and final-full contract-repair responses were exact JSON, so
  the new transport fallback was not invoked in the accepted live path. Its
  bounded behavior remains covered by focused deterministic tests.

Current verification: integration 83/83, accepted core 84/84, `py_compile` and
`git diff --check` pass.

The implementation, tests, task packet, and evidence were included in one
scoped local commit. No Synology backup, GitHub push, Gateway/config, cron, or
deploy action was performed.
