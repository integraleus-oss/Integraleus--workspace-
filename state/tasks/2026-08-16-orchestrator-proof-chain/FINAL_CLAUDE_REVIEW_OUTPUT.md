## Scope note
Reviewed only the filtered diff of `7ff67bd`. `agent_launcher`, `requirements_traceability`, `trusted_review_builder`, `managed_one_cycle` are outside the packet; where a control's integrity depends on them I say so explicitly rather than assuming it holds.

---

# Spec findings

### BLOCKER S1 — The "internal" side of the acceptance cross-check is fabricated
`production_cycle_cli.py`, `_run_loaded_packet`: the internal acceptance document is synthesized with a hardcoded `"outcome": "pass"` and the literal evidence string `"internal sealed policy outcome R17_ACCEPT"` for every active requirement. It is not derived from gate results, review verdicts, or the task map.

Consequences:
- `compare_acceptance`'s disagreement check compares the blind verdict against a constant, so it can never detect an internal failure — only re-detect a blind non-pass, which `non_pass` already catches. The dual-verdict design is vacuous.
- Final ACCEPTED therefore rests on a single blind agent verdict.
- `internal-requirements-acceptance.json` is a persisted artifact asserting per-requirement evidence that was never computed. That is fabricated evidence in the run record.

Answer to Q2: a genuinely failed/unverified Rxx *is* recorded as `pass` internally; it is only stopped if the blind agent independently catches it.

### BLOCKER S2 — "manual" / foreground / one-at-a-time is a label, not a control
- `load_packet` rejects `control_mode != "manual"`, but nothing anywhere requires a human: no tty check, no confirmation prompt, no session marker. A packet labelled `manual` runs identically under cron or a background supervisor.
- The single-run lock lives only in `openclaw_foreground_adapter.run_one`. `production_cycle_cli.main()` will execute a 1.3.0 packet with no lock at all, so N concurrent runs against the same worktree are possible via the primary CLI.
- `run_one(packet, lock_path=...)` takes an unvalidated lock path; any caller passing a per-packet path defeats mutual exclusion (the tests do exactly this).

Answer to Q3/Q4 (partial): automatic/deep/pre-1.3 packets are correctly blocked (`load_packet` mode/depth gate; `_run_loaded_packet` pre-1.3 gate; adapter re-check). But the *foreground/serial* invariant is not enforced on the path that actually executes.

### MAJOR S3 — `verification_commands` allowlist is decorative
`load_packet` validates each argv against `trusted_review_builder.ALLOWED_GATE_PROGRAMS`, then `build_prompt` only string-formats them into prose ("Verification commands you may run read-only"). Nothing executes them and nothing constrains what the blind agent actually runs. A validated allowlist that has no runtime effect reads as a control but is not one.

### MAJOR S4 — Blind read-only-ness is asserted, not demonstrated
The only controls are `codex_write=False` on a `launch("claude", ...)` call and prompt text. `codex_write` is a codex-role flag; the packet contains no evidence it constrains the claude role. There is no post-run check that the worktree is unchanged (no baseline diff, no digest of `project_root` before/after), even though `trusted_review_builder.capture_clean_baseline` is already available in the same function. An acceptance agent that can write to the tree it is judging invalidates the gate.

### MAJOR S5 — Blindness is not enforced at the source of the prompt text
`build_prompt` labels `item["original_text"]` as "exact source excerpts (not internal specifications)", but nothing requires `original_text` to be a verbatim substring of `original_brief`. Whoever generates the manifest can put implementation prose there and it reaches the blind prompt verbatim. Answer to Q1: the *harness* prose is clean; the *data* channel is unvalidated.

Related: brief and excerpts are interpolated inside `---` fences with no delimiter neutralization.

### MAJOR S6 — Dashboard displays fabricated/incomplete evidence
Display-only, escaped, and non-overwriting — yes. But the content is wrong:
- `"tests": []` is hardcoded, so the Tests/gate table is always empty despite gates having run.
- Task statuses are derived from the terminal state (`completed`/`review_required`), not from actual task outcomes.
- Requirement rows come from the fabricated internal list (S1), so the dashboard always renders every requirement as `pass`.
- No dashboard is produced at all for any non-ACCEPTED managed-cycle outcome (early `return result`), i.e. exactly the runs an operator most needs to inspect.

