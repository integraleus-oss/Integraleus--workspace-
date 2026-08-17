# Capability-grant accepted diff transfer

## Goal

Transfer the accepted capability-grant diff from the detached pilot worktree into the clean main `home-agent-factory` repository.

## Fixed point

- Source base: `8985b8e95427c471662562afa1b89a9e5b17a6a0`
- Accepted diff SHA-256: `5b29fb1e2a91f34c9a1c01c8ae04734a4f289ab4dcc29ecaff07e8e8dcf17fa2`
- Policy result: `ACCEPTED / R17_ACCEPT`
- Evidence commit: `fec0119`

## Allowed files

- `src/core/policy.js`
- `schemas/capability-grant.schema.json`
- `test/policy.test.js`

## Boundaries

- Main repository must start clean at the fixed source commit.
- Transfer only the three accepted files.
- Recompute the transferred diff digest and require an exact match.
- Run the repository tests and `git diff --check`.
- Create one local scoped commit only after all checks pass.
- No push, deploy, Gateway, systemd, plugin installation, or background process.
- Stop fail-closed on any mismatch or failed check.

## Checklist

- [x] Transfer explicitly authorized by Stanislav.
- [x] Source diff digest verified.
- [x] Main repository clean at fixed base.
- [x] Three files transferred.
- [x] Transferred digest equals accepted digest.
- [x] Tests pass.
- [x] `git diff --check` passes.
- [x] Local commit created.
- [x] Evidence recorded.
