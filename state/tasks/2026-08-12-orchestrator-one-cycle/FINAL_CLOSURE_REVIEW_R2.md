## Findings

**Blocker:** none.

**Major — REWORK packet derivation covers only `FIX_FINDINGS`**
`managed_policy_review.py:56-69` builds `requested_ids` exclusively from directives of type `FIX_FINDINGS` and raises when the list is empty. But `RULE_OUTCOMES` (`managed_one_cycle.py:19-22`) maps four other rules to `REWORK`: `R09_GATE_FAIL`, `R13_EVIDENCE`, `R15_NEED_FULL_REVIEW` (plus `R11`). If the policy engine emits any of those with a non-`FIX_FINDINGS` directive (e.g. rerun-gates / run-full-review), admission raises `ManagedReviewError` and the legitimate bounded rework cannot be handed to the controller at all. It fails **closed** (no decision → ESCALATED), which is a permitted terminal state, so it doesn't break the authority model — but only the `R11` path is implemented and tested (`tests/test_managed_one_cycle.py:127`), and the live trial exercised only `R11`.

**Nits**
- `managed_policy_review.py:43,50-51`: `_read_json`/`_sha256` on a missing or non-JSON `run-result.json` / `decision.json` / `trusted-review-projection.json` raise `FileNotFoundError`/`JSONDecodeError`, not `ManagedReviewError`. Direction is still fail-closed (the controller's `except Exception` at `managed_one_cycle.py:73` converts it to ESCALATED), but the module's declared error contract leaks.
- `managed_policy_review.py:36`: `decision_dir` is resolved against the process CWD, and the durable artifacts store it relative (`"state/tasks/.../policy-runs/managed-live-provenance-r1"`). Admission is therefore only replayable from the workspace root; from elsewhere it rejects (safe, but not self-describing).
- `managed_policy_review.py:68`: duplicate `finding_ids` across directives are not de-duplicated — repeated lines in the packet, harmless.
- `managed_one_cycle.py:41-43`: single-use `root.exists()` check is TOCTOU-racy; irrelevant for the serialized local runner.
- Input digests inside the manifest (`policy_fixture`, `projection_binding`, `review_verdict`, `trusted_manifest`) are not re-verified against the `input-*.json` files that sit beside `run-result.json`. Adds nothing against a writer who controls the directory, but would catch runner bugs cheaply.

## Checked items

**Deterministic outcome authority — holds.** Outcome comes from the `rule_id → outcome` table only; a verdict lacking `document_type == "local_orchestrator_run_result"` yields `rule_id = None` → `ESCALATED`, an unknown rule defaults to `ESCALATED`, and a self-reported `outcome` disagreeing with the table's forces `ESCALATED` (`managed_one_cycle.py:57-60`). Second-attempt `REWORK` is rewritten to `ESCALATED` in both the final status and the history record (`:69-72`). Budget is pinned at exactly two attempts (`:38-39`).

**Digest/path fail-closed admission — holds.** Admission requires `DECIDED` + manifest shape, requires `decision_dir` to resolve inside the resolved cycle root and be a real directory (symlink escape closed by `resolve()`), requires `run-result.json` to parse equal to the manifest, and requires both `decision.json` and `trusted-review-projection.json` SHA-256s to match the manifest, then re-checks `outcome`/`rule_id` against the decision itself. Every failure raises rather than degrading.

**REWORK packet derivation — holds for the implemented path.** IDs are taken from the decision's directives, every one must resolve in the trusted projection, the packet text is built from projection fields (not model prose), and it is bounded at 8192 bytes — with the controller independently re-checking type/emptiness/size before reuse.

**Fresh live REWORK admitted.** `review-1/cycle-result.json`: `DECIDED`, `R11_OPEN_FINDINGS` → `REWORK`, from a real read-only `claude-review` launch (exit 0, 48.1 s, distinct prompt digest). `review-1/admitted-review.json` carries the derived packet `fnd_b5ea59e6… [blocker]: Validator reports success for invalid review (src/reviewer_contract.py)`, and the run directory holds the full artifact set (`run-result.json`, `decision.json`, `trusted-review-projection.json`, five read-only `input-*.json`).

**Subject-bound fresh ACCEPTED admitted.** `honest-closure-review-r2/cycle-result.json`: `DECIDED`, `R17_ACCEPT` → `ACCEPTED`, from its own 41.9 s launch with a different prompt digest, and with all four `input_digests` plus `projection_digest`, `decision_digest_file`, and `run_bundle_digest` distinct from review-1's — i.e. bound to the post-fix closure subject, not a relabelled copy of the earlier run. `admitted-review.json` is the manifest verbatim with no `rework_packet`, as expected for a non-REWORK outcome.

**Two malformed closure responses produced no policy decision.** `review-2` and `honest-closure-review` both record `status: FAILED_ADMISSION`, `decision: null`, `LaunchError: Claude result does not contain exact JSON`, on distinct prompt/stdout digests. Neither directory contains a `policy-runs/` tree or an `admitted-review.json` — the failure happened before any policy evaluation, so no decision artifact exists to admit.

ONE_CYCLE_CLOSURE_PASS
