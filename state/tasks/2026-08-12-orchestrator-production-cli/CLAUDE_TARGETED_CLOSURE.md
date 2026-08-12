I could not execute the test suite — the Bash call was denied by the current permission mode. This is a static review; no test-run evidence backs any "tests pass" claim below.

## Verification against the five items

**1. MAJOR 1 — write-enabled `project_root` restricted. RESOLVED.**
`production_cycle_cli.py:23-26` defines `SAFE_PROJECT_BASES`; `:90-91` requires the *resolved* `project_root` to be relative to one of them, and `:92-93` requires `(project_root / ".git").exists()`, which covers both a repo root (dir) and a worktree root (file). Resolution happens at `:86` before the containment check, so a symlink pointing outside the base is rejected. The `base` name in the genexp at `:90` does not leak into the enclosing scope, so the packet-dir `base` bound at `:81` is still correct at `:99`/`:108`. Tests: `tests/test_production_cycle_cli.py:84-93` covers both the outside-allowlist and the no-`.git` rejection, with `SAFE_PROJECT_BASES` patched to a temp base at `:40-41`.

**2. MAJOR 2 — CLI exit codes and validate-only/error tests. RESOLVED.**
`tests/test_production_cycle_cli.py:154-159` asserts the exact mapping `ACCEPTED→0`, `FAILED_INFRA→3`, `ESCALATED→4` against the ternary at `production_cycle_cli.py:174`, patching only `_run_loaded_packet` so the real `load_packet` and the real exit logic run. `:161-167` asserts `--validate-only → (0, "VALID")` *and* that `run_root` is not created, then a malformed packet → `(2, "ERROR")`.

**3. TOCTOU on review inputs. RESOLVED.**
`production_cycle_cli.py:148` copies with `symlinks=True` (links are copied as links, not dereferenced), and `:149-150` rescans `copied_inputs.rglob("*")` and raises `PacketError` on any symlink. The bundle is then re-derived from the copied tree at `:151`, so check and use are on the same bytes. `pathlib.rglob` does not descend into symlinked directories, so a symlinked dir surfaces as a detected entry rather than a traversal.

**4. Write-Codex timeout escalates. RESOLVED.**
`production_cycle_cli.py:140-143` maps *every* non-`OK` launch result to `classification: "UNKNOWN"`, and `managed_one_cycle.py:53` only yields `FAILED_INFRA` when the classification is exactly `KNOWN_INFRA` — so a timed-out write-mode Codex now lands on `ESCALATED` (exit 4). `tests/test_production_cycle_cli.py:125-129` asserts this for `{"status":"FAILED","timed_out":True}`.

**5. Invalid UTF-8 / path errors and missing attempt-2 rework fail closed. RESOLVED.**
`_bounded_text` wraps `UnicodeDecodeError` into `PacketError` at `:44-45`; `_inside` guards both `Path(raw)` (`:52-54`) and `resolve()` (`:60-63`) against `ValueError`/`OSError`. Attempt 2 with a missing or blank rework raises `PacketError` at `:133-134` — no `(rework or "")` fallback — which `managed_one_cycle.py:73-76` converts to `ESCALATED`.

## Remaining items (all below major)

- `production_cycle_cli.py:31` — `_read_json` catches `(OSError, json.JSONDecodeError)` but `read_text(encoding="utf-8")` on a packet file with invalid UTF-8 raises `UnicodeDecodeError`, which escapes as a non-`PacketError`. Same for the unguarded `packet_path.resolve()` at `:72` (NUL byte → `ValueError`). `main()`'s `except Exception` at `:175` still fails closed to exit 2/`ERROR`, so this is a library-contract wart, not an exit-code defect — it's the residue of the prior nit, whose two named sites were fixed.
- `production_cycle_cli.py:108,111` vs `live_review_cycle.py:31` — the review *prompt* is validated at load time but not copied; `run_cycle` reads it from the packet directory at use time, and for leg 2 that read happens after a full Codex+Claude round. Unlike `input_dir`, there is no re-check. Impact is bounded: a swapped prompt only changes what Claude is told, and the verdict still passes through digest-checked deterministic admission (`admit_live_review`), so it cannot manufacture `ACCEPTED`; a decode failure propagates to `ESCALATED`. Closing it would mean copying the prompt alongside the inputs at `:148`.
- `tests/test_production_cycle_cli.py:126` — the test name `test_codex_timeout_is_failed_infra` is stale; the body asserts `ESCALATED`. Rename only.
- Consequence of item 4: with all non-`OK` launches classified `UNKNOWN`, the `FAILED_INFRA`/exit-3 branch at `production_cycle_cli.py:174` is unreachable in production and is exercised only through the mocked status in `test_main_exit_contract`. That is the intended fail-closed posture, worth recording rather than fixing.

No blocker or major findings remain. Note that the checklist gate at `TASK_PACKET.md:49` ("Run integration/core/syntax/whitespace checks") is still unverified here — I could not run anything.

PRODUCTION_CLI_CLOSURE_PASS
