# Evidence — Alpha-Presale doctor transfer

- Owner authorization: Telegram topic 2922, message 3367.
- Canonical base before transfer: `52ea3baac783d08ce95f54000933af65b7af570f`.
- Accepted source and target pre-commit diff digest:
  `b89c4a32e616fde9710f4f292923f20131515d99ec82ff3361170d33642b0bff`.
- Transferred exactly:
  - `README.md`
  - `alpha_presale/cli.py`
  - `tests/test_core.py`
  - `verification-manifest.json`
- Focused `DoctorCliTests`: 25/25 PASS.
- Full canonical suite: 121/121 PASS.
- Python source compilation: PASS.
- `git diff --check`: PASS.
- Local project commit: `95a5818` (`feat: add declarative doctor readiness checks`).
- Pre-existing untracked `docs/reviews/` and `memory/` were not staged or
  modified by the transfer.
- No push, deploy, Gateway/systemd, licensing calculation, price read, Web/API
  change, or customer-facing action occurred.
