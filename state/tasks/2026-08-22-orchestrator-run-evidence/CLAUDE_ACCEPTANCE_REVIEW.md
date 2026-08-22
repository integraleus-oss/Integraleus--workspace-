## Verdict: REWORK

Scope note first, since it bounds everything below: the packet contains **only commit `3d60ce70`** (2 files), not the staged diff for the six files listed in the task. `run_evidence.py`, `managed_one_cycle.py`, `test_run_evidence.py` and `test_managed_one_cycle.py` are absent, so spec axes 1–3, 5–7 are unverifiable here. Tool use is disallowed, so I also cannot verify the 55/55, 184/184 or `git diff --check` claims — treat them as unverified. The verdict below covers this commit only.

### Major

**1. `except Exception: pass` silently discards every terminal-write failure (`production_cycle_cli.py`, error path in `run_packet`).**
The handler now suppresses `OSError` (ENOSPC, EACCES, parent dir removed), `TypeError`/`AttributeError` from payload construction, and anything else — with no log line, no stderr note, no sidecar. Consequences:

- Axis 4 ("ERROR and INTERRUPTED all receive one terminal event") degrades from an enforced invariant to a best-effort one, and the degradation is undetectable after the fact: the stream is simply missing its terminal record with no explanation anywhere.
- Axis 3's fail-closed posture is inverted on this path: a stream that was truncated or externally modified mid-run raises, gets swallowed, and the run exits with only the original error visible.
- Standards axis "error preservation": the primary exception is preserved correctly by the bare `raise` (good), but the *secondary* one is destroyed outright.

The intent — never let evidence bookkeeping mask the real failure — is right; the implementation loses the diagnostic. Suggested shape: keep the broad catch, but emit the suppressed error somewhere durable, e.g. `run_root/RUN_EVIDENCE.terminal-error` or a stderr line, before `pass`.

**2. The production change is untested and unrelated to the commit.**
Commit message and both test additions are about the unauthorized-builder-gate path; neither added assertion exercises the failure path where `evidence.append("terminal", …)` raises. The one behavioral change in the commit has zero coverage and no stated rationale, which is exactly the "no unrelated edits" standard. If the broadening was required by something in the missing five files, that dependency isn't visible from this packet.

### Minor

3. Asymmetry between the outer `except BaseException` and inner `except Exception`: a `KeyboardInterrupt` delivered *during* the terminal append (double Ctrl-C is plausible on the INTERRUPTED path) escapes and replaces the original exception. Pre-existing shape, not a regression, but the broadening is the natural moment to make it `except BaseException` with the same suppress-and-`raise`.

4. Success-path `evidence.append("terminal", …)` sits outside the `try`, so an `EvidenceError` there turns an `ACCEPTED` run into a `main()`-level `ERROR`/exit 2 with a stream that has no terminal event. Not touched by this diff; flagging because it's the mirror of the case being hardened.

5. Positive, worth keeping: the terminal payload carries only `status`/`error_type`/`exit_code` and deliberately omits `str(exc)`, unlike `final-result.json`. That's the correct read of axis 6 — don't let it drift.

### Nit

6. The new test appends a second full scenario to `test_…repair…` rather than a new method: shared mutated `app.py`, `reset_mock()` on two mocks, and `shutil.rmtree` of the run root. A failure in the second half reports under the first half's name, and the first half's residue is in scope. Split it.

7. `shutil` is used but no import appears in the diff — verify it's already imported at module top, otherwise this is a `NameError` at runtime (which would contradict the 55/55 claim).

### Test gaps

- **No test for the only production change.** Needed: patch `EvidenceStream.append` to raise `OSError` on the terminal write, drive `_run_loaded_packet` to raise, assert the original exception type/message propagates unchanged *and* that the suppressed error is recorded wherever finding 1 lands it.
- Second scenario asserts the event *sequence* but not the escalation reason: add `attempts_used == 1`, `terminal_reason`, and `launch.call_count == 1` / `live.call_count`, so a light-profile escalation caused by something other than unauthorized rework can't pass silently.
- No assertion that the light-profile stream is hash-chain-valid / monotonic after the `rmtree` + fresh-create (axis 2 and the clean-new-run-root invariant, axis 7). The event-list check doesn't cover chain integrity; it may live in `test_run_evidence.py`, which isn't in this packet.
- `KeyboardInterrupt` → `INTERRUPTED` terminal event with `exit_code: 130` is in the changed hunk but has no assertion in the added tests.
