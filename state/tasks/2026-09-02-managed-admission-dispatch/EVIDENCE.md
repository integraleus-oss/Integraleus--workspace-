# Evidence: managed admission and dispatch

Status: GATEWAY_DISPATCH_REPAIR_VERIFIED_AWAITING_LIVE_TELEGRAM_DRILL

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
- [x] Runtime inspection after the repair shows typed hooks for `before_agent_run`, `before_prompt_build`, and `before_tool_call`, with `customHooks: []` and no plugin diagnostics.
- [x] Focused checks after activation: plugin integration PASS, managed runner PASS, Python supervisor 7/7 PASS, recovery 1/1 PASS, syntax checks PASS, and `git diff --check` PASS.
- [ ] Repeat the real inbound Telegram topic drill after the typed-hook repair.
- [ ] Repeat the real inbound Telegram private-chat drill for admission, foreground blocking, terminal delivery exactly once, and recursion exclusion.

## Live-test findings

- The first restart rejected agent-tool registration because the manifest lacked `contracts.tools`; this was corrected before the second restart.
- The second restart loaded the plugin without registration errors, and the three supervisor tools are present in the live OpenClaw tool registry.
- A CLI topic attempt ended during transcript compaction and created no admission artifact. A nested `sessions_send` direct attempt executed as an internal agent call and also created no admission artifact. These attempts are recorded as invalid ingress simulations, not as passing Telegram drills.
- Real Telegram ingress tests at 2026-09-02 15:11 Europe/Moscow failed in both topic 14 and private chat: each turn invoked `bash` directly, returned a foreground answer, and created no admission/flow/state/evidence artifacts.
- Runtime inspection exposed the registration defect: `openclaw plugins inspect ... --runtime --json` reported `typedHooks: []`, `hookCount: 0`, and the intended lifecycle handlers only under `customHooks`. The plugin used `api.registerHook`; the installed OpenClaw runtime registers typed lifecycle hooks through `api.on`.
- Repair completed and activated at the 2026-09-02 15:16 Europe/Moscow Gateway restart: admission uses typed `before_agent_run`, prompt injection uses typed `before_prompt_build`, and the gate uses typed `before_tool_call`.
- Runtime proof: Gateway PID `3100659`, started 2026-09-02 15:16:08 Europe/Moscow; plugin status `loaded`, `hookCount: 3`, typed hooks present, custom hooks absent, all three supervisor tools present; Telegram deep status `OK`.
- Real Telegram tests at 2026-09-02 15:21 Europe/Moscow failed again: the Codex runtime did not execute the registered agent lifecycle hooks, so both requests ran in foreground and created no admission artifacts.
- The admission boundary was therefore moved to typed `before_dispatch`, which executes in the Gateway dispatch path before any agent runtime starts. A matching owner request is now handled there: admission artifacts and TaskFlow are created, supervisor is launched, and the immediate reply contains flow/PID/evidence; the original Codex turn is not started.
- Owner authorization at this boundary is constrained by `authorizedSenderIds`; the focused integration test covers accepted owner sender `109592643` and rejected non-owner sender.
- Post-repair checks: plugin integration PASS, managed runner PASS, Python supervisor 7/7 PASS, syntax checks PASS, and `git diff --check` PASS.
