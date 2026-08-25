# Universal integration R3 — sealed-run preparation

- Baseline: `b9e637754c5b00f38fd09f5949c971afd12db7a1`
- Profile: `standard`, manual/strict
- Canonical project mutation: forbidden
- Commit, push, deploy, transfer, VM/service/network access: forbidden
- Prior v1 implementation output: rejected and forbidden as input
- .NET output: external `/tmp/alpha-bpr-universal-integration-r3-artifacts` only, bound through schema 1.4 `codex_add_dirs`
- Explicit repository exclusions: `DECISIONS.md`, `STATE.md`, `TODO.md`, `memory/**`

The run is authorized only after a separate command containing the final sealed digest.
