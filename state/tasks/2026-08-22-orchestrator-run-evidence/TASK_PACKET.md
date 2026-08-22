# Automatic RUN_EVIDENCE task packet

Status: ACCEPTED
Risk: MEDIUM
Owner: Stanislav
Baseline: workspace commit `9f8cf849`

## Goal

Every production-cycle invocation writes a deterministic, append-only,
versioned `RUN_EVIDENCE.jsonl` covering start, agent launches, gates/review
state, changed paths when available, and terminal status. Evidence must survive
`ERROR` and `INTERRUPTED` outcomes.

## Allowed files

- `state/tasks/2026-08-12-orchestrator-integration/run_evidence.py`
- `state/tasks/2026-08-12-orchestrator-integration/production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/managed_one_cycle.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_run_evidence.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_production_cycle_cli.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_managed_one_cycle.py`
- this task directory

## Forbidden

- Alpha BPR and `home-agent-factory` changes
- Gateway, auth, model, Synology, deploy, push, network, cron, system changes
- secrets or raw prompts in evidence
- overwrite/truncate of an existing evidence stream
- Codex/Claude review before local tests pass

## Acceptance criteria

- [x] Event schema is explicit and versioned.
- [x] Sequence numbers are monotonic and existing streams are never truncated.
- [x] Start and terminal events are written for accepted, escalated, error, and
      interrupted outcomes.
- [x] Agent/review/gate summaries avoid raw prompt and secret content.
- [x] Malformed/tampered existing streams fail closed.
- [x] Unit and integration tests pass, including abrupt exception paths.
- [x] Independent read-only review has 0 blocker/major.
- [x] Scoped local commit created; push/deploy remain forbidden.

## Checklist

- [x] Audit integration points
- [x] Add red tests
- [x] Implement writer and lifecycle integration
- [x] Run focused and full suites
- [x] Independent review
- [x] Fix blocker/major and rerun closure
- [x] Provisional commit and report
