# Manual-004 result

Status: `ACCEPTED / R17_ACCEPT`; transferred and committed locally

## Managed result

- One Codex implementation completed within the bounded write scope.
- The initial review required the mandatory separate final-full review only;
  no second code modification was performed.
- The final review-only Claude leg was admitted after its bounded contract
  repair and produced `R17_ACCEPT`.
- Changed paths are exactly `schemas/agent-pack.schema.json`,
  `src/core/policy.js`, and `test/policy.test.js`.
- Managed cycle-result SHA-256:
  `0eddcfaf68a7cbde01277979a9b276fdb7418233825468ce3ae1c415d94657e5`.

## Independent verification

- `npm test`: PASS — 12 tests, 0 failures.
- `git diff --check`: PASS.
- Runtime and schema use one explicitly pinned externalRead grammar.
- Dotted-tail IPv6 is rejected consistently.
- URL-like, whitespace, zone-id, bracketed, malformed, method, and missing-field
  cases are covered.
- Nested `modelPolicy` and all grant containers are defensive immutable copies.
- Source `/home/stanislav/projects/home-agent-factory` remains clean at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.

## Residual nit

The final reviewer recorded one non-blocking nit: `requestedModelClass` is
expected to be a scalar string but does not pass through the same explicit
clone/validation helper as the surrounding grant fields. This does not violate
the sealed criteria and did not block `R17_ACCEPT`; it should be addressed in a
later small hardening task or before expanding accepted input types.

## Controlled transfer

- Stanislav explicitly authorized the separate transfer step on 2026-08-16.
- The accepted three-file diff was applied to
  `/home/stanislav/projects/home-agent-factory` from the unchanged source base
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- All three transferred files match the accepted detached-worktree versions
  byte-for-byte.
- Repeated `npm test`: PASS — 12 tests, 0 failures.
- Repeated `git diff --check`: PASS.
- Local target-project commit:
  `6e56761 fix: harden external read policy contract`.
- The target-project worktree is clean after the commit.
- No dependency/network change, push, deploy, Gateway, cron, systemd, daemon,
  unattended, or system change occurred.
