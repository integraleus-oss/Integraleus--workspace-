I could not execute anything this session — Bash was denied by the harness ("don't ask mode"), so the test suites and an end‑to‑end policy replay were not run. Everything below is static analysis of the current files plus the committed canary artifacts (`canary-inputs/`, regenerated 22:49 by the reworked builder).

## Per-criterion result

| # | Criterion | Status |
|---|---|---|
| 1 | policy identities/tree/gates/evidence derived from the observed attempt | **Derived, but the blocker it came from is still open** |
| 2 | ignored-file changes detected vs clean baseline | Closed |
| 3 | gate mutations fail closed, no split diff/tree subject | Closed (one residual gap) |
| 4 | empty/duplicate gates fail closed | Closed |
| 5 | schema 1.1 builder path has an integration test | Test exists; the decisive assertion is still missing |
| 6 | Claude gets the sealed path + manifest-bound instructions | Closed at packaging; return-contract wording is wrong |

**2, 3, 4** are genuinely fixed. `_ignored_state` (`trusted_review_builder.py:49-61`) is captured at baseline and re-compared both before (`:166`) and after (`:174`) gates; changed paths, ignored state and the pre-gate tree digest are all re-derived after gates and any difference raises (`:173-175`), so `diff_digest` and `reviewed_tree_digest` cannot describe different trees; `PYTHONDONTWRITEBYTECODE=1` (`:123`) removes the self-inflicted `__pycache__` case; empty and duplicate gate lists raise `BuilderError` (`:159-163`) with tests at `tests/test_trusted_review_builder.py:77-100`. `--no-textconv` and `--no-renames` (`:176`) also close old findings 9 (partly) and 12.

## Blocker — finding 1 is not closed: no builder-produced bundle can yield *any* policy decision

The identities are now derived (`trusted_review_builder.py:236-255`), and the canary proves it: `canary-inputs/policy.json` carries the same `task_id`/`spec_digest`/`run_id` as `binding.json`, real `gate_results`, real `required_evidence`/`evidence_artifacts`, and `expected_subject` == the observed tree. That part of the criterion is met.

But the values the builder mints cannot appear in a schema-valid verdict, so the bundle dies before `POLICY.decide` is ever reached:

- `trusted_review_builder.py:200` sets `subject.gate_run_id_pre = "builder-baseline"` and `gate_run_id_post = run_id`; `:193` sets `run_id = f"{task_id}-attempt-{attempt}"`.
- `review-verdict.schema.json:167-172` types both `gate_run_id_*` as `run_id_or_null`, and `:144-146` types `subject.run_id` as `run_id`, whose pattern is `^run_[0-9A-Za-z._-]{1,64}$` (`:618-621`).
- `validate_review_verdict.py:394-402` requires the verdict's subject to equal **every** manifest subject key, and `REQUIRED_MANIFEST_SUBJECT_KEYS` (`:23-34`) includes `gate_run_id_pre`.

So the reviewer has two options and both fail: copy `"builder-baseline"` → schema failure (`validate_review_verdict.py:758-760`); omit it → `trusted_binding_mismatch` semantic failure (`:762-765`). Either way `contract_valid` is false → `review_projection.py:59-60` raises `ProjectionError` → `local_orchestrator_runner.py:76-85` propagates → `live_review_cycle.py:60-73` records `FAILED_ADMISSION` and re-raises → `managed_one_cycle.py:73-76` returns `ESCALATED`. Every attempt, every time — and unlike the old `run_id` mismatch this one is unconditional: `"builder-baseline"` is a hard-coded constant no packet configuration can fix. The canary manifest shows exactly these values (`canary-inputs/manifest.json`: `"gate_run_id_pre":"builder-baseline"`, `"run_id":"trusted-builder-canary-attempt-1"`), against the working trial's `run_pre_01` / `run_20260811T090000Z` (`…one-cycle/live-provenance-trial/closure-inputs/manifest.json:6,13`).

Same class, same root cause — the builder never validates that what it mints conforms to the reviewer contract: `task_id`/`repo_id` must be slugs `^[a-z0-9][a-z0-9._-]{1,63}$`, and acceptance-criteria ids must match `^AC-[0-9]{1,3}$` (`review-verdict.schema.json:644-646`), while `trusted_review_builder.py:189` accepts any non-empty string and copies it into `manifest.criteria`.

## Major regressions introduced by the fixes

