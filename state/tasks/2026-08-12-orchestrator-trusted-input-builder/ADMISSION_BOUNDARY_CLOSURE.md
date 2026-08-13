## Scope and result

I traced the B1 fix statically across the five files plus `agent_launcher.py`, `local_orchestrator_runner.py`, `managed_one_cycle.py` and the wrapper at `/home/stanislav/agent-runs/_bin/claude-review`. No files edited. Tests were not run (Bash execution denied this session), so all statements below are from reading the current tree.

**The three literal checks you asked for all pass.** One blocker survives underneath them.

### Ordering — confirmed correct

`live_review_cycle.run_cycle` (`live_review_cycle.py:20-66`):

1. `:33` launch Claude, `:37-46` early-return `FAILED_LAUNCH` (callback correctly not reached, no admission).
2. `:48-49` `pre_admission_verify()`.
3. `:51` `POLICY.parse_json_file(bundle_path)` — the **first** read of any sealed artifact after the launch.
4. `:65` verdict materialization, `:66` `local_orchestrator_runner.run` (which re-reads `policy.json`, `manifest.json`, `binding.json`, `prior-findings.json` at `local_orchestrator_runner.py:57-70`).

The callback is strictly before the bundle read, the verdict write, and the policy run. A raise at `:49` propagates out of `run_cycle` — no verdict file, no `policy-runs/` — and lands in `run_managed_cycle`'s handler (`managed_one_cycle.py:86-89`) as `ESCALATED`. Fail-closed. Covered by `test_live_review_cycle.py:86-102`.

The verdict is written *after* the verify, so `verify_seal`'s file-set check (`trusted_review_builder.py:337-343`) doesn't spuriously reject it — the exclusion the review's fix direction called for isn't needed, and `:61-62` independently rejects a pre-existing verdict file.

### Legacy compatibility — confirmed

`pre_admission_verify` is keyword-only with a `None` default; legacy packets pass `None` (`production_cycle_cli.py:209-210` ternary on `packet["builder"]`, which `load_packet:150-158` sets to `None` for schema `1.0.0`). All pre-existing `run_cycle` call sites (`live_review_cycle.py:100`, `test_live_review_cycle.py:45/58/69/81/118`) are unchanged 4-positional calls. No behavioral change on the legacy path.

### Callback skippability in builder mode — adequately closed

Single call site; `packet["builder"]` is validated to be a non-empty dict (`production_cycle_cli.py:142-143`), so it cannot be falsy in builder mode, and the same expression gates both the build (`:185`) and the callback (`:210`). `test_production_cycle_cli.py:214-215` asserts the callback is non-`None` and invokes the real `verify_seal` against real built inputs and a real repo.

---

## Blocker

**B-1 (carried) — `seal.json` is its own root of trust and lives in the reviewer-writable directory, so the re-verification is bypassable by the exact actor B1 postulated.**

`build_review_inputs` computes `seal = {name: digest …}` over eight/nine artifacts and writes it to `out/seal.json` (`trusted_review_builder.py:297-302`). `seal.json` is not in its own digest map, and no digest of it is retained anywhere outside that directory. `build_review_inputs` returns `{"input_dir", "bundle", "seal"}` (`:306`) — `production_cycle_cli.py:190` consumes only the first two; **`built["seal"]` is never read**. `verify_seal` (`:309-320`) re-reads `seal.json` from disk and validates everything against it.

Consequence: `verify_seal` proves only that the directory is *internally consistent with whatever `seal.json` currently says*. B1's own premise — files are `0o444` inside a `0o755` same-UID directory, so unlink/rename succeeds — applies to `seal.json` identically. The wrapper allowlist is unchanged (`claude-review:88`: `Bash(sed *)`, `Bash(find *)`, `Bash(git *)`, `Bash(python3 -m unittest *)`, `Bash(bash scripts/verify.sh)`), giving arbitrary write and arbitrary code execution as the same user, and `production_cycle_cli.py:200-202` hands the reviewer the sealed directory path in the prompt.

Failure scenario (unchanged from B1, one extra step): the reviewer rewrites `manifest.json`'s `subject`/`expected_review_mode` and `policy.json`'s `ledger` (`counters.final_full_used`, `finding_registry.findings`, `seen_nonces`), rewrites `evidence.json`'s `reviewed_tree_digest`/`changed_paths` to match the tree it also controls, recomputes the eight SHA-256 values and rewrites `seal.json`. `verify_seal` at `:49` passes on all three legs — digest loop, gate-evidence loop, file-set equality, and the `project_root` tree recheck (`:344-347`). `build_projection` validates against the mutated manifest, `decide()` reads the mutated ledger, `R17_ACCEPT`. Acceptance focus #1, #4 and #5 still fail on this path, with no capability the reviewer didn't already need for the pre-fix attack.

The fix is small and the material is already in hand: capture `_sha256(built["seal"])` in `review()` before the launch and assert it inside the callback before delegating to `verify_seal` (an in-process anchor is the only defense that works against a same-UID adversary — directory permissions do not, since the owner can chmod them back). Materializing the verdict outside the sealed directory, as B1's fix direction also suggested, is the complementary structural change: today the verdict lands in `bundle_base` (`live_review_cycle.py:57-63`), which forces that directory to stay writable.

I am not treating the literal wording of your three checks as failed — they pass. I am flagging that the security property they were meant to establish does not yet hold.

## Non-blocking residuals

- **Tamper detection leaves no cycle artifact.** `:48-49` sits outside the `try` at `:64`, so a seal mismatch writes no `cycle-result.json` — unlike the invalid-verdict path, which records `FAILED_ADMISSION` (`:69-76`). The only trace of a tampering event is the exception string in `managed_one_cycle` history. Fail-closed behavior is intact; forensics is weaker for the more serious event.
- **TOCTOU window between verify and read.** `verify_seal` digests the files at `:49`; `local_orchestrator_runner.run` re-opens them via `shutil.copyfile` at `:66`. `agent_launcher.launch` uses `start_new_session` but only calls `killpg` on the timeout path (`agent_launcher.py:79-84`), so a daemonized child surviving a clean exit is not reaped. Narrow, but non-zero. Snapshotting bytes at verify time and running the policy over the snapshot would close it.
- **`test_post_review_verifier_runs_before_verdict_or_policy` does not pin the callback *after* the launch.** The stub raises immediately, so every assertion (`verified == [True]`, no verdict, no `policy-runs/`) would also hold if the callback were invoked before `agent_launcher.launch`. Asserting `cycle/claude-launch/launch-result.json` exists would pin the real ordering.
- **No end-to-end tamper test through the CLI.** `test_production_cycle_cli.py:205-216` invokes the real `verify_seal` only on the happy path; the tamper cases live in `test_trusted_review_builder.py:104-122` against `verify_seal` directly. Nothing drives a mutated sealed directory through `production_cycle_cli` → `run_cycle` → admission. This is M2's pattern from the prior review, still present on the new code path.
- **No structural enforcement inside `run_cycle`.** Builder mode is enforced solely by the caller's ternary. A future refactor that drops the argument fails only `test_production_cycle_cli.py:214`. Passing a mode marker, or having `run_cycle` refuse to proceed when `bundle_path.parent/"seal.json"` exists and no verifier was supplied, would make the omission structurally impossible.

M1 and M3 from `FINAL_FULL_REVIEW.md` are outside this closure's scope and were not re-examined; `EVIDENCE.md`/`TASK_PACKET.md` still describe a superseded state as far as I can tell.

ADMISSION_BOUNDARY_CLOSURE_REWORK
