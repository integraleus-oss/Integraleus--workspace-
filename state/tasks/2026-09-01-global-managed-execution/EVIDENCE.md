# Evidence: global managed execution

Status: SUCCEEDED
Started: 2026-09-01 19:01 MSK
Owner: main agent
Mechanism: foreground Codex turn
Last verified: 2026-09-01 19:12 MSK

## Current proof

- Material artifact: this task packet and evidence.
- Live process: current foreground Codex turn only; no detached job claimed.
- Baseline finding: plugin v0.1.0 uses manual `start`/`recover`, fixed delivery to topic 2922, and has no autonomous recovery service.
- Latest committed baseline: `aca3c133 feat: enforce managed execution truth`.

## Verification log

- Dynamic originating-session delivery implemented: channel, account, target,
  and thread/topic are persisted with each supervised run.
- Gateway recovery service implemented with a 2-second configured poll loop,
  terminal reconciliation, provider delivery, and acknowledgement after send.
- Python supervisor tests: 7/7 PASS.
- TaskFlow plugin integration test: PASS.
- Owner admission is bounded to `agent:main:telegram:*` sessions and the
  `agent:main:main` direct session; other agents remain rejected.
- Live current-topic drill: flow `c0e7e39b-3d41-4b63-8131-f674072419f6`,
  owner topic `2922`, `SUCCEEDED`, notification delivered.
- Live Alpha BPR drill: flow `06dad8d8-caf9-4dcc-9019-9ed70e9b245a`, owner
  topic `14`, `SUCCEEDED`, notification delivered.
- Live private-chat drill: flow `43429179-c081-45a6-bf5a-bb50676a2511`, owner
  `agent:main:main`, `SUCCEEDED`, notification delivered.
- All three TaskFlows reconciled to terminal `succeeded` state.
- `EXECUTION_TRUTH_OK` after the live drills.
