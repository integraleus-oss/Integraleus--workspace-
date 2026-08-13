I reviewed the builder, the CLI diff, the builder tests, the canary artifacts, and the accepted core contracts (`orchestrator_policy.py`, `validate_review_verdict.py`, `review_projection.py`, `local_orchestrator_runner.py`, `managed_one_cycle.py`). I was not permitted to execute the test suites in this session, so all findings are from static analysis plus the committed canary artifacts.

## What holds up

Real strengths, and they are not small: the change set is genuinely observation-driven inside its own boundary. Baseline cleanliness + pinned HEAD (`trusted_review_builder.py:49-56`, `:137-138`) makes the diff provably Codex's. Scope validation uses path-component matching rather than string prefixes (`:76`) so `srcevil/` cannot masquerade as `src/`. Gate failure, timeout, non-allowlisted program, out-of-scope path, symlink, missing input, and pre-existing output dir all raise before any review input is finalized. `verify_seal` re-derives the tree digest against the live repo (`:232-235`), and `run_managed_cycle` converts any `BuilderError` into `ESCALATED` (`managed_one_cycle.py:73-76`), so the failure direction is correct throughout. The builder's `binding.json` key set exactly matches what `review_projection.build_projection` demands, and the manifest subject exactly matches `REQUIRED_MANIFEST_SUBJECT_KEYS`. That is careful work.

The problems are at the seam, not in the builder's interior.

## Blocking

**1. The built evidence is never bound to the policy decision; builder-mode acceptance is structurally unreachable.** `trusted_review_builder.py:193`, `:197-200`; `production_cycle_cli.py:174-179`

`policy.json` is copied verbatim from the packet's static `policy_fixture`, and `local_orchestrator_runner.run` feeds that fixture's `task_policy`/`ledger`/`execution_report` into `POLICY.decide` alongside the projection derived from the builder's real binding. `orchestrator_policy._binding_errors` (`:868-881`) requires `task_id`, `spec_digest`, `run_id` to be identical across all four documents, plus matching `attempt_epoch`.

The canary demonstrates the mismatch directly: `canary-inputs/binding.json` carries `task_id: trusted-builder-canary`, `run_id: trusted-builder-canary-attempt-1`, `spec_digest: sha256:58fd…`, while `canary-inputs/policy.json` carries `task-2026-08-11-state-machine`, `run-001`, `sha256:aaaa…`. That bundle yields `R01_BINDING` → `ESCALATED`. Every attempt, every time.

Hand-tuning the fixture does not rescue it. `_final_full_ok` (`orchestrator_policy.py:1122-1130`) gates `R17_ACCEPT` on `reviewed_tree_digest == execution_report.subject.tree_digest`. The real tree digest is only knowable after Codex runs, so a static fixture cannot contain it. One fixture is also reused for both legs while `run_id` and `attempt_epoch` differ per attempt. Separately, the gate results and evidence the builder actually observed never populate `execution_report.gate_results` / `evidence_artifacts` — the policy still evaluates `mandatory_gates` and `required_evidence` against declared prose. The spec goal "safely connects them to production CLI" is not met: observed evidence is built, sealed, and then discarded at the decision boundary.

**2. Gitignored changes are invisible to every check.** `trusted_review_builder.py:46`, `:60-62`

`_status` uses `--untracked-files=all` without `--ignored`, and `_changed_paths` uses `ls-files --others --exclude-standard`. Any path matching the repo's `.gitignore` is absent from baseline cleanliness, changed paths, scope validation, the diff, and the tree digest — while still being present on disk when gates execute and afterwards. A repo ignoring `build/`, `*.log`, `.env`, or `__pycache__/` gives Codex an unobserved write channel. This defeats the packet's first acceptance criterion.

**3. Gate side effects mutate the subject after the diff is captured.** `trusted_review_builder.py:144-163`

Order is: paths collected → scope validated → diff written → gates run → `tree_digest` computed. So `reviewed_tree_digest` describes the post-gate tree while `diff_digest` and `changed-paths.json` describe the pre-gate tree, and anything a gate creates or modifies is never scope-checked or re-observed.

This is not hypothetical: the gate shipped in the builder's own test fixture, `python3 -m py_compile src/app.py` (`tests/test_trusted_review_builder.py:29`), writes `src/__pycache__/*.pyc` into the repo. On attempt 2 those artifacts surface as changed paths, get appended to the diff as raw binary, and hard-fail the cycle if `allowed_paths` does not happen to cover them.

**4. An empty gate list passes silently.** `trusted_review_builder.py:154`; `production_cycle_cli.py:131-136`

`config["gates"]` is never checked for type or emptiness in either layer. `"gates": []` produces `evidence["gates"] = []` and a fully sealed, apparently-valid packet with zero executed gates — directly contradicting "Every required gate must run, return zero." Gate ids are also not checked for uniqueness; a duplicate id escapes as `FileExistsError` from `gate_dir.mkdir(parents=True)` (`:116`) rather than a `BuilderError`.

