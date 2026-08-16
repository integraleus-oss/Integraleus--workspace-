# Manual-004 — external-read contract closure

Status: ACCEPTED / R17_ACCEPT; TRANSFERRED; LOCAL COMMIT ONLY

- Source: `/home/stanislav/projects/home-agent-factory` at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- Worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-004-external-read-closure`.
- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-004-external-read-closure-run`.
- Allowed files: `src/core/policy.js`, `test/policy.test.js`, and
  `schemas/agent-pack.schema.json`; all other source paths are forbidden.

## Required result

- One explicit externalRead grammar in runtime and schema, with dotted-tail
  IPv6 rejected consistently.
- The complete externalRead schema subtree is pinned exactly; tests must not
  pretend to be a general JSON Schema validator or silently ignore keywords.
- A shared corpus covers accepted values and URL/path/port/credential/
  wildcard/whitespace/newline/zone-id/bracketed rejects.
- All compiled grant containers, including nested `modelPolicy`, are detached
  from caller-owned data and deeply immutable.
- Missing fields remain compatible; malformed values raise `PolicyError`; GET
  remains the only external-read method.

## Limits

- Maximum two Codex implementations, one final-full Claude review, and the
  standard single contract-only repair.
- Gates: `npm test` and `git diff --check`, 60 seconds each.
- Any unresolved major finding, invalid repaired verdict, unknown failure,
  forbidden path, or exhausted budget means STOP.
- No target-project commit, source transfer, dependency/network change, push,
  deploy, Gateway, cron, systemd, daemon, unattended, or system change.
- `R17_ACCEPT` permits inspection only; transfer is a separate decision.

## Checklist

- [x] Packet and boundaries recorded.
- [x] Clean detached worktree created.
- [x] Managed cycle completed.
- [x] Independent checks and path audit completed.
- [x] Result recorded.
- [x] Explicit transfer authorization received.
- [x] Accepted three-file diff transferred byte-for-byte to source.
- [x] Source checks repeated: 12/12 tests and `git diff --check` passed.
- [x] Local source commit created: `6e56761`.
- [x] Source worktree verified clean; no push, deploy, or activation performed.
