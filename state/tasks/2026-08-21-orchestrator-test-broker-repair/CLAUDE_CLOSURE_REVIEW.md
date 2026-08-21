I read `CLAUDE_REVIEW.md`, then inspected the current `trusted_test_broker.py`, `trusted_review_builder.py`, `production_cycle_cli.py`, `blind_acceptance.py`, `managed_one_cycle.py`, `agent_launcher.py`, `scripts/codex-local-run.sh`, the tests, and the `DECISIONS.md`/`STATE.md`/`EVIDENCE.md` records.

Note on method: running the suite was denied in this session (`python3 -m unittest` blocked), so every verdict below is from reading code. I confirmed 167 `def test_` methods exist across `tests/*.py`, consistent with the claimed 167/167, but I did not execute them.

Path shorthand: `TSK/` = `state/tasks/2026-08-12-orchestrator-integration/`.

---

## Status of the prior findings

| ID | Verdict | Evidence |
|---|---|---|
| B1 | **Partially closed** — see Major 1 | `TSK/trusted_review_builder.py:197-198` resets before gates; `TSK/blind_acceptance.py:68-69` resets before blind commands; `TSK/production_cycle_cli.py:398,567` pass the dirs on both paths |
| B2 | **Closed (honestly bounded)** | `DECISIONS.md:631` and `STATE.md:320` now both say "The broker is not an OS security boundary… may execute agent-authored tests" |
| M3 | **Closed** | Output is JSON-encoded with `ensure_ascii=True` and labelled `UNTRUSTED_GATE_EVIDENCE_JSON` (`TSK/trusted_test_broker.py:140-146`); the implement prompt adds the counter-instruction at `TSK/production_cycle_cli.py:377-379` |
| M4 | **Closed** | Count mismatch is now `SAFETY_FAILURE` with `repair_packet=None` (`TSK/trusted_test_broker.py:148-152`); `observed_test_count is None` on 0-or-many markers reaches the same branch (`:126`) |
| M5 | **Closed** | `exit_code != 1 → INFRASTRUCTURE_FAILURE` (`:130-137`) catches 124/126/127/137/139/143 and negative codes; `OSError` is caught and typed as 127 (`:112-114`) |
| M6 | **Closed** | Blind acceptance calls `run_sealed_gate` (`TSK/blind_acceptance.py:72-77`), same env/context construction |
| M7 | **Closed** | `run_id = f"run_{task_id}.attempt-{attempt}"` is computed before gates and passed in (`TSK/trusted_review_builder.py:199-203`); `builder_attempt` is no longer forced to 1 |
| M8 | **Partially closed** — see Minor 2 | 1.4.0 happy path + `/tmp` rejection at `TSK/tests/test_production_cycle_cli.py:106-115`; repair path at `:407-455`; broker classification at `TSK/tests/test_trusted_test_broker.py:37-73` |
| m9 | **Closed** | `TSK/production_cycle_cli.py:406-409` seeds `budgets_after.rework_used = 1`, consumed at `TSK/trusted_review_builder.py:313` |
| m10 | **Closed** | Real attempt flows through, so `seen_nonces` (`:504`) and `execution.nonce` (`TSK/trusted_review_builder.py:329`) agree |
| m11 | **Closed** | `review_profile != "standard"` re-raises (`TSK/production_cycle_cli.py:402`); light escalates via `managed_one_cycle.py:98` with `review=None`, giving `policy_or_runtime_escalation` |
| m12 | **Closed** | `fixture_root` is a parameter, `is_dir()`-checked with fallback to root (`TSK/trusted_test_broker.py:100-101`) |
| m13 | **Closed** | Env is a literal allowlist (`:92-103`); no `SSH_AUTH_SOCK`, no `*_API_KEY`, no `GIT_*` |
| n14 | **Closed** | `is_symlink()` now checked pre-resolution (`TSK/production_cycle_cli.py:210-212`) |
| n15 | **Closed** | head+tail split (`TSK/trusted_test_broker.py:39-43`) |
| n16 | **Open (nit)** | `TSK/trusted_test_broker.py:87` still `mkdir(parents=True)` without `exist_ok` |
| n17 | **Closed** | `scripts/codex-local-run.sh:127-131` now enforces existence, non-symlink, and the `/tmp` bound |
| n18 | **Closed** | No test asserts the old string (grepped repo-wide) |

Also confirmed: the operator flow is unchanged — `--review-profile` has a default, `--add-dir` is optional, `main()` gained no required argument (`TSK/production_cycle_cli.py:600-608`).

---

## Major

### Major 1 — The broker's own `HOME` is an agent-writable external root that is never cleared or validated
`TSK/trusted_test_broker.py:90-91,96-97`.

```python
broker_home = Path("/tmp/orchestrator-test-broker-home")
broker_home.mkdir(mode=0o700, parents=True, exist_ok=True)
... "HOME": str(broker_home), "DOTNET_CLI_HOME": str(broker_home),
```

