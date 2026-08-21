I read the closure review, then the current broker, its tests, and the two records. Bash was denied for running the suite (`python3 -m unittest`) and for shell loops, so every verdict below is from reading code plus file-level greps — I flag where that limits me.

Path shorthand: `TSK/` = `state/tasks/2026-08-12-orchestrator-integration/`, `REP/` = `state/tasks/2026-08-21-orchestrator-test-broker-repair/`.

---

## Status of the two Major findings

**Major 1 — broker `HOME` never cleared or validated → CLOSED.**
`TSK/trusted_test_broker.py:94-96` now runs `reset_writable_dirs([broker_home])` followed by `chmod(0o700)` inside `run_sealed_gate`, before the env dict is built and before `subprocess.run` (`:111`). Because the reset lives in `run_sealed_gate` rather than the caller, it fires for **every** gate on **both** paths — builder (`TSK/trusted_review_builder.py:202-203`, one call per gate) and blind acceptance (`TSK/blind_acceptance.py:72`). The validation is real, not the dead check the prior review flagged as n1: `reset_writable_dirs:50` now tests `raw_path.is_symlink()` *before* `.resolve()` (`:53`), and `:54` rejects both `/tmp` itself and anything outside `/tmp`. A pre-existing symlink at the fixed path therefore raises `SAFETY_FAILURE` with `repair_packet=None` instead of redirecting `HOME`. The child-deletion loop (`:58-62`) correctly unlinks symlinked directories rather than recursing through them.

**Major 2 — `EVIDENCE.md:10` contradicted the code → CLOSED.**
`REP/EVIDENCE.md:10` now reads "Exit code 1 is typed `IMPLEMENTATION_FAILURE` with bounded repair evidence" and `:11` lists test-count mismatch first among the non-repairable failures. That matches `TSK/trusted_test_broker.py:143-147` and no longer contradicts the Review paragraph at `:27`. `DECISIONS.md:632` was corrected from 164/164 to 167/167 — see MAJOR below on whether 167 is the right number.

**Count mismatch is non-repairable even at exit 1 → CLOSED (prior n4 fixed too).** The count check (`:143-147`) now precedes the exit-1 repairable branch (`:148`), so a gate that exits 1 *and* reports a tampered count raises `SAFETY_FAILURE` on the first attempt rather than converging to it on the second. `observed_test_count is None` for zero or multiple markers (`:131`) reaches the same branch. Exercised directly by `TSK/tests/test_trusted_test_broker.py:78-84`.

**Bounded evidence vs. the rework ceiling → CLOSED.** `_bounded_failure_text`'s limit dropped 6000 → 900 (`:36`). `repair_packet` propagates verbatim through `trusted_review_builder.py:160-161` and `production_cycle_cli.py:416` to the `len(rework_context.encode()) > 8192` check at `managed_one_cycle.py:89`. Worst-case arithmetic: ≤900 bytes → ≤~935 characters after the truncation marker; the maximum `ensure_ascii=True` expansion is 6 chars/byte (ASCII control chars, or BMP non-ASCII at 2 bytes → `\uXXXX`), giving ≈5400 chars, plus ~45 chars of JSON envelope and ~259 chars of directive prefix ≈ **5.7 KB**. The realistic Russian-assertion case the prior review named lands near 3 KB. Both fit.

---

## MAJOR

**M1 — The regression count in both frozen records is stale, so the post-fix suite run is unevidenced.**
`REP/EVIDENCE.md:17` and `DECISIONS.md:632` both claim `167/167`, and `EVIDENCE.md:17` explicitly scopes that to "after independent-review fixes." But the fixes *added tests*: `TSK/tests/test_trusted_test_broker.py` now holds 8 test methods, including the two written for exactly these Majors (`test_broker_home_is_reset_before_every_gate:69`, `test_exit_one_with_count_mismatch_is_safety_failure:78`). Counting `def test_` at class-method indentation across `TSK/tests/*.py`, all inside the 12 `unittest.TestCase` subclasses, I get **169** collectible tests, with no `skip`/`expectedFailure` decorators anywhere in the directory. 167 is the pre-fix number the prior review counted.

So either the recorded run predates the fixes it certifies, or the number was copied forward without re-running. Either way, `DECISIONS.md` is a frozen record whose RATIONALE cites a verification that cannot be the one it describes — the same defect the prior review raised as Minor 3 at 164/164, now recurring at 167/169. I could not settle it by execution (Bash denied); one `python3 -m unittest discover -s tests -t .` resolves it, and the record must carry the number that run actually prints.

---

## MINOR

**m1 — Per-gate `HOME` wiping destroys the .NET/NuGet cache, and the .NET proof was not re-run.**
`HOME` and `DOTNET_CLI_HOME` both point at `/tmp/orchestrator-test-broker-home` (`:101-102`), which is now emptied before every gate. NuGet's global package folder defaults to `$HOME/.nuget/packages` and the http cache to `$HOME/.local/share/NuGet`, so a build gate and a test gate in the same run each restore from scratch, and a sealed run without network — previously viable once warm — now fails `INFRASTRUCTURE_FAILURE`. It fails closed, so this is not a safety issue, but it changes the operating requirements of the .NET profile that `D-2026-08-21-01` makes this architecture mandatory for, and neither `DECISIONS.md` nor `EVIDENCE.md` records it. `EVIDENCE.md:20` still cites the same `sha256:3fcaf80d…` .NET proof, which appears nowhere else in the repo as an artifact; nothing indicates it was re-run under per-gate wiping.

