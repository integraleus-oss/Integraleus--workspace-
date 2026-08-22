## REWORK

The core fix is correct: emitting `review/REWORK` only after the authorization gate passes stops the stream from claiming a rework decision on runs that actually die at the gate. Event ordering (gate FAIL → review) is preserved on the authorized path, `repair_packet` prose is still kept out of the payload (spec 6), and the re-raise path still reaches a single terminal event via `run_packet`'s `BaseException` handler (spec 4). Two things block acceptance.

### Major

**1. The added test does not exercise the changed branch.** The new assertions in `test_production_cycle_cli.py` cover only the *authorized* repair path, where old and new code emit exactly the same two events in the same order. Revert the `production_cycle_cli.py` hunk and this test still passes — it is not a regression guard for the commit it ships with. The behavior that changed is the unauthorized path (`review_profile == "light"`, `classification != "IMPLEMENTATION_FAILURE"`, `attempt >= 2`, empty/non-str `repair_packet`), and none of those four cases is asserted. Needed: at least one case where `GateFailure` re-raises, asserting the stream contains the `gate`/FAIL event, **no** `review` event, and one terminal event.

**2. `except Exception:` → `except run_evidence.EvidenceError:` is an unrelated, unguarded change.** It is outside the commit's stated scope ("record only authorized builder rework"), has no test, and narrows a deliberately broad swallow in the crash path. If `EvidenceStream.append` can surface anything that is not an `EvidenceError` — a bare `OSError` on a full/read-only filesystem, or a `TypeError`/`ValueError` from payload serialization — the new exception propagates out of the `except BaseException` block and *replaces* the original failure: `main()` then reports the evidence-write error instead of the real cause, and a `KeyboardInterrupt` is reclassified from `INTERRUPTED`/130 to `ERROR`/2. That directly contradicts the error-preservation and spec-4 requirements. `run_evidence.py` is unchanged in this packet, so I cannot confirm from the diff that `append` wraps all I/O and encoding failures in `EvidenceError`; if it does, state that contract and add a test pinning it, otherwise keep the broad swallow (or `except (run_evidence.EvidenceError, OSError)`).

### Minor / nit

- **Compatibility check not evidenced.** Dropping the per-attempt `review` event on the fail-closed path is only safe if no validator/replay path requires "every attempt has a review event". Nothing in this packet demonstrates that; worth confirming against `run_evidence` validation before merge.
- **Duplicated guard.** `if evidence is not None:` now appears twice in the same handler; the second could be folded into the existing block structure, though the current form is the clearest way to keep the `raise` in between.
- **Assertion breadth.** The test filters to `event == "review"` only; it never asserts the `gate` FAIL event survives on the repair path, so the "gate recorded even when rework is authorized" half of spec 5 is unpinned here.

### Unverified claims

Per the instruction to review this packet without tools, I could not independently run the suites or `git diff --check`; the 55/55, 184/184 and whitespace results are unconfirmed. Nothing in the added lines shows trailing whitespace, and indentation/line length are unchanged from the original condition, so the `--check` claim is at least consistent with the visible diff.
