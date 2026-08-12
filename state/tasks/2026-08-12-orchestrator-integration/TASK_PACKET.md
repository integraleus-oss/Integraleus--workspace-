# Task Packet: Local Orchestrator Integration Slice

Status: TARGETED_CLOSURE_CODE_PASS_EVIDENCE_REFRESHED
Owner: Stanislav
Coordinator: OpenClaw main
Risk: MEDIUM, local tooling only

## Goal

Turn the completed deterministic Codex-Claude policy core into a locally usable
workflow entry point without changing OpenClaw runtime, Gateway configuration,
remote repositories, or external services.

## Source

- Accepted core commit: `e95faa7`
- Policy implementation:
  `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`
- Final core result: `ACCEPTED / R17_ACCEPT`, 84/84 tests

## Tracer-bullet slice

Implement one complete local path:

1. create a run workspace from explicit JSON inputs;
2. validate the reviewer verdict with trusted bindings;
3. evaluate the deterministic policy;
4. write machine-readable decision and a concise run summary;
5. preserve every input/output artifact for audit and replay.

This slice does not launch Codex or Claude itself. It integrates validated
outputs first; agent-process automation is a later slice.

## Allowed files

- `state/tasks/2026-08-12-orchestrator-integration/`
- new local scripts under `scripts/` only when required by this slice

## Forbidden actions

- GitHub push or other remote publication
- Gateway, OpenClaw config, model, auth, or MCP changes
- Synology reads/writes or backups
- root/system changes
- network calls except the approved, sanitized fresh Claude review gate
- edits to the accepted core unless a reproduced blocker requires a separate
  rework packet
- automatic commit

## Deliverables

- [x] task packet
- [x] deterministic reviewer projection adapter
- [x] local runner CLI and documented bundle format
- [x] integration tests for all four outcomes and fail-closed behavior
- [x] evidence and usage documentation
- [x] current-tree deterministic verification
- [x] fresh independent review
- [ ] scoped commit after owner direction or normal completion handoff

## Acceptance criteria

- AC-01: Runner invokes the accepted validator and policy core; it does not
  duplicate or weaken their decisions.
- AC-02: Inputs are explicit files, not inferred from free text.
- AC-03: Each run has an isolated directory and immutable input snapshots.
- AC-04: Output includes the contract-validation result, policy decision,
  exit status, and content digests.
- AC-05: Invalid/missing inputs fail closed and never emit `ACCEPTED`.
- AC-06: Replaying identical inputs yields byte-identical decision output.
- AC-07: Tests cover accepted, rework, failed-infra, escalated, malformed, and
  replay behavior.
- AC-08: Existing 84 core tests remain green.
- AC-09: No unrelated dirty-worktree file is changed.

## Current checkpoint

- Adapter and isolated local runner implemented.
- New integration suite: 14/14 passing after rework.
- Accepted core regression suite: 84/84 passing.
- `py_compile` and whitespace checks passing.
- Fresh targeted closure found all six original findings closed by construction
  and no new blocker/major code regression. Its only major was stale evidence
  that still reported the pre-rework 9-test suite; that evidence is now
  refreshed from an independent local 14/14 + 84/84 run.
- Next action: scoped local commit, then encrypted local-network backup.
