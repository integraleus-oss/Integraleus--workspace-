Verified statically against the three files (Bash was denied, so no test execution — findings below are read-only).

**Criterion 1 — all four accepted REWORK rules have a bounded, policy-derived packet path: closed.**
`managed_policy_review.py:64-83` now branches on directive type rather than only `FIX_FINDINGS`:
- `FIX_FINDINGS` (R11) → `:67-70`, `:77-83`
- `FIX_GATES` (R09) → `:71-72`
- `PROVIDE_EVIDENCE` (R13) → `:73-74`
- `REVIEW_ONLY_FULL` (R15) → `:75-76`

Every line is built from `decision.json` fields (SHA-256-verified against the manifest at `:45-48`) plus the trusted projection — no model prose. The 8192-byte bound at `:87-88` applies to the assembled packet, so it covers all four paths, not just the finding path.

**Criterion 2 — finding IDs resolve against trusted projection: holds.**
`finding_by_id` is built solely from `trusted-review-projection.json` entries with string `finding_id` (`:57-61`); any requested id absent from it raises before a packet exists (`:78-79`). Packet text for findings is drawn from projection fields (`severity`/`message`/`path`), never from the decision.

**Criterion 3 — malformed/unsupported directives fail closed: holds.**
Non-dict directives, unknown types, and `FIX_GATES`/`PROVIDE_EVIDENCE` with non-list payloads all contribute no lines; if nothing survives, `:84-85` raises `ManagedReviewError`, so the controller gets no decision (→ ESCALATED). Nothing degrades to a partial or unverified packet.

**Criterion 4 — regressions cover added paths: holds.**
`tests/test_managed_one_cycle.py:152-172` exercises R09/R13/R15 as separate `subTest` cases, each with its own run directory, freshly computed `decision_digest_file`/`projection_digest`, and an assertion on the derived packet text. R11 remains covered at `:127`, projection-resolution failure at `:144`, digest tamper at `:132`, path escape at `:138`.

Residual nits (same class as those already accepted in R2, not blocking):
- `:72,74` — `", ".join` over a list containing non-strings raises `TypeError`, not `ManagedReviewError`; direction is still fail-closed, but the module's error contract leaks, as with `_read_json`/`_sha256`.
- `:70` — non-string entries inside `finding_ids` are silently dropped rather than rejected; scope narrows (never widens).
- The `if not packet_lines` guard at `:84` has no direct regression (existing tests reach the unprojected-finding raise at `:79` instead), so the newly narrowed "unsupported directive" fail-closed behaviour is asserted only indirectly.

The R2 major is closed.

DIRECTIVE_CLOSURE_PASS
