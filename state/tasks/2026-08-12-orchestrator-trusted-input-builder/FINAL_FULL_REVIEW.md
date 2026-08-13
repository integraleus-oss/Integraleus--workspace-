I traced the full slice against the accepted core (`orchestrator_policy.py`, `validate_review_verdict.py`, `review-verdict.schema.json`, `review_projection.py`) and the launcher/wrapper chain.

## Verification method

Bash and test execution were denied in this session (don't-ask mode), so the suites were **not run**. Test counts (`58`/`69` integration, `84` core) are treated as independently reported and remain unverified here. Everything below is static tracing of the current working tree, including files outside the nominal diff that the slice depends on (`live_review_cycle.py`, `agent_launcher.py`, `/home/stanislav/agent-runs/_bin/claude-review`).

## Confirmed closed (independently re-traced)

| Prior finding | Result |
|---|---|
| S1 — attempt-2 coverage scope contradiction | **Closed.** `trusted_review_builder.py:216` derives `expected_coverage_scope` from `review_mode`. Reconciles the schema `allOf` targeted branch (`review-verdict.schema.json:489-530`, `coverage_scope` const `targeted`) with the validator's semantic binding (`validate_review_verdict.py:422-426`). The `initial_full` branch (`:458-487`) keeps `full`. Both now satisfiable. |
| S2 — first-attempt `R15` burned a Codex rework | **Closed.** `managed_one_cycle.py:62-74` precedes the rework branch at `:75`; `implement` is never called on the final leg; any `REWORK` there is forced to `ESCALATED` (`:69-70`). |
| S3 — unauthenticated registry hop | **Closed.** `production_cycle_cli.py:216-217` binds `registry-after.json` to both `manifest.registry_digest_file` and `decision.registry_digest_after`. Canonicalization matches `orchestrator_policy.py:73-78` byte-for-byte, and both `merge_finding_registry` call sites (`orchestrator_policy.py:1224`, `local_orchestrator_runner.py:84-87`) receive identical arguments, so the check cannot spuriously fire. |
| Blocker 1 — schema-invalid `prior_attempts` | **Closed.** All five fields in `allowed_attempt` (`_validate_ledger:665-681`) are present, epochs unique and non-negative, both digests `sha256:`-formed. |
| Lifecycle #3, no third Codex attempt | **Confirmed.** Both paths reach `review(max_attempts + 1)` with at most two `implement` calls. |

Also confirmed sound: Git-observed provenance (Codex prose cannot declare paths or gate results); the post-gate recheck now covering HEAD, path set, ignored state and tree digest (`:180-183`); prior-findings bidirectional digest binding (`validate_review_verdict.py:488-494`) plus sealing (`:300-301`); no reset of counters, nonces, registry, or prior decisions (`:254-268`, `production_cycle_cli.py:219-232`).

---

## Blocker

### B1 (Spec) — the seal is never re-verified between the Claude launch and policy admission; the reviewer has write capability

`production_cycle_cli.py:189` is the **only** `verify_seal` call, and it runs *before* `live_review_cycle.run_cycle` (`:206`). Inside that call the order is: launch Claude (`live_review_cycle.py:32`) → extract verdict (`:61`) → `local_orchestrator_runner.run(bundle_path, …)` (`:62`), which re-reads `manifest.json`, `binding.json`, `policy.json` and `prior-findings.json` from the same directory. Nothing checks integrity in between.

The seal is advisory: `trusted_review_builder.py:303-305` chmods files `0o444` but leaves the containing directory `0o755`, same UID — unlink/rename over any file succeeds.

And the reviewer is not read-only. `/home/stanislav/agent-runs/_bin/claude-review:88` allowlists `Bash(sed *)`, `Bash(find *)`, `Bash(git *)`, `Bash(python3 -m unittest *)`, `Bash(bash scripts/verify.sh)`. `sed -i` rewrites a `0o444` file via directory rename; `python3 -m unittest <target>` imports and executes Codex-authored code from the repo under review; `bash scripts/verify.sh` executes a repo-controlled script verbatim. `agent_launcher.py:111` records `"sandbox": "read-only"` for the claude role but enforces nothing — the label is not backed by the wrapper.

**Failure scenario.** Attempt 1 Codex output contains injected instructions in a file the reviewer reads. The reviewer (or code it executes) rewrites `manifest.json`'s `subject`, `expected_review_mode` and `expected_coverage_scope`, and `policy.json`'s ledger — `counters.final_full_used`, `finding_registry.findings`, `seen_nonces`, `prior_attempts` — then emits a verdict consistent with the mutated manifest. `build_projection` validates against the mutated manifest, `decide()` evaluates the mutated ledger, and the cycle returns `R17_ACCEPT`. Every downstream cross-check agrees, because `decision_digest_file`, `projection_digest`, `registry_digest_file` and the new S3 check are all computed *over the tampered inputs*. Acceptance focus #1, #4 and #5 all fail on this path.

**Scope caveat, stated fairly.** `TASK_PACKET.md:66-67` scopes the criterion to "stops **before** Claude review", and the wrapper is listed at `:23` as a fixed allowed input. On a literal reading of that one bullet the current behaviour conforms. I still count it blocking because the packet Goal (`:12-14`) explicitly says inputs must fail closed "before Claude review **or policy admission**", this review's charter names provenance-binding and mutated-input fail-closed as acceptance conditions, and the enforcement mechanism already exists — `verify_seal` is simply not wired to the admission boundary. If the wrapper were genuinely read-only this would drop to major.

**Fix direction.** Call `verify_seal` in `live_review_cycle.run_cycle` immediately before `local_orchestrator_runner.run`, with the generated verdict excluded from the expected file set (`verify_seal:337-343` would otherwise reject it). Materialising the verdict outside the sealed directory would be cleaner still.

---

## Major

### M1 (Spec) — the review-only final-full leg can be blocked by the earlier review leg's own permitted tool use

Attempt 3 rebuilds from the live worktree and compares ignored-file state against the *original* baseline (`trusted_review_builder.py:173-174`). Any side effect of the attempt-1 or attempt-2 review — `__pycache__` from the allowlisted `python3 -m unittest`, a scratch file from `scripts/verify.sh` — makes the final leg raise `BuilderError("ignored files changed since baseline capture")`, or `"changed path is outside allowed scope"` at `:93` if the artefact is not gitignored. `PYTHONDONTWRITEBYTECODE=1` is set only for gates (`:124`), not for the agent launches.

Fail-closed, so not unsafe — but acceptance focus #3's primary lifecycle (correct first attempt → review-only final-full → `R17_ACCEPT`) is contingent on the reviewer touching nothing, and no test covers two builder invocations separated by a real review.

### M2 (Standards) — the added code paths are not reached by any test

Read directly, not inferred:

- `test_production_cycle_cli.py:216-217` mocks `admit_live_review` to return `ACCEPTED`/`R17` on attempt 1, so `production_cycle_cli.py:211-232` — the entire carry block including the new S3 digest check — never executes. The `R17` assertion at `:219` is the mock's own return value.
- `test_trusted_review_builder.py:164-203` asserts only on generated JSON shape from hand-authored `prior_context`; no test drives an attempt-2 targeted verdict through `validate_document` → `build_projection` → `decide`, which is exactly where S1 hid.
- `test_builder_bundle_reaches_policy_acceptance…:133-162` is the one genuine end-to-end assertion, but it uses `attempt=3, prior_context=None` — the carried-state attempt 3 is not the one exercised.
- `test_managed_one_cycle.py:51-79` does prove both leg orderings (`implemented == [1, 2]` and `implemented == [1]`), but with stub verdicts.

Net: acceptance focus #3 is demonstrated at the controller level with stubs and by static tracing only. This is the same gap that hid all three previously-found blockers — each was caught by review, none by test.

### M3 (Spec) — closure documentation contradicts the code

- `EVIDENCE.md:3` reads "rework required; not ready to commit"; `:23-28` still lists the `prior_attempts` blocker as open, which is closed.
- `TASK_PACKET.md:42-43` records `TRUSTED_BUILDER_FINAL_REWORK` and `:47-54` describes the missing third leg as the current blocker — also closed.
- `TASK_PACKET.md:68` claims "58 integration" tests; `EVIDENCE.md:12` says 69. Neither is verifiable here.
- `canary-inputs/policy.json` carries `run_id: "trusted-builder-canary-attempt-1"` — the pre-`run_`-prefix format the builder no longer mints (`trusted_review_builder.py:204`) and which the reviewer schema would now reject. Checklist item 7 ("Run isolated builder canary", marked `[x]`) is backed by superseded artefacts, as `EVIDENCE.md:15` itself concedes.
- `FINAL_FULL_REVIEW.md` is zero bytes.

---

## Minor (Standards, all carried forward)

- **St1** — the `prior_attempts` carry is implemented twice (`trusted_review_builder.py:257-259`, `production_cycle_cli.py:219-221`) and must stay in lockstep; a duplicate epoch trips `duplicate_prior_attempt_epoch` → `R01_BINDING` with no local diagnostic. On the attempt-1-`R15` skip path the attempt-1 decision is recorded as `attempt_epoch: 2` — an epoch that never occurred. Passes `_validate_ledger:668-674`; the only consumer, `_latest_prior_attempt:946-950`, is unreachable on the accept path and strictly more conservative where it is reachable.
- **St2** — `local_orchestrator_runner.py:84-87` recomputes the registry after `decide()` and before the invariant check at `:88`, indexing `fixture["execution_report"]["subject"]["tree_digest"]` raw. A malformed report that `decide()` would return as a clean `R01_BINDING` instead raises `KeyError` → `local_orchestrator_run_error`.
- **St3** — `production_cycle_cli.py:149` fabricates `[{prompt_text}] * 3`; in legacy mode an `R15` reaches `packet["reviews"][2]` → bare `IndexError` rather than a named `PacketError`.
- **St4** — `trusted_review_builder.py:259` (`**previous["last_decision"]`) and `:283` (`.get("finding_registry", {}).get(…)`) raise `TypeError`/`AttributeError` on malformed carried context instead of `BuilderError`.
- **St5** — `capture_clean_baseline` sits outside `run_managed_cycle`'s try (`production_cycle_cli.py:163`), so a dirty worktree surfaces as `ERROR`/exit 2; basename-only gate program allowlist (`trusted_review_builder.py:120`); gate env is full `os.environ` plus one variable (`:124`); gate stdout/stderr captured unbounded into memory.
- **New nits** — `observed.diff` appends untracked file contents as raw NUL-delimited bytes after the real diff (`:185-190`), so a new file's content is not in valid diff form; `:188` uses `not …returncode == 0` where `!= 0` is meant.

---

## Assessment against the five acceptance points

1. **Provenance-bound and fail-closed** — holds up to the review boundary; **fails at the admission boundary** (B1).
2. **Generated inputs reach validation → projection → policy → admission** — yes, traced end-to-end; the one automated proof (`test_trusted_review_builder.py:133-162`) covers the uncarried attempt-3 case only.
3. **Both lifecycles, no third Codex attempt** — structurally correct and proven with stubs; not proven through the real policy (M2), and lifecycle 1 is environmentally fragile (M1).
4. **No reset, nothing unauthenticated** — nothing is reset; the registry hop is now authenticated (S3 closed). Undermined by B1, which lets the ledger itself be rewritten before `decide()` reads it.
5. **Unknown / malformed / stale / mutated / out-of-scope / exhausted stop closed** — yes for every case reachable through the builder's own inputs; **no** for post-seal mutation (B1).

B1 is the only finding I would not sign off on. M1–M3 are each independently sufficient to hold closure: the primary lifecycle is untested end-to-end, and the packet and evidence files still describe a superseded state.

TRUSTED_BUILDER_FINAL_FULL_REWORK