**m2 — The symlink/bounds half of the Major 1 fix has no test.**
`TSK/tests/test_trusted_test_broker.py:69-76` covers the wipe only. No test anywhere asserts that `reset_writable_dirs` raises `SAFETY_FAILURE` for a symlinked path or one outside `/tmp` (`trusted_test_broker.py:50-56`) — a repo-wide grep for `reset_writable_dirs` in `tests/` returns only the happy-path call at `:62`. Since `broker_home` is a hardcoded path, that guard *is* the entire testable surface of the validation, and it is untested.

**m3 — `test_exit_one_is_repairable_and_evidence_is_bounded` asserts no bound.**
`:26-35` checks classification, substring presence, and the recorded exit code — nothing about length. The truncation branch (`:39-43`) is never exercised by any test, and no test asserts the encoded packet stays under `managed_one_cycle.py:89`'s 8192. The 900↔8192 coupling that makes the arithmetic work is undocumented at both ends; a later bump of `limit` back toward 6000 would silently reintroduce Minor 1 with nothing red.

**m4 — `TMPDIR` is not pinned, so `/tmp` remains an uncleared cross-attempt channel.**
The env allowlist (`:97-108`) omits `TMPDIR`, so gate processes fall back to `/tmp` — predictable, agent-writable, never reset. That is structurally the channel Major 1 named, one directory up. `D-2026-08-21-01`'s "the broker is not an OS security boundary" honestly covers it, but "agent-writable external artifact roots must be cleared" reads stronger than what is implemented. Setting `TMPDIR` to a subdirectory of the already-reset `broker_home` would close it for free.

**m5 (carry-over, unchanged) — `ORCHESTRATOR_ARTIFACT_ROOT` silently absent for 2-4 dirs.**
`trusted_review_builder.py:200` still uses `reset_dirs[0] if len(reset_dirs) == 1 else None` while the packet schema admits up to 4. Prior Minor 4, untouched.

---

## NIT

- `:91` — `gate_dir.mkdir(parents=True)` still lacks `exist_ok`; prior n16/n2 remains open.
- `tests/test_trusted_test_broker.py:59` — the writable-root case still builds under `tempfile.TemporaryDirectory()` and passes the `/tmp` bound only because `TMPDIR` is unset; with `TMPDIR=/var/tmp` it fails as `SAFETY_FAILURE` for an unrelated reason. Prior n3, unchanged.
- `tests/test_trusted_test_broker.py:69-76` — the new HOME test contains no assertion; it detects breakage only via `GateFailure` propagating out of the verify gate, so a regression surfaces as a bare error with no message pointing at HOME.
- `:135-142` — `if timed_out or exit_code != 1:` / `if exit_code == 0: pass else: raise` is unchanged. The `timed_out` disjunct is still redundant (`:115` already forces 124) and the empty `pass` still obscures the `exit_code == 0 → continue` rule. Prior n6.
- `:135` precedes `:143`, so a gate exiting 2 *with* a tampered count is `INFRASTRUCTURE_FAILURE` rather than `SAFETY_FAILURE`. Both non-repairable; only the label is less precise.
- `reset_writable_dirs` is called inside the `try` at `:93`, so an `OSError` from it (root-owned directory, unremovable child) is caught at `:117` and reported as exit 127 — fail-closed, but labelled as a missing tool.
- A `SAFETY_FAILURE` from the broker-home reset escapes before `:120`, leaving an empty `gate_dir` with no `stdout.log`/`result.json`.
- `gate_id` length is unbounded in the broker (`:75` validates charset only), so `repair_packet` is bounded only modulo the caller's id length.

---

## Direct answers to the required checks

| Check | Result |
|---|---|
| Broker `HOME` reset before every gate | **Yes** — `trusted_test_broker.py:95`, inside `run_sealed_gate`, both builder and blind paths |
| Broker `HOME` symlink/bounds-validated | **Yes** — `:50` pre-resolution `is_symlink()`, `:54` `/tmp` bound; untested (m2) |
| Count mismatch non-repairable even at exit 1 | **Yes** — `:143-147` precedes `:148`; asserted at `tests/test_trusted_test_broker.py:78-84` |
| Bounded evidence fits the 8192 rework ceiling | **Yes** — limit 900 → ≈5.7 KB worst case, ≈3 KB realistic; unasserted (m3) |
| `EVIDENCE.md` classification record accurate | **Yes** — `EVIDENCE.md:10-11` now matches the code |
| Regression count record accurate | **No** — 167/167 recorded, 169 tests defined (M1) |
| Added tests exercise the fixes | **Partial** — wipe and exit-1+count covered; symlink/bounds and evidence bound not (m2, m3) |

---

**REWORK**

Both Majors are genuinely closed, and closed at the right layer — putting the reset inside `run_sealed_gate` rather than at each call site is what makes "before every gate" true by construction, and reordering the count check ahead of the exit-1 branch closes n4 as a side effect. The blocking item is narrow and clerical: the frozen records certify a 167/167 run that cannot be the post-fix suite. Re-run the suite, put the real number in `EVIDENCE.md:17` and `DECISIONS.md:632`, and state whether the .NET proof at `EVIDENCE.md:20` still holds under per-gate HOME wiping (m1) — that second point is worth resolving in the same pass, since it is the one behavioral consequence of the Major 1 fix that no test or record currently covers.