`DECISIONS.md:631` and `STATE.md:320` both state as mandatory architecture: *"Before trusted gates and blind acceptance, agent-writable external artifact roots must be cleared."* This directory is an agent-writable external artifact root and is cleared nowhere. `reset_writable_dirs` is only ever called with `packet["codex_add_dirs"]` (`TSK/trusted_review_builder.py:197-198`, `TSK/blind_acceptance.py:68-69`); a repo-wide grep finds `broker_home` only at these two lines.

Failure scenario: attempt 1's gate runs the agent's own test project (accepted adapter behavior per B2). That agent-authored code writes `$HOME/.nuget/NuGet/NuGet.Config` — or any cache the harness consults — into `/tmp/orchestrator-test-broker-home`. The gate exits 1, a repair is issued, `reset_writable_dirs` clears `codex_add_dirs`, and attempt 2's gate runs against the planted HOME state and reports PASS. This is B1's channel one step removed, and it persists not just across attempts but across every task and run on the machine, which also undercuts the determinism goal the variable pinning exists to serve.

Secondary: the path is fixed and predictable, and `Path.mkdir(exist_ok=True)` succeeds when the target is a pre-existing symlink to a directory (`is_dir()` follows the link), so `HOME` can be redirected outside `/tmp` entirely. `reset_writable_dirs:50` guards exactly this case for `codex_add_dirs`; `broker_home` has no equivalent guard, no `is_symlink()` check, and no `/tmp` bound assertion.

Minimum fix: include `broker_home` in the reset set (or make it run-scoped under an already-reset root), and apply the same symlink/bound validation `reset_writable_dirs` applies to declared dirs.

### Major 2 — `EVIDENCE.md:10` asserts the opposite of what the code does for test-count mismatch
`state/tasks/2026-08-21-orchestrator-test-broker-repair/EVIDENCE.md:10`:

> Exit code 1 and test-count mismatch are typed `IMPLEMENTATION_FAILURE` results with bounded repair evidence.

The code types count mismatch as `SAFETY_FAILURE` with `repair_packet=None` (`TSK/trusted_test_broker.py:148-152`) — which is the correct M4 fix, asserted by `TSK/tests/test_trusted_test_broker.py:50-56`. The evidence file also contradicts its own Review paragraph (`EVIDENCE.md:27`, "conservative failure classification") and omits counts from the non-repairable list at `:11`.

This matters because `EVIDENCE.md` is the artifact being frozen for exactly the check "counts… fail closed". An auditor reading the evidence record concludes the anti-tamper signal is agent-repairable. The code is right; the record is wrong, and the record is the deliverable under review.

---

## Minor

### Minor 1 — The 6000-byte evidence bound is not coordinated with the 8192-byte rework ceiling
`TSK/trusted_test_broker.py:36-44,140-146` → `TSK/managed_one_cycle.py:89`.

