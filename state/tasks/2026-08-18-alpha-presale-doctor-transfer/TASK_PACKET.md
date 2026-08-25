# Alpha-Presale doctor manifest transfer

## Authorization

Telegram topic 2922, message 3367: owner approved the separate transfer gate.

## Source

- Accepted isolated worktree: `alpha-presale-doctor-pilot-002-r3`.
- Source diff digest:
  `b89c4a32e616fde9710f4f292923f20131515d99ec82ff3361170d33642b0bff`.
- Files: `README.md`, `alpha_presale/cli.py`, `tests/test_core.py`,
  `verification-manifest.json`.

## Target

- Canonical project: `/home/stanislav/workspace/alpha-presale`.
- Expected base: `52ea3baac783d08ce95f54000933af65b7af570f`.
- Preserve pre-existing untracked `docs/reviews/` and `memory/`.

## Gates

- Apply exactly the accepted four-file diff.
- Verify target diff digest equals source.
- Run focused tests, compilation and `git diff --check`.
- Commit locally only after gates pass.
- No push, deploy, Gateway/systemd, licensing calculation or customer action.