**A. The derived ledger is amnesiac** (`trusted_review_builder.py:240-247`). It is regenerated per attempt with `prior_attempts: []`, `rework_used: 0`, `no_progress_streak: 0`, `finding_registry.findings: []`, `terminal_decision: null`. That makes `_no_progress_transition` (`orchestrator_policy.py:953-965`) structurally unable to trip, `_rework_available` (`:910`) always true, and attempt-1 findings invisible to attempt 2 (`bundle.prior_findings` is `None`). The rework/no-progress budgets are inert; only the controller's hard `max_attempts = 2` bounds the loop. The previous static fixture was at least capable of carrying prior state — the generated one never can.

**B. No post-gate HEAD re-check.** `:153` verifies HEAD before gates, and `:173-175` re-observes paths/tree/ignored afterwards, but not HEAD. Gates execute Codex-authored repo content (`bash scripts/verify.sh`, `python3 -m pytest`) with `git` and `bash` allowlisted, so gate-run code can commit; `git diff <baseline_head>` and the tree digest stay coherent, but `manifest.subject.base_commit`/`head_commit` (`:198`) keep asserting the baseline commit as head. The subject does not split, so criterion 3 as worded holds — the provenance metadata is what goes false.

**C. The appended prompt misstates the return contract** (`production_cycle_cli.py:188-190`): "Return the verdict at the contract path requested by the harness." The harness never names a path and never reads one — `agent_launcher.extract_claude_verdict` parses `envelope["result"]` from the wrapper's JSON stdout (`agent_launcher.py:135-143`), and `claude-review` grants no write tool at all (`Read,Grep,Glob,Bash(git *|rg|sed|cat|wc|find)`). The sealed path and the manifest-bound `review-instructions.md` *are* delivered correctly (`trusted_review_builder.py:256`, sealed at `:264-266`; path injected at `production_cycle_cli.py:186-191`), so criterion 6's substance is met, but this sentence pushes the reviewer toward an unsatisfiable action instead of the JSON-only final message the extractor requires.

**D. Criterion 5's test does not reach the policy.** `tests/test_production_cycle_cli.py:172-219` does build a real 1.1.0 packet over a real git repo and exercises both new branches — good. But `live.side_effect = inspect_bundle` (`:205-215`) replaces `live_review_cycle.run_cycle` wholesale and `admit_live_review` is mocked, so `local_orchestrator_runner.run`, `build_projection`, `validate_document` and `POLICY.decide` are never invoked on builder output. It asserts `policy.run_id == binding.run_id` and matching tree digests — internal coherence, not admissibility. That is precisely the assertion the prior review called critical, and its absence is why the identifier-format blocker survived this rework. No test anywhere constructs a verdict against a builder-produced manifest.

## Minor

- Reviewer-controlled `verdict.json` is written *into* the sealed input directory (`live_review_cycle.py:54-74`, bundle base = sealed dir) and unlinked afterwards; a crash between write and unlink leaves an unsealed file inside the "immutable evidence" dir, which `verify_seal`'s file-set check (`trusted_review_builder.py:302-308`) would then reject on any later verification.
- `_ignored_state` digests every ignored file, three times per cycle, and the full map is embedded in `evidence.json` (`:214`) — expensive and bloating on repos with `node_modules`/`.venv`.
- Non-hashable gate `id` (list/dict) raises `TypeError` from `set(gate_ids)` (`:162`) rather than `BuilderError`; still fail-closed via the controller's generic handler, but off-contract.
- `capture_clean_baseline` is called at `production_cycle_cli.py:153`, outside `run_managed_cycle`'s try, so a dirty worktree surfaces as CLI `ERROR`/exit 2 rather than `ESCALATED`.
- Old findings 8, 10, 11 (basename-only allowlist, unsanitized env, advisory seal, unvalidated numeric config in direct callers) are unchanged — consistent with their non-blocking classification.
- `EVIDENCE.md` still reads "Pending implementation, tests, canary, and independent closure", and the canary's `review-instructions.md` is the closure-review prompt rather than a reviewer-contract instruction document. The "58 integration and 84 core tests remain green" claim remains unverified — I could not run them.

Findings 2, 3, 4 are closed and 6 is substantively closed. Finding 1 is not: the evidence is now correctly derived and then rejected at the reviewer contract instead of at the policy binding, so builder-mode acceptance remains unreachable — and finding 5's test still cannot detect that.

TRUSTED_BUILDER_CLOSURE_REWORK