### MAJOR S7 — `depth` is validated and then ignored
`strict` vs `normal` is accepted by `load_packet` and never read again. No behavioural difference exists.

### MAJOR S8 — Interrupt during blind acceptance produces no structured evidence
`except Exception` around the blind call does not catch `KeyboardInterrupt`/`SystemExit`; neither does `main()`. Ctrl-C after the managed cycle returns ACCEPTED escapes both handlers: no `final-result.json`, no dashboard, no structured status, non-standard exit code. It is fail-*safe* (never ACCEPTED) but not fail-closed-with-evidence. Answer to Q6: error paths yes, interrupt path no.

### MINOR S9 — Escalation record loses per-requirement detail
On disagreement/non-pass, `run_blind_acceptance` raises before writing `result.json`, and the caller stores only `{"type","message"}`. Which Rxx disagreed survives only as a comma-joined string inside an exception message, which then also becomes the single dashboard "finding".

### MINOR S10 — `allow_legacy=True` now silently permits executing 1.2.0 packets with no blind acceptance
The flag's meaning widened from "legacy" to "pre-1.3" with no audit record distinguishing the two. No caller in this packet sets it, but the escape hatch is broader than before.

---

# Standards findings

### MAJOR T1 — Digest anchors do not bind what was validated
`run_blind_acceptance` validates the in-memory `raw` (after rewriting `document_type` to `requirements_acceptance`), then records `verdict_digest` as the hash of `blind-verdict.json` — a file that is never re-read and compared to the validated object. The commit's own test demonstrates the divergence: `fake_extract` writes `{}` to disk while returning a full verdict, and the run still records status ACCEPTED. `prompt_digest` similarly assumes the launcher wrote `input-prompt.md` with the exact prompt passed in.

### MAJOR T2 — Symlink checks are dead code (applied after `.resolve()`)
Three occurrences: `evidence_dashboard.generate_dashboard` (`evidence_path`, `output_path`) and `openclaw_foreground_adapter._inside_packet_root`. `Path.resolve()` follows symlinks, so `resolved.is_symlink()` is always false. Practical impact: a **dangling** symlink at `output_path` passes both `exists()` and `is_symlink()` on the resolved path, so the "output must be new" guard is bypassed and the HTML is written to the symlink target, potentially outside `run_root`. The containment checks that matter (`is_relative_to`) still hold; the codebase's own pattern elsewhere (`_inside`) checks `is_symlink()` *before* resolving — match it.

### MAJOR T3 — Artifact hrefs have no scheme allowlist
`f'<a href="{_safe(item.get("path","#"))}">'` — `html.escape` neutralizes quotes and angle brackets but not `javascript:`/`data:text/html` URLs. Currently the artifact list is harness-authored, but `generate_dashboard` is a general function over untrusted evidence JSON and the test suite only covers text-node escaping.

### MAJOR T4 — Dashboard digest binding is self-referential and unrecorded
The caller does `generate_dashboard(dashboard_json, ..., evidence_dashboard.file_digest(dashboard_json))` — hashing the file it just wrote. That is a narrow TOCTOU guard, not a binding to the run's sealed evidence. Neither the evidence digest nor the dashboard digest is recorded in `final-result.json`, so the HTML cannot later be verified against the run.

### MINOR T5 — Adapter double-loads the packet (TOCTOU)
`run_one` calls `load_packet` to check schema/mode, then `run_packet(packet_path)` re-reads and re-validates from disk. The re-validation prevents downgrade, but the adapter should pass the already-loaded packet to `_run_loaded_packet` so exactly one snapshot is executed.

### MINOR T6 — Exit-code vocabulary diverges between CLI and adapter
`production_cycle_cli.main` maps `FAILED_INFRA→3`; the adapter maps everything non-ACCEPTED/non-INTERRUPTED to `4`, collapsing infra failure and escalation.

