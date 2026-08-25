# Universal integration pilot v1 — result

Status: `ESCALATED / DOTNET_IGNORED_STATE_AND_SCOPE_FAILURE`

## Cycle

- Packet: `sha256:c446b850a11161feff3a86cf2069686a7aba4ce322250f00dfdc87660589a52f`
- Baseline: `b9e637754c5b00f38fd09f5949c971afd12db7a1`
- Profile: `standard`
- Attempts used: 1
- Review: not launched
- Formal terminal reason: `policy_or_runtime_escalation`

## Failure evidence

The managed builder stopped before review with
`ignored files changed since baseline capture`. The .NET build and test steps
updated ignored `bin/` and `obj/` outputs after baseline capture. The current
strict ignored-state invariant is therefore incompatible with in-worktree
.NET compilation unless build outputs are isolated outside the worktree or the
builder receives a narrowly defined generated-output policy.

The implementation also changed forbidden tracked paths outside the packet
allowlist: `DECISIONS.md`, `STATE.md`, and `TODO.md`, and created
`memory/2026-08-20.md`. This independently prevents admission. `README.md` and
the integration/docs/test paths were allowed.

Codex reported direct checks of 10 focused tests, 350 full tests, build, JSON,
and diff-check, but these claims were not admitted by the trusted builder and
received no independent review. The isolated diff is therefore unaccepted and
must not be transferred.

## Safety

- Canonical `/home/stanislav/projects/alpha-bpr` remained clean.
- No commit, transfer, push, deploy, VM operation, service change, Gateway
  change, system change, or network change was performed.
- This sealed cycle is terminal and must not be continued.

## Next gate

Prepare a fresh packet/worktree that:

1. makes `DECISIONS.md`, `STATE.md`, `TODO.md`, and `memory/` explicitly
   forbidden in the implementation prompt;
2. routes all .NET intermediate/output paths outside the Git worktree, or adds
   a narrowly tested builder policy for deterministic generated build output;
3. reuses no unreviewed implementation output automatically;
4. repeats deterministic red/preflight checks before a separately authorized
   RUN.
