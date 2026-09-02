# Evidence: managed admission and dispatch

Status: READY_FOR_ACTIVATION

- Artifact: `state/tasks/2026-09-02-managed-admission-dispatch/TASK_PACKET.md`
- Owner: main
- Started: 2026-09-02 14:30 Europe/Moscow
- Execution mechanism: current foreground implementation turn
- Expected output: tested plugin admission/dispatcher/gate implementation and focused commit
- Runtime activation: pending separate Gateway/config approval

## Implemented

- `before_agent_run` classifies the explicit completion-notification contract and writes admission, context, task packet, and evidence before agent work.
- `before_agent_start` injects the mandatory dispatcher instruction.
- `before_tool_call` blocks foreground tools and Codex/subagent launch until dispatch, and keeps them blocked after detachment.
- `execution_supervisor_dispatch` creates the owner-bound TaskFlow and launches a detached managed agent runner.
- The runner records atomic terminal evidence; the existing restart-safe recovery service performs exactly-once delivery.
- Managed child sessions are excluded from admission to prevent recursive dispatch.

## Checks

- [x] Plugin integration: `TASKFLOW_PLUGIN_INTEGRATION_OK`
- [x] Managed runner: `MANAGED_AGENT_RUNNER_OK` (success and crash)
- [x] Existing Python supervisor tests: 8/8 PASS, including success, timeout, crash, escalation, recovery, and exactly-once notification
- [x] Syntax checks for plugin and runner
- [x] `git diff --check`

## Pending runtime gate

- Restart Gateway to load the new hooks/tool.
- Inspect the live plugin registry after restart.
- Run one synthetic request from a Telegram topic and one private-session drill.
- Confirm task artifact precedes flow, foreground bypass is blocked, terminal notification is delivered once, and no recursive admission occurs.
