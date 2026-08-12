## Targeted closure verification — MAJ-6 and MAJ-7 only

Read exactly the four named files. No other file opened, nothing edited. **The suites were not executed** — the prior review recorded `python3` as denied in this session and the current scope is read-only over four files — so all counts below are read-verified, not run-verified.

### MAJ-6 (wording correction) — CLOSED

The prior fix list had three items; all three landed:

1. **Smoke scope disclosed.** `EVIDENCE.md:23-25` now says the first Codex and Claude launcher smokes "used the workspace root as their read-only project scope." The scope is stated rather than left implied. The literal path is not spelled out, but "workspace root" is unambiguous in this document and satisfies the disclose-or-narrow ask.
2. **Categorical sentence scoped.** The former unqualified "No Synology, memory, config, secrets, customer data… was involved" is now "no *prompt requested* Synology, memory, config, secrets, or customer data," with Gateway/systemd/GitHub/push split into a separate, correct claim about what the run used. The claim no longer overstates read scope.
3. **r3 root mischaracterization fixed.** `EVIDENCE.md:51-53` now reads "a synthetic fixture *prompt* against the narrow accepted core root `state/tasks/2026-08-11-codex-claude-orchestrator/implementation`." "Synthetic fixture" attaches to the prompt; the root is correctly labeled accepted core code.

### MAJ-7 (negative-test gaps) — CLOSED

All four named gaps now have tests:

| Gap | Coverage |
| --- | --- |
| Unsupported `role` | `test_agent_launcher.py:60-62` — `launch("other", …)` raises `LaunchError` |
| Bad `project_root` | `test_agent_launcher.py:63-64` — nonexistent path raises `LaunchError` (same `is_dir` guard) |
| Missing `wrapper-output.json` | `test_agent_launcher.py:101-105` |
| `run_cycle` path escape | `test_live_review_cycle.py:73-88` — symlink to an out-of-root dir raises, and asserts nothing was written outside |

The previously closed items in these files are intact: process-group timeout regression (`:66-75`), envelope/error rejection (`:86-99`), argv contract (`:107-115`), absolute-path-across-`cd` (`:117-126`).

### Regression check on the bounded change

`EVIDENCE.md:38` moved from 26/26 to 29/29. That is consistent, not a drift: `test_agent_launcher.py` now holds 11 tests (was 9, +unknown-role/missing-project and +missing-wrapper-output) and `test_live_review_cycle.py` holds 4 (was 3, +symlink escape), so 14 + 11 + 4 = 29. MAJ-5 remains closed on counts and, as before, unverified on execution results.

No previously closed finding was disturbed by the edit. The `py_compile` line still omits its file list and the post-`SIGKILL` `communicate` residual still stands — both were logged as non-blocking nits and are unchanged.

TARGETED_PASS
