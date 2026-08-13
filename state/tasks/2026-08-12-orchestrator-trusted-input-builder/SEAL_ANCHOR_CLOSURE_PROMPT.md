# Seal-anchor targeted closure

Re-review the residual blocker in `ADMISSION_BOUNDARY_CLOSURE.md` against current:

- `trusted_review_builder.py`
- `production_cycle_cli.py`
- `live_review_cycle.py`
- their changed tests

Confirm that the SHA-256 of `seal.json` is captured before Claude launch, retained outside the reviewer-writable input directory, and required by the post-review/pre-admission verifier before any sealed input is read or verdict is materialized. Confirm that rewriting both inputs and `seal.json` cannot satisfy the anchored check, builder mode cannot omit it, and legacy behavior remains compatible.

Do not edit files. End with exactly one token on its own line: `SEAL_ANCHOR_CLOSURE_PASS` or `SEAL_ANCHOR_CLOSURE_REWORK`.
