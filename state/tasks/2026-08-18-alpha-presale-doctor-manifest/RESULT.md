# Result — declarative Alpha-Presale doctor

Outcome: **ACCEPTED FOR SEPARATE TRANSFER DECISION**

- The ad-hoc Bash parser was removed.
- `verification-manifest.json` is the readiness source of truth.
- The manifest declares PATH dependencies, project/workspace scripts, and the
  reviewed SHA-256 of `scripts/verify.sh`.
- Invalid manifests cannot trigger reads through invalid declared paths.
- Changed paths are exactly `README.md`, `alpha_presale/cli.py`,
  `tests/test_core.py`, and `verification-manifest.json`.
- Focused tests: 25/25 PASS.
- Python source compilation: PASS.
- `git diff --check`: PASS.
- Final diff digest:
  `b89c4a32e616fde9710f4f292923f20131515d99ec82ff3361170d33642b0bff`.
- Manifest/script SHA-256 match:
  `192b7ac583a4b867d682aa5527f7f0520f01fc6f985ecb824cbcbed1922eba1a`.
- Independent review confirmed no blockers, the architecture replacement, the
  read-only boundary, deterministic JSON, exact 0/2 exits, and four-file scope.
- Its final two follow-up majors were closed after review by a real-file Python
  3.10 fallback test and explicit workspace-base documentation; gates were
  repeated on the final fixed point.
- No commit, transfer, push, deploy, Gateway/systemd, Web/API, licensing
  calculation, price read, or customer-facing action occurred.

Transfer remains a separate owner decision.