**5. The new integration path has no test at all.** `tests/test_production_cycle_cli.py`

Twelve tests, none constructing a `1.1.0` packet. The new `load_packet` branch (`production_cycle_cli.py:128-140`) and the new builder branch of `review()` (`:174-179`) are entirely uncovered; every existing test uses legacy `1.0.0` packets. Critically, nothing asserts that a builder-produced bundle is acceptable to `local_orchestrator_runner.run` — the single test that would have caught finding 1. The builder unit tests themselves are good (tamper, scope, dirty baseline, HEAD change, gate failure all covered), but they stop at the builder's edge.

**6. Review instructions are digested but never delivered, and the prompt sent is a different file.** `trusted_review_builder.py:155`, `:175`; `production_cycle_cli.py:129`, `:140`, `:186-188`

`manifest.review_instructions_digest` binds `builder.review_instructions`, but that file is never copied into the sealed directory, and the prompt Claude actually receives is `packet.review_prompt` — a different document. `validate_review_verdict.py:405-413` requires the verdict's `review.inputs_digest.review_instructions_digest` to equal the manifest value, which the reviewer has no way to compute from what it was given. Compounding this, the static prompt cannot name the per-attempt input directory (`run_dir/review-inputs`), and Claude is launched with `cwd=project_root` — so the sealed inputs are plausibly never read by the reviewer at all.

## Non-blocking

**7. `observed.diff` is a mixed format and an unlabelled injection channel.** `trusted_review_builder.py:146-152` — a real `git diff` is concatenated with `path\0<raw bytes>\0` records for untracked files. New-file content is not valid diff syntax, and it is Codex-controlled text placed in a reviewer-facing artifact with no delimiter, so it can carry fabricated `diff --git` headers or reviewer instructions.

**8. Gate allowlist is basename-only; environment is unsanitized.** `trusted_review_builder.py:104` — `Path(argv[0]).name` accepts `/tmp/x/python3` or `./python3` (resolved against `cwd=root`, which Codex can write). `subprocess.run(argv, cwd=root)` (`:108`) inherits the full parent environment. With `bash` on the list the allowlist is largely advisory regardless. Gate stdout/stderr is also uncapped — buffered in memory and written unbounded into the sealed dir.

**9. Git invocations are not hardened against repo-controlled config.** `trusted_review_builder.py:35`, `:146` — `--no-ext-diff` is set but `--no-textconv` is not, and `.gitattributes` plus a repo-local `diff.<driver>.textconv` is an execution path while observing a tree Codex just wrote. Suggest `-c core.attributesFile=/dev/null -c core.hooksPath=/dev/null --no-textconv` and an explicit `GIT_*` env scrub.

**10. Seal integrity is advisory, not tamper-proof.** `trusted_review_builder.py:204-206`, `:218-221` — `chmod 0o444` covers files only; directories stay writable and the owning user can re-chmod (the tests do exactly that at `tests/test_trusted_review_builder.py:76,84`). `verify_seal` iterates only keys already in the seal, so *added* files go undetected, `gates/*/result.json` is never digest-checked, and nothing authenticates `seal.json` itself. Sound as a corruption detector; should not be documented as immutable evidence.

**11. Builder does not re-validate its own numeric config.** `gate_timeout_seconds` is range-checked only in the CLI (`production_cycle_cli.py:135`) and passed straight to `subprocess.run(timeout=…)` (`trusted_review_builder.py:108`); a direct caller passing `None` gets an unbounded gate. Non-string `allowed_paths` entries raise `TypeError` from `PurePosixPath` (`:69`) rather than `BuilderError`.

**12. Rename edge case.** `git diff --name-only` with default rename detection reports the destination only, so a rename moving a file *out of* an allowed prefix can leave the deleted source unobserved. Consider `--no-renames`.

**13. Task-packet state is inconsistent with the slice.** `TASK_PACKET.md` checklist items 2–10 are unchecked and `EVIDENCE.md` still reads "Pending implementation, tests, canary, and independent closure." `canary-inputs/` holds builder artifacts only — no end-to-end production-cycle run and no policy decision, which is precisely why finding 1 went unnoticed. The "58 integration and 84 core tests remain green" criterion has no recorded result, and I could not run the suites to confirm or refute it.

## Assessment

The builder does what its own docstring claims: it derives manifest, binding, evidence, and bundle from observed Git state and real gate executions, and it fails closed on the cases it knows about. But the packet's spec axis asks for two things, and the second one — connecting that observed evidence to the production CLI — is where it comes apart. The decision the CLI ultimately makes is still computed from static packet prose, and the binding identities guarantee `R01_BINDING` on every builder-mode attempt. Findings 2, 3, and 4 each independently breach a stated acceptance criterion about observation completeness and gate enforcement. Finding 5 explains how findings 1 and 6 survived to review.

TRUSTED_BUILDER_REWORK
