# Alpha-Presale doctor — declarative verification manifest

## Goal

Replace the ad-hoc `scripts/verify.sh` parser with explicit verification
metadata in `pyproject.toml`. Detect drift with the script SHA-256, check all
declared commands read-only, and preserve deterministic JSON/exit behavior.

## Allowed paths

- `alpha_presale/cli.py`
- `tests/test_core.py`
- `README.md`
- `pyproject.toml`

## Forbidden

- Changing or executing `scripts/verify.sh`.
- Licensing/TKP calculations, prices, Web/API, deployment or customer files.
- Commit, transfer, push, deploy, Gateway or systemd changes.

## Acceptance

- No shell-language parser remains in `doctor`.
- Manifest declares script path/hash, PATH dependencies, project-local scripts,
  and workspace-local scripts.
- Missing, malformed, stale, or unavailable declarations yield JSON and exit 2.
- Focused tests, compilation, `git diff --check`, allowlist and independent
  review pass before transfer can be considered separately.
