I could not execute the test suite — the Bash call was denied by the current permission mode, so this is a static review only. Everything below is from reading the code; no test-run evidence backs the "tests pass" question.

# Independent review: bounded production CLI

## Axis 1 — Spec

The core bound holds. `run_packet` delegates to `run_managed_cycle` with the default `max_attempts=2` (`production_cycle_cli.py:133`), never overriding it, and `managed_one_cycle.py:38-39` hard-rejects any other value. Rework text reaches Codex only via the controller's `rework_context`, which comes from `admit_live_review`'s derived `rework_packet` — digest-checked against `decision.json`/`trusted-review-projection.json` (`managed_policy_review.py:45-48,84-89`), never from raw model output. `reviews` is pinned to exactly two legs (`production_cycle_cli.py:82-83`) and indexed as `attempt - 1`. There is no commit/push/deploy/systemd/cron/Synology call anywhere in the CLI, and the executable is fixed, not caller-selected. Exit 0 is reachable only for `VALID`/`ACCEPTED` (`production_cycle_cli.py:144`), and every failure path — admission error, digest mismatch, bad review JSON, launch failure — lands in the controller's `except` and yields `ESCALATED`.

One spec gap is material, below.

## Axis 2 — Standards/security

Path validation is otherwise sound: `_inside` rejects absolute paths and `..`, rejects a symlinked final component, then `resolve()`-and-containment-checks, which also catches a symlinked *intermediate* component. Copying inputs into the run dir before handing them to `live_review_cycle` correctly keeps the generated verdict write out of the packet directory.

---

## Findings

### MAJOR 1 — `project_root` is unconstrained, so a packet grants workspace-write Codex to any directory on the host

`production_cycle_cli.py:70-73` accepts any absolute path that is a directory and is not `/`:

```python
project_root = Path(packet["project_root"]).resolve()
if not project_root.is_dir() or project_root == Path("/"):
```

That value is passed straight into a **write-enabled** launch at `production_cycle_cli.py:113-116` (`codex_write=True`), which becomes `--cd <project_root> --write` (`agent_launcher.py:65`) and finally `codex exec --cd "$workdir" --sandbox workspace-write --skip-git-repo-check` (`scripts/codex-local-run.sh:118`). `--skip-git-repo-check` removes the only incidental guard, so the write sandbox is scoped to whatever the packet names — with no allowlist, denylist, or repo check anywhere in the chain.

Failure scenario: a packet with `"project_root": "/home/stanislav/.config"` (or `/home/stanislav/.openclaw/workspace/agents/main`, or a mounted Synology share) passes every check in `load_packet` and hands Codex write access there. That is exactly the mutation class `TASK_PACKET.md:23-25` forbids — Gateway/config/systemd/cron changes, secrets/`.env` access, Synology writes. The CLI enforces none of it; it relies entirely on the packet author not making a typo. `run_root` gets a real containment rule (`production_cycle_cli.py:74-75`) while the far more dangerous field gets none.

Remediation: constrain `project_root` the way `run_root` is constrained. Require it to resolve under an explicit allowlisted base (the canary step at `TASK_PACKET.md:51` already assumes "a separate worktree" — make that a check, not a convention), require `(project_root / ".git").exists()`, and reject a resolved path that equals or contains a home dotfile directory, `/etc`, or a non-local mount point.

### MAJOR 2 — `main()` has zero test coverage, so the fail-closed contract is untested at the only surface that expresses it

`TASK_PACKET.md:63-64` defines blocker behavior as "fail closed to a non-zero CLI exit," and the exit mapping lives entirely at `production_cycle_cli.py:141-149`. The test file imports only `PacketError, load_packet, run_packet` (`tests/test_production_cycle_cli.py:7`) — `main()` is never called. Nothing asserts that `ACCEPTED` → 0, `FAILED_INFRA` → 3, `ESCALATED` → 4, a `PacketError` → 2 with an `ERROR` document, or that `--validate-only` reports `VALID` without creating `run_root`.

Failure scenario: a future edit inverts or widens the ternary — e.g. adding `"REWORK"` to the exit-0 set, or reordering it so `ESCALATED` returns 0 — and the whole suite still passes. An operator or wrapper script keying on exit status would then treat a non-accepted cycle as success. The checklist item "Add success and fail-closed tests" (`TASK_PACKET.md:48`) is met for `run_packet` but not for the CLI boundary.