### NIT T7 — Style
`rows`/`links` as assigned lambdas inside `generate_dashboard` (prefer nested defs, and it diverges from the module's function style); `_write` in `blind_acceptance` is a generic helper used once; the `blind_acceptance_verdict → requirements_acceptance` rewrite silently accepts either type, so the prompt's document-type instruction is unenforceable.

---

# Test gaps

1. **The blind path is never exercised end-to-end from the CLI** — `test_v12_requires_complete_requirements_proof_chain` patches `run_blind_acceptance` entirely, so `compare_acceptance`, prompt construction, and verdict validation are untested from `_run_loaded_packet`.
2. **No test that a non-pass or missing blind result yields ESCALATED and non-zero exit** from the CLI; no test that blind `INTERRUPTED` yields final `INTERRUPTED`.
3. **No test that a failing internal outcome blocks acceptance** — impossible to write against the current fabricated internal document, which is itself the signal for S1.
4. **No test of missing-requirement handling in `compare_acceptance`** (`blind_by_id[req_id]` would raise `KeyError`, not `BlindAcceptanceError`).
5. **No test that the blind agent cannot write to `project_root`** and no worktree-unchanged assertion after the blind run.
6. **No test that `verification_commands` have any runtime effect** — only that malformed ones are rejected at load.
7. **Adapter concurrency is never tested**: no contention test (two holders of the same lock), and every test passes a custom `lock_path`, so `DEFAULT_LOCK` behaviour and `main()` exit codes are uncovered. `load_packet`/`run_packet` are fully mocked, so `_inside_packet_root` symlink behaviour and the real 1.3 gate integration are untested.
8. **Dashboard tests cover only the ACCEPTED shape**: no findings-row rendering, no `javascript:` href case, no dangling-symlink output path, no non-dict members inside collections.
9. **`test_prompt_excludes_internal_material_and_keeps_exact_brief` is near-tautological** — it asserts against harness-authored constant prose (`assertNotIn("specification", prompt.lower().replace("internal specifications",""))`) and never feeds a manifest whose `original_text` contains internal prose.
10. **No test that `depth` changes behaviour** (it cannot).
11. **Legacy replay is not re-asserted after the gate message change** from "legacy task packets…" to "pre-1.3 task packets…"; no test in this diff pins 1.0.0/1.1.0/1.2.0 replay under `allow_legacy=True`.
12. `test_successful_run_is_read_only_and_digest_bound` contains dead scaffolding (creates `run/agent/input-prompt.md`, then unlinks and rmdirs it before setting `launch.side_effect`) — remove it; it obscures what the test actually asserts.

---

# Answers to the hard questions

| # | Question | Answer |
|---|---|---|
| 1 | Prose leak into blind prompt? | Harness prose is clean; `original_text` is unvalidated against the brief, so internal prose can enter (S5). |
| 2 | Can bad Rxx reach ACCEPTED? | Blind non-pass/disagreement is blocked. But internal outcomes are hardcoded `pass`, so the cross-check is vacuous and ACCEPTED is single-sourced (S1). |
| 3 | Automatic/deep/pre-1.3 execution? | No — correctly gated at both `load_packet` and `_run_loaded_packet`. |
| 4 | Adapter escape/concurrency/config/push? | Root containment holds; no Gateway/config/cron/commit surface in the adapter. Concurrency is *not* guaranteed — the lock is absent from the primary CLI path and bypassable via `lock_path` (S2). |
| 5 | Dashboard display-only/digest-bound/escaped/overwrite-safe? | Display-only and text-escaped: yes. Digest binding is self-referential and unrecorded (T4); overwrite guard defeatable by a dangling symlink (T2); hrefs unscoped (T3); content partly fabricated (S6). |
| 6 | Fail-closed with structured evidence? | Exceptions: yes → ESCALATED with a record. Interrupts: no — `KeyboardInterrupt` escapes both handlers, leaving no artifacts (S8). |
| 7 | Sufficiently tested without weakening legacy replay? | No. The blind path is mocked out end-to-end, adapter tests mock the entire orchestrator, and legacy replay is not re-pinned after the gate-message change. |

**VERDICT: REWORK**
