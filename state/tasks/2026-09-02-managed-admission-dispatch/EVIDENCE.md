# Evidence: managed admission and dispatch

Status: LIVE_VALIDATION_PARTIAL

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

- [x] Gateway restarted and healthy; Telegram deep probe is OK.
- [x] Live tool registry exposes `execution_supervisor_dispatch`, `execution_supervisor_start`, and `execution_supervisor_recover`.
- [x] Manifest tool contract and runtime config schema updated for OpenClaw 2026.7.1-2 compatibility.
- [ ] Real inbound Telegram topic drill. `sessions_send` now rejects thread-session targets, and `openclaw agent` is a CLI/nested path rather than Telegram ingress; neither is valid evidence for this gate.
- [ ] Real inbound Telegram private-chat drill for admission, foreground blocking, terminal delivery exactly once, and recursion exclusion.

## Live-test findings

- The first restart rejected agent-tool registration because the manifest lacked `contracts.tools`; this was corrected before the second restart.
- The second restart loaded the plugin without registration errors, and the three supervisor tools are present in the live OpenClaw tool registry.
- A CLI topic attempt ended during transcript compaction and created no admission artifact. A nested `sessions_send` direct attempt executed as an internal agent call and also created no admission artifact. These attempts are recorded as invalid ingress simulations, not as passing Telegram drills.
