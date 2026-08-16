## Findings by severity

### Major

**M1 — Single-use is keyed on the authorization *filename*, not on its content or message ID (`openclaw_foreground_adapter.py::_admit_authorization`).**
```python
used = authorization_path.with_suffix(authorization_path.suffix + ".used")
with used.open("x", ...)
```
Replay requires only `cp authorization.json authorization2.json`: the packet digest still matches, `approved_by` still matches, `source_message_id` still matches, and the marker path is new, so `open("x")` succeeds. The same owner message therefore authorizes unlimited schema‑1.3 executions. There is no ledger keyed by `authorization_digest`, `packet_digest`, or `source_message_id` — the marker records the first two but is never *read* by any admission path. The `.used` marker is also plain-file deletable by the same process that invokes the adapter.

**M2 — `source_message_id` is validated for presence only; it is bound to nothing.**
```python
or not isinstance(value["source_message_id"], str) or not value["source_message_id"].strip()
```
The major requires the authorization to be bound to the packet digest *and* the message ID. The packet digest binding is real (`value["packet_digest"] != _digest(packet_path)`); the message-ID binding does not exist. Any non-blank string passes, it is not cross-checked against any owner-message record, and it is not written into the `.used` marker, so it cannot even be reconciled after the fact. Combined with M1, the authorization is an unsigned plaintext file inside a directory the invoking process can write — the only remaining barrier is the literal string `"Stanislav Pavlovskiy"`.

### Major-risk (correct as written only under an assumption the diff does not establish)

**M3 — `project_state` now hashes the full bytes of every ignored file (`blind_acceptance.py::project_state`).**
Two consequences, neither covered by a test:
- `run_verification_commands` captures `before`, *then* creates `run_dir/verification/gate-N/{stdout.log,stderr.log,result.json}`, then compares `project_state(...) != before`. If `run_root` lives inside `project_root` under an ignored path, every blind run now self-trips `"blind verification commands mutated the worktree"`. This was previously invisible because ignored paths were not hashed. It is safe only if `run_root` is outside `project_root` — the pre-existing untracked-file hashing implies that is the case today, but nothing in the code enforces it.
- The read is unbounded: `path.read_bytes()` over every ignored file, twice per verification run. In a tree with `node_modules`, `.venv`, build output, or the large binary assets present in this repo, that is a wall-clock and memory hazard on the acceptance path.

**M4 — The new review-time `PacketError`s bypass the new terminal-evidence path (`production_cycle_cli.py::_run_loaded_packet`, inside `review()`).**
```python
raise PacketError("sealed internal reviewer verdict digest mismatch")
raise PacketError("requirements acceptance requires a trusted builder")
```
These fire inside the `review()` closure, i.e. inside `run_managed_cycle`, while the new `try/except BaseException` that writes `final-result.json` + dashboard wraps only the *post-cycle* block. Unless `run_managed_cycle` converts closure exceptions into a terminal result, a verdict-digest mismatch — the exact failure M‑"internal acceptance" is meant to make auditable — produces no `final-result.json` and no dashboard record. Not determinable from this packet.

### Verified as claimed

- **One fixed lock on every public path:** the `if allow_legacy: return _run_loaded_packet(...)` early return that skipped `FOREGROUND_LOCK` is gone; `allow_legacy` is now threaded through the locked call. `run_packet` is the only non-underscore entry, and both `main()` and the adapter go through it.
- **Schema‑1.3 cannot run directly:** `main()` now passes `foreground_authorized=False` unconditionally (the `sys.stdin.isatty()` self-grant is removed), and `run_packet` raises for `schema_version == "1.3.0"` without the flag. The adapter is the only grantor. (What it grants on is M1/M2.)
- **Interrupts:** both `main()`s catch `BaseException` and map `KeyboardInterrupt` → `INTERRUPTED`/130; the post-cycle block maps it to status `INTERRUPTED` with a written `final-result.json`.
- **Failing gate records are loadable:** `run_verification_commands` writes `result.json` *before* raising, so `load_verification_records` does see the failing gate, and the records are attached to `blind` prior to `_render_dashboard`.

### Minor

1. `load_verification_records` uses `sorted(glob("gate-*/result.json"))` — lexicographic, so `gate-10` precedes `gate-2` in the dashboard once there are ≥10 gates.
2. On internal-acceptance failure with a *partially* complete `internal`, the dashboard renders `internal["results"]` verbatim; requirements missing from the incomplete document (precisely what `validate_acceptance_completeness` rejected) are silently omitted rather than emitted as `not_assessed`. The `if not requirements` fallback only catches the empty case.
3. The failing `internal` document itself is never persisted — `internal-requirements-acceptance.json` is written only on the success path, so the failure evidence is the error string alone.
4. The verdict digest is taken from the in-process `result["decision"]["input_digests"]` with no cross-check against on-disk `decision.json` — unlike the REWORK branch two blocks below, which cross-checks both `registry_digest_file` and `registry_digest_after`.
5. `except BaseException` in both `main()`s swallows `SystemExit`, reporting it as `ERROR`/exit 2.
6. The `.used` marker is written *before* `run_packet`, so an infra failure or interrupt permanently burns the owner authorization; recovery requires a fresh owner message.
7. TOCTOU: the adapter digests `packet_path`, then `run_packet` re-reads the file from disk.
8. `verification_gates` is attached only on the exception path; whether the normal-return `blind` carries gate records to the dashboard is not shown.

## Test gaps

- **`_admit_authorization` has zero direct tests** despite being the headline change: wrong `packet_digest`, wrong `approved_by`, blank/non-string `source_message_id`, extra or missing keys, unreadable JSON, symlinked authorization, and — critically — replay via the *same* file (`.used` exists) and replay via a *copied* file (would fail, exposing M1).
- No test asserts `run_one` creates the marker or returns `manual_authorization_marker`; the existing test only checks `status`.
- No test that `run_packet` rejects schema‑1.3 without `foreground_authorized`, and none that `main()` never self-authorizes now that the tty check is gone.
- No test that the legacy path takes `FOREGROUND_LOCK` (concurrent second run with `allow_legacy=True` must be rejected) — the regression this commit fixes is unguarded.
- No test for the verdict-digest mismatch raise or the non-dict `builder` raise, and none showing what terminal artifact those produce (M4).
- No test that internal-acceptance failure / `KeyboardInterrupt` writes `final-result.json` with `status` `ESCALATED`/`INTERRUPTED` plus dashboard fields, nor for the partial-`internal` dashboard shape (Minor 2).
- No test that a failing blind gate's record reaches the *rendered* dashboard, only that it can be loaded.
- No test for ignored-file mutation detection, for the `<special>` sentinel on ignored dirs/symlinks, or for run artifacts written under an ignored path not tripping the mutation check (M3).

**VERDICT: REJECT** — 2 confirmed majors (M1, M2), 2 unresolved major-risks (M3, M4).
