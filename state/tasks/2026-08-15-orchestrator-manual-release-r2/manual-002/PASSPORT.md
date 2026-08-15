# Manual-002 — integrated external-read contract

Status: KNOWN REVIEW INFRA STOP; ONE CONTROLLED RETRY SCHEDULED AFTER 20:30 MSK

- Source: `/home/stanislav/projects/home-agent-factory` at
  `3d9c27e6901fc98f8fbaaf3819eac5a33225e73f`.
- Detached worktree:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-002-external-read-contract`.
- Evidence root:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-002-external-read-contract-run`.
- Allowed files: `src/core/policy.js`, `test/policy.test.js`,
  `schemas/agent-pack.schema.json`.
- Every other source path is forbidden.

## Required contract

- Missing `externalRead`, `domains`, or `methods` remains compatible and means
  an empty allowlist.
- `domains` accepts explicit ASCII DNS hostnames including single-label LAN
  names, multi-label names, and literal IPv4/IPv6 addresses. It rejects URLs,
  schemes, paths, queries, fragments, credentials, ports, wildcards,
  whitespace, empty labels, invalid label boundaries, and non-string entries.
- Host names are canonicalized to lowercase; IP literals retain a canonical
  representation supported by the Node standard library where practical.
- `methods` must be an array of strings and remains GET-only in the MVP;
  malformed containers/entries and non-GET methods raise controlled
  `PolicyError`, never an unknown exception.
- Result arrays are defensive frozen copies so later pack mutation cannot
  change the compiled grant.
- `agent-pack.schema.json` describes the same container types and accepted
  externalRead shape without adding dependencies.

## Gates and limits

- `npm test`; `git diff --check`, 60 seconds each.
- Maximum two Codex implementation attempts, 600 seconds each.
- Maximum one review-only final-full Claude leg, 600 seconds.
- Standard bounded repair and fail-closed policy.

## Boundaries

No dependency, network access, source edit, commit, merge, transfer, push,
deploy, Gateway/runtime/config, cron, systemd, daemon, unattended execution, or
external/system change. `R17_ACCEPT` authorizes only inspection of the isolated
diff; source transfer remains a separate explicit decision.