Note the CLI-level duplicate of the two-attempt bound is *not* needed — `tests/test_managed_one_cycle.py:47-54` already covers repeated-REWORK → `ESCALATED` and missing-rework → `ESCALATED`, and `:56-59` covers the `KNOWN_INFRA`/`UNKNOWN` mapping. The gap is specifically `main()`.

Remediation: add tests invoking `main()` with patched `run_packet` returning each of `ACCEPTED`/`FAILED_INFRA`/`ESCALATED`, asserting the exit code and the parsed stdout JSON; plus one `--validate-only` test and one malformed-packet test asserting exit 2 and `status == "ERROR"`.

### Nit — symlink scan and `copytree` are separated by a full Codex+Claude round (TOCTOU)

`production_cycle_cli.py:93-94` scans `input_dir.rglob("*")` for symlinks once, during `load_packet`. The actual copy happens later at `production_cycle_cli.py:124` with `shutil.copytree(leg["input_dir"], copied_inputs)` — default `symlinks=False`, which **follows** symlinks and copies target content. For review leg 2 that copy runs after attempt 1's Codex launch and Claude review have both completed, a window that can be tens of minutes wide. A symlink planted into `inputs-2/` inside that window is followed and its target dereferenced into the run directory. `test_rejects_symlink_in_review_inputs` (`tests/test_production_cycle_cli.py:59-62`) only proves the load-time check, not the use-time one.

Remediation: pass `symlinks=True` to `copytree` and re-run the `is_symlink` scan on `copied_inputs` immediately after copying, so the check and the use are on the same bytes. Alternatively stage both input trees into a private directory once during `load_packet` and copy from the staged trees.

### Nit — a killed write-sandboxed Codex is reported as retryable infra

`production_cycle_cli.py:118` maps any timed-out launch to `KNOWN_INFRA`, which `managed_one_cycle.py:53` turns into `FAILED_INFRA` (exit 3, the `R05_INFRA_RETRY` class). But that timeout path SIGTERMs and then SIGKILLs the process group (`agent_launcher.py:79-83`) while Codex was running with `codex_write=True`, so `project_root` may hold partially applied edits. Labelling that "infra, retryable" invites a rerun on a dirty tree. The same condition on the review leg is surfaced differently — a Claude wrapper timeout yields `FAILED_LAUNCH`, which `admit_live_review` rejects into `ESCALATED` (exit 4) — so the two legs disagree about the same underlying event.

Remediation: classify a write-mode Codex timeout as `UNKNOWN` (→ `ESCALATED`), reserving `KNOWN_INFRA` for read-only launches; or keep `FAILED_INFRA` and record a `workspace_dirty: true` marker in the launch result so any consumer knows the tree needs inspection before a rerun.

### Nit — non-`PacketError` exceptions escape `load_packet`

`_bounded_text` decodes with `data.decode("utf-8")` (`production_cycle_cli.py:35`) and `_inside` calls `Path(raw).resolve()` (`production_cycle_cli.py:47`) without guarding either. A prompt or bundle containing invalid UTF-8 raises `UnicodeDecodeError`, and a packet path containing a NUL byte raises `ValueError` — neither is a `PacketError`. `main()` still fails closed via `except Exception`, so this is not an exit-code defect, but every test asserts `assertRaises(PacketError)` and any future library caller catching `PacketError` would leak these through.

Remediation: wrap the decode in `try/except UnicodeDecodeError` and the `Path(raw)`/`resolve()` in `try/except (ValueError, OSError)`, re-raising as `PacketError`.

### Nit — `(rework or "")` masks a broken controller invariant instead of failing closed

At `production_cycle_cli.py:111`, attempt 2 builds the prompt with `+ (rework or "")`. The controller guarantees a non-empty rework string before continuing (`managed_one_cycle.py:62-67`), so `None` here means that invariant is already broken — and the fallback would quietly send Codex a prompt ending in a bare `Policy-authenticated rework:` header with no directives. Also worth noting: `load_packet` is executed twice per run (once at `production_cycle_cli.py:142`, again inside `run_packet` at `:107`, making the `packet` local dead in the non-validate branch), and `_bounded_text(task_note)` runs twice (`:80`, `:108`) — each duplicating the full `rglob` symlink scan.

Remediation: `raise PacketError("attempt 2 requires a policy-authenticated rework packet")` when `attempt != 1 and not rework`. Reuse the already-loaded packet in `main()` by having `run_packet` accept the loaded dict.

---

Two major findings are open (unconstrained write target; untested CLI exit contract), so this slice should not proceed to the canary or the scoped commit.

PRODUCTION_CLI_REWORK