`_bounded_failure_text` bounds the *raw* output at 6000 bytes, but the packet delivered to `managed_one_cycle` is that text after `json.dumps(..., ensure_ascii=True)` plus ~310 bytes of prefix, checked against `len(rework_context.encode()) > 8192`. JSON escaping expands `"`/`\`/newline 2× and every non-ASCII BMP character to `\uXXXX` (3 bytes → 6 chars).

Failure scenario: a gate whose assertion messages are in Russian — realistic for this project — produces ~3000 Cyrillic characters in the 6000-byte window, which encode to ~18000 bytes. `managed_one_cycle.py:89-92` then sets `final = "ESCALATED"` and breaks. Fail-closed, so not a safety issue, but the advertised "one bounded repair" silently does not happen, and nothing in `cycle-result.json` records *why* (`terminal_reason` resolves to `policy_or_runtime_escalation` because `len(history) == 1 != max_attempts`). Bound the encoded packet, not the raw text.

### Minor 2 — Key failure paths in the new admission and repair branches remain untested
- No test that a **second** builder gate failure escalates — `TSK/production_cycle_cli.py:402` (`attempt >= 2`) is unexercised.
- No test that `--review-profile light` re-raises instead of synthesizing a repair — the m11 fix at `:402` is unexercised.
- No test that a non-`IMPLEMENTATION_FAILURE` classification propagates terminally through `review()`.
- Of the eight 1.4.0 rejection branches at `:205-216`, only bare `/tmp` is covered (`TSK/tests/test_production_cycle_cli.py:112-115`); non-list, empty, `>4`, non-absolute, symlink, non-dir, and inside-`project_root` are not.
- The 1.4.0 → `foreground_authorized` gate at `:588` is untested; the guard tests at `TSK/tests/test_production_cycle_cli.py:305-320` use the 1.0.0 `setUp` packet, so they never reach it.
- `TSK/tests/test_blind_acceptance.py:69-71` calls `run_blind_acceptance` with `broker_reset_dirs=None` and asserts nothing about broker context or reset — the M6 fix has no direct assertion.
- No test that `_run_loaded_packet` forwards `codex_add_dirs` into `broker_reset_dirs` and into blind acceptance (`:398`, `:567`).

`TSK/tests/test_production_cycle_cli.py:407-455` is the genuinely valuable new test — it proves the repair path end-to-end with `live.call_count == 1` — but it runs on schema 1.1.0, so it touches none of the 1.4.0 surface.

### Minor 3 — `DECISIONS.md:632` records a stale regression count
`DECISIONS.md:632` says "the full 164/164 orchestrator regression suite"; `EVIDENCE.md:17` says 167/167, and the suite currently defines 167 test methods. The frozen decision record understates the verification it cites.

### Minor 4 — `ORCHESTRATOR_ARTIFACT_ROOT` is silently absent for 2–4 declared directories
`TSK/trusted_review_builder.py:200` and `TSK/blind_acceptance.py:76`: `reset_dirs[0] if len(reset_dirs) == 1 else None`. The packet schema admits 1–4 dirs (`TSK/production_cycle_cli.py:205`), but a packet declaring 2 gets no artifact-root variable at all, with no error and no documentation of the restriction. A gate written against the documented variable fails with exit 1 and is classified repairable, burning the repair budget on a packet-shape problem.

---

## Nit

- **n1** — `TSK/trusted_test_broker.py:50`: `path.is_symlink()` is evaluated after `.resolve()` (`:49`) and is therefore always `False`. Same dead-check pattern that n14 fixed in `production_cycle_cli.py`; harmless here because the `/tmp` bound is applied to the resolved path, but it reads as a guard that isn't one.
- **n2** — `TSK/trusted_test_broker.py:87`: `gate_dir.mkdir(parents=True)` still lacks `exist_ok`; n16 is unaddressed. Uniqueness is enforced only by the caller (`TSK/trusted_review_builder.py:187-188`), so a direct caller with duplicate ids gets an untyped `FileExistsError`.
- **n3** — `TSK/tests/test_trusted_test_broker.py:59-62`: the "writable root is reset" case builds its directory under `tempfile.TemporaryDirectory()`, which passes `reset_writable_dirs`' `/tmp` bound only because `TMPDIR` is unset. With `TMPDIR=/var/tmp` the test raises `SAFETY_FAILURE` and fails for an unrelated reason.
- **n4** — `TSK/trusted_test_broker.py:138-152`: the exit-1 branch precedes the count check, so a gate that exits 1 *and* reports a tampered count is classified repairable. It converges to `SAFETY_FAILURE` on the next attempt, so it fails closed, but the ordering is worth an inline note.
- **n5** — `TSK/blind_acceptance.py:74`: `run_id=f"blind-{run_dir.name}"` is always the constant `"blind-blind-acceptance"` — the same shape as the M7 defect. Benign only because the artifact roots are reset immediately before (`:69`) and blind runs once per `run_root`.
- **n6** — `TSK/trusted_test_broker.py:130-137`: `if timed_out or exit_code != 1:` followed by `if exit_code == 0: pass / else: raise` is correct but convoluted; the `timed_out` disjunct is redundant (the handler at `:110` already forces 124) and the empty `pass` branch obscures the intended `exit_code == 0 → continue` rule.

---

## Direct answers to the required checks

| Check | Result |
|---|---|
| External writable roots cleared before builder gates and blind acceptance | **Partial.** Declared `codex_add_dirs` yes (`trusted_review_builder.py:198`, `blind_acceptance.py:69`); the broker's own `HOME` no (Major 1). |
| Minimal env allowlist, no inherited secrets/SSH agent | **Yes.** `trusted_test_broker.py:92-103` is a literal dict; nothing inherits except `PATH`/`LANG`/`LC_ALL` values. |
| Broker described honestly as an execution adapter | **Yes.** `DECISIONS.md:631`, `STATE.md:320`. |
| Gate evidence cannot become authoritative instructions | **Yes.** JSON-escaped, explicitly labelled untrusted at both ends (`trusted_test_broker.py:143-146`, `production_cycle_cli.py:377-379`). |
| Only exit 1 repairable; counts/timeout/signals/missing tools/other exits fail closed | **Yes in code** (`trusted_test_broker.py:112-114,130-152`). **Misstated in `EVIDENCE.md:10`** (Major 2). |
| Blind acceptance uses the same adapter/context | **Yes** (`blind_acceptance.py:72-77`). |
| Run IDs and ledger counters reflect the real attempt and consumed repair | **Yes** (`trusted_review_builder.py:199`, `production_cycle_cli.py:406-409`). |
| Light profile does not synthesize an unavailable repair | **Yes** (`production_cycle_cli.py:402`). |
| Schema 1.4 admission and key failure paths have tests | **Partial** (Minor 2). |
| Operator flow remains PREPARE then RUN | **Yes** (`production_cycle_cli.py:600-608`; `codex-local-run.sh:49-51`). |

---

**REWORK**

Twelve of the fourteen prior findings are genuinely closed, and the two structural ones (B2's honesty, M6's blind-path unification) are closed well. The blocking gap is narrow: the clearing control that closed B1 has a hole at `/tmp/orchestrator-test-broker-home` (Major 1), and the evidence record being frozen states the opposite of the code on one of the checks it is being frozen against (Major 2). Both are small, targeted fixes — add the broker home to the reset/validation set, and correct `EVIDENCE.md:10-11` plus the `164/164` figure at `DECISIONS.md:632`. Minor 2's test gaps are worth closing in the same pass since the repair branch's escalation paths currently have no coverage at all.
