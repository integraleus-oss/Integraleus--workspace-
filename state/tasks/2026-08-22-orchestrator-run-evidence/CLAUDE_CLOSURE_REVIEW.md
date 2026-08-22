## Verdict: REWORK

Scope note up front: the packet contains only commit `217daab5`'s filtered diff (4 files). `managed_one_cycle.py`, `tests/test_managed_one_cycle.py`, and the base implementations of `run_evidence.py` / `production_cycle_cli.py` are not present, so spec axes 1, 5 and 7 and legacy-replay compatibility are assessed only insofar as the shown hunks touch them. Per your "do not use tools" instruction I did not execute the suites or `git diff --check`; the 55/55, 184/184 and clean-whitespace claims are unverified here.

### Blocker / major

**1. `review` REWORK event is emitted on gate failures that never rework** (`production_cycle_cli.py`, GateFailure handler)
The new `evidence.append("review", {..., "outcome": "REWORK", "rule_id": "R09_GATE_FAIL"})` sits *before* the guard that decides whether the failure is repairable:

```python
evidence.append("review", {"attempt": ..., "outcome": "REWORK", ...})
if (review_profile != "standard" or exc.classification != "IMPLEMENTATION_FAILURE"
        or attempt >= 2 or not isinstance(exc.repair_packet, str) or not exc.repair_packet.strip()):
    raise
```

For every non-repairable gate failure (light profile, non-`IMPLEMENTATION_FAILURE`, attempt 2, missing/blank repair packet) the stream now records a REWORK verdict immediately followed by an `ESCALATED`/`FAILED_INFRA` terminal, for a run in which no rework was ever authorized. That is a false evidence record on the exact axis this change exists to serve (4/5). Move the append below the `raise` guard, or distinguish the terminal case (`outcome: "ESCALATED"`/`"GATE_FAIL_TERMINAL"`).

**2. Probable duplicate `review` event on the repairable path**
The accepted-run test asserts the sequence `start, agent_launch, review, agent_launch, review, terminal`, i.e. some caller of `review()` appends a `review` event from the returned result. The GateFailure branch also `return`s a `{"outcome": "REWORK", "rule_id": "R09_GATE_FAIL"}` dict after appending its own `review` event. If the caller appends unconditionally, attempt 1 gets two `review` events with the same `attempt`, which breaks any consumer deriving attempts/verdict counts from the stream and undercuts the two-attempt-ceiling audit (axis 7). The caller's append site is not in the packet — this must be checked before merge; if the duplicate exists it is a blocker.

**3. 1 MiB cap on builder artifacts converts oversized-but-valid runs into hard failures**
`_read_json(copied_inputs / "changed-paths.json", 1048576)` / `evidence.json` are called inside `review()` with no handler. A legitimately large changed-path set or gate-evidence file now raises mid-review and aborts a run that would otherwise pass gates. The cap itself is right (unbounded attacker-influenced input into a hash-chained append is worse), but the failure should degrade the *evidence entry* (truncated marker + count + digest of the source file), not the run. Also, `_read_json`'s second positional parameter is not shown in the packet; that it is a byte limit is an assumption.

### Minor

**4. `except Exception: pass` around the terminal append is silent and over-broad.** Not masking the original `KeyboardInterrupt`/error is correct, but the outcome is a stream that ends without a terminal event and no trace of why — exactly the state axis 3 tells readers to treat as "fail closed / suspicious". At minimum narrow to `EvidenceError` and attach the failure to the raised exception's context (or to `result`/stderr) so the missing terminal is explainable. Note the asymmetry is otherwise fine: the success-path append is deliberately unguarded and fails the run closed.

**5. `exclusive_parent` drops ancestor creation and conflates errors.** `os.mkdir(path.parent, 0o700)` no longer creates intermediate directories, so a run root whose parent tree does not yet exist fails with `ENOENT` reported as `"run root already exists or cannot be created"`. Either pre-create ancestors with `os.makedirs(path.parent.parent, exist_ok=True)` before the exclusive `mkdir`, or distinguish `EEXIST` from other `OSError`s in the message. Mode `0o700` on the run root is correct for the local-admin model but is not asserted anywhere.

**6. No cleanup on partial `create` failure.** If the parent-directory `fsync` (or anything after `os.mkdir`) fails, the freshly created run root and empty `RUN_EVIDENCE.jsonl` are left behind, and every retry then fails with "already exists" until manual cleanup. Unlink the file / rmdir the parent on the error path when this call created them.

**7. `allow_nan=False` protects writes but not reads.** `_parse_valid` uses bare `json.loads`, which accepts `NaN`/`Infinity` literals; an externally written stream containing them parses, then fails in `_digest` with `"evidence payload is not JSON serializable"` rather than a chain/contract error. Fails closed, but the diagnostic is misleading — pass `parse_constant=` to reject at parse time.

**8. O(n²) re-validation per append.** `append` re-reads and fully re-validates the whole file on every event. With `changed_paths` payloads now bounded at 1 MiB, a builder run with many attempts re-hashes megabytes per event. Pre-existing, but the new cap makes large payloads reachable; consider validating only the tail record against the cached digest plus length.

### Nits

- `(event == "start" and self._sequence)` is a pure precedence-clarifying paren; behavior unchanged. Fine, just note it as cosmetic in a "close review findings" commit.
- `create`'s symlink defense is sound (`mkdir` refuses an existing symlinked parent, `O_EXCL|O_NOFOLLOW` on the file), but the parent is opened by path again for the `fsync`; a dirfd-relative `openat` would close the residual TOCTOU. Out of scope under the stated threat model.

### Test gaps

- **No test for the packet's main functional addition**: nothing exercises the GateFailure branch to assert the new `review` event is written, that it appears exactly once, or that it is *absent* on the non-repairable/escalating path. Finding 1 would not be caught by this suite.
- `test_run_packet_rejects_existing_or_symlink_run_root_without_mutation` uses `assertRaisesRegex(Exception, "run_root must be new|run root already exists")`. With `_run_loaded_packet` patched to return ACCEPTED, only the evidence guard can fire, so the alternation is dead and the assertion would still pass if either invariant were deleted. Pin the exact exception type and message per branch, and assert the two invariants separately (one with `_run_loaded_packet` patched, one without).
- `test_terminal_evidence_failure_does_not_mask_interrupt` asserts only that `KeyboardInterrupt` escapes. It does not assert the resulting stream state (start-only, still chain-valid, unsealed, reopenable by `EvidenceStream.open`) — i.e. the durability half of finding 4 is untested.
- No test that the 1 MiB `_read_json` cap actually trips, nor what a run does when it does.
- No test that the run root is created `0o700`, or that `create` leaves no residue when it fails after `mkdir`.
- No test for external append *after* a terminal event (reopen a sealed stream and append) — in-process sealing is covered, the post-terminal external case in axis 3 is not, at least not in the files shown.
- No concurrency test despite `flock` + the "changed outside the writer" path; two writers racing on one stream is asserted only by the single-writer tamper test.
