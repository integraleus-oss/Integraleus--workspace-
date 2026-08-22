**REWORK** — one major finding; the rest of the diff is clean.

## Major

**`print` inside the crash handler can mask the original exception** (`production_cycle_cli.py`, `run_packet` `except BaseException` block)

The old `except Exception: pass` was unconditionally safe. The replacement performs I/O inside the handler that swallowed the append failure:

```python
except Exception as evidence_exc:
    print("WARNING: ...", file=sys.stderr)
raise
```

If `print` itself raises — closed/broken stderr (`BrokenPipeError`), full disk (`OSError` ENOSPC), redirected-and-closed stream under a guard parent (`ValueError: I/O operation on closed file`) — that exception propagates instead of reaching `raise`. The original `KeyboardInterrupt` is demoted to `__context__`, so `main()` classifies the run as `ERROR`/exit 2 rather than `INTERRUPTED`/exit 130, and a genuine builder exception is replaced by an I/O error at the top level. This is precisely the invariant `test_terminal_evidence_failure_does_not_mask_interrupt` exists to protect, and the test only exercises a failing `append`, not a failing `print`.

Fix is one line — wrap the report so the handler stays total:

```python
except Exception as evidence_exc:
    with contextlib.suppress(Exception):
        print(..., file=sys.stderr)
```

## Minor

- **Error detail is discarded.** Only `type(evidence_exc).__name__` is emitted; the message (`"disk failure"`, the failing path, the chain-verification reason) is dropped, so the operator learns an `EvidenceError` occurred but not why. If the omission is deliberate leak-avoidance for spec axis 6, note that stderr is not the evidence stream and axis 6 does not constrain it — a truncated `str(exc)` would materially improve diagnosability of a terminal-evidence loss.
- **Exact-equality stderr assertion is fragile.** `assertEqual(stderr.getvalue(), "WARNING: ...\n")` captures *all* stderr writes in that block; any `warnings.warn` emitted from the packet-loading or evidence path during the test would fail it for unrelated reasons. `assertIn` (or `assertEqual` on the last line) keeps the same signal without the coupling.

## Test gaps

- No coverage of the failure mode introduced above: a failing `append` combined with an unwritable stderr should still surface `KeyboardInterrupt` (and `RuntimeError` for the non-interrupt branch). Patching `sys.stderr` with a stub whose `write` raises would pin it.
- The stderr-report path is asserted only for the `INTERRUPTED` branch; the `ERROR` branch (`test_run_packet_persists_error_terminal_event`) still exercises only the success-append case, so the `exit_code: 2` / `error_type` warning path is untested. Low value, same code path — worth a subTest rather than a new test.

## Out of scope (pre-existing, no change requested)

The success-path `evidence.append("terminal", ...)` after the `try` is unguarded, so an append failure there converts an `ACCEPTED` result into a top-level `ERROR` — the asymmetry with the crash path is untouched by this commit and I'd leave it alone here.

## Scope and claims

Diff is confined to the two stated files, 10 insertions / 3 deletions, no unrelated edits; `sys` and `StringIO` are already imported in their respective modules, so no new imports are needed. `patch("sys.stderr", ...)` correctly intercepts `production_cycle_cli`'s late `sys.stderr` lookup. The two-attempt ceiling, clean-run-root invariant, hash chain, and redaction surfaces are not touched by this commit.

I could not execute the suites (no tools this pass), so 55/55, 184/184, and `git diff --check` are unverified — this verdict is from inspection of the packet only.
