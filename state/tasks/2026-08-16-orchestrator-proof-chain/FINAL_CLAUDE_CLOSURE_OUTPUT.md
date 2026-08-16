## Blockers

None that make an unsound acceptance provable from this packet alone — but see M1/M2, which leave the closure claims only partly evidenced.

## Majors

**M1 — Internal per‑R derivation is not bound to the *admitted* verdict digest.**
`production_cycle_cli.py` review(): `verdict_data = _read_json(decision_dir / "input-review_verdict.json", 1048576)` is read raw. The neighbouring `_load_prior_finding_details` deliberately verifies `_sha256(verdict_path) != expected_digest` against `manifest["input_digests"]["review_verdict"]` before trusting the same file. The new acceptance derivation skips that check, so per‑R outcomes derive from a file on disk rather than from the digest‑sealed reviewer verdict. Also `packet["builder"]` is dereferenced unconditionally (`packet["builder"]["acceptance_criteria"]`) whenever `proof_chain is not None`, while every other site guards with `if packet["builder"]`; a proof‑chain packet without a builder raises `TypeError`, not `PacketError`.

**M2 — Foreground control is a self-assertion, not a control.**
`openclaw_foreground_adapter.run_one` passes `foreground_authorized=True` unconditionally, and `main()` passes `sys.stdin.isatty()`. Neither verifies foreground execution; a pty wrapper, `script(1)`, tmux, or simply calling the adapter from a scheduler satisfies both. The adapter lost its own enforcement (the `fcntl` lock) and gained no replacement check. The prior blocker "foreground controls apply to every production execution path" is closed only nominally.

**M3 — Serialization lock is bypassed on the legacy execution path.**
```python
if allow_legacy:
    return _run_loaded_packet(packet, allow_legacy=True)
FOREGROUND_LOCK.parent.mkdir(...)
```
`allow_legacy=True` returns before the lock is taken, so legacy packets can execute concurrently with a locked 1.3 run. `_run_loaded_packet` also remains directly callable and unlocked (the tests use it that way).

**M4 — Internal-acceptance failure produces unstructured `ERROR`, not terminal evidence.**
When the managed cycle reaches `ACCEPTED` but `validate_acceptance_completeness` fails, or any `outcome != "pass"`, or no accepted review carries `requirements_acceptance`, `_run_loaded_packet` raises `PacketError`. Nothing is persisted: no `internal-requirements-acceptance.json`, no `final-result.json`, no dashboard. The blind leg is wrapped in `except BaseException` and escalates gracefully; the internal leg — the one this commit added — does not. This directly contradicts "dashboards cover failure states" and "error paths preserve structured terminal evidence".

**M5 — Dashboards can never display a failing gate.**
`run_verification_commands` raises on the first non-zero exit / timeout and returns nothing, and the escalation object is `{"status", "error"}` with no `verification_gates`. `_render_dashboard` therefore renders `tests: []` in exactly the failure states it is supposed to document; `"PASS" if gate["exit_code"] == 0 else "FAIL"` is unreachable. Builder gate results from `trusted_review_builder._run_gate` are still never surfaced at all. Gate evidence appears only when everything already passed.

**M6 — Interrupt outside the blind block yields no structured evidence.**
`main()` and `openclaw_foreground_adapter.main()` catch `except Exception`. `KeyboardInterrupt` during `load_packet`, `capture_clean_baseline`, `run_managed_cycle`, or `_render_dashboard` escapes as a traceback with no JSON terminal record and no exit-code 130 mapping. Only the blind stage was hardened (`except BaseException`).

**M7 — Worktree mutation detection has a real blind spot and a self-trip.**
`project_state` uses `git status --porcelain=v1 -z --untracked-files=all` plus `diff --binary HEAD`; gitignored paths are invisible, so a verification command writing to build/output/ignored dirs passes as read-only. `trusted_review_builder` already tracks `_ignored_state(root)` for exactly this reason — the two mutation checks are inconsistent. Conversely, nothing requires `run_root` to be disjoint from `project_root`; when it is not, the gate logs, `agent/` dir, and `blind-verdict.json` written after `before = project_state(...)` make every run report "blind verification commands mutated the worktree".

## Nits

- `href` filter rejects any `:` and leading `/`, but not leading backslashes; `\\host/x` is normalised to `//host/x` by WHATWG URL parsing for special schemes. Currently unreachable (artifacts are hardcoded), but `generate_dashboard` is a general utility.
- The blind verdict file is rewritten in place with `document_type` remapped, so `verdict_digest` binds the rewritten document, not the agent's actual output; the persisted-equals-admitted check then compares a file this function just wrote.
- Legacy `ACCEPTED` runs hit the same non-accepted branch (`or blind_config is None`) and render every requirement as `"not_assessed"` with evidence `"managed cycle did not reach acceptance"` — factually wrong text for that terminal state.
- `_render_dashboard` runs before `final-result.json` is written; a dashboard error (e.g. `output must be new` on a reused `run_root`) destroys the terminal record it was meant to illustrate.
- strict vs normal differ only by whether `code_inspection` counts as verification; gates, blind commands, and coverage scope are identical. Meaningful, but thin.
- `main()` calls `load_packet` then `run_packet` (which loads again) — duplicated parse of a file that may change between reads.
- Gate stdout/stderr are captured unbounded into memory before being written.
- Tasks table now hardcodes `"traceability_covered"` for every task in every terminal state; the Status column carries no information.

## Test gaps

- The entire per‑R derivation added in `review()` is untested: no case for `criteria_coverage` → `pass`/`fail`/`unable_to_verify`, missing coverage entries, unsatisfied status, or strict-vs-normal `verification_method` filtering.
- `run_managed_cycle` is mocked with a hand-authored `history` shape (`{"outcome": ..., "review": ...}`). The consumer in `_run_loaded_packet` reads `item.get("outcome")` at the item level; nothing in the suite verifies that the real `run_managed_cycle` emits that shape. If it nests outcome under `review`, schema‑1.3 acceptance is unreachable in production and the test still passes.
- No test that a mutating verification command is detected, that a failing/timing-out gate escalates, or that the timeout path (`exit_code = 124`) records evidence.
- No test for persisted-verdict ≠ admitted-verdict rejection, nor for post-agent worktree mutation.
- No test for the internal non-pass / missing `requirements_acceptance` path (M4) or for the non-accepted dashboard render.
- No test for lock contention or for `run_packet(..., foreground_authorized=False)` rejecting a 1.3 packet.
- `evidence_dashboard` symlink-ordering fix and href-scheme filtering have no accompanying tests in this commit.
- The new `text not in brief` traceability rule is only accommodated by editing fixtures; no negative test asserts a non-excerpt requirement is rejected.
- `test_blind_acceptance` now shells out to real `git init/commit` without isolating user config (`commit.gpgsign`, hooks, templates, `init.defaultBranch`), making the suite environment-dependent.

VERDICT: REWORK
