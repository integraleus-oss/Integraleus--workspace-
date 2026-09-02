# Task Packet: managed admission and dispatch

- Owner: Stanislav / main agent
- Started: 2026-09-02 14:30 Europe/Moscow
- Execution: current foreground implementation turn
- Goal: make explicit completion-notification requests enter managed execution before work starts.

## Scope

- Add deterministic managed-intent classification.
- Add automatic managed dispatch with task packet, evidence, state, and TaskFlow.
- Fail closed on work tools until managed admission exists.
- Cover Telegram topics, private chat, Codex/subagent launch, recovery, terminal states, and exactly-once delivery.

## Boundaries

- Allowed: `projects/execution-supervisor-taskflow/`, focused tests, this task directory.
- Forbidden: unrelated dirty files, Alpha BPR source, production/customer deployment.
- Gateway/config activation requires a separate explicit runtime approval.
- Commit only focused files after tests; no push.

## Acceptance checklist

- [x] Explicit completion-notification intent is classified as managed.
- [x] Admission creates durable artifacts before work tools run.
- [x] Dispatcher creates an owner-bound TaskFlow and managed runner.
- [x] Work-tool bypass is blocked fail-closed.
- [x] Telegram topic/private and Codex/subagent paths are tested.
- [x] Restart, success, timeout, crash, escalation, and exactly-once delivery are tested locally.
- [x] Existing supervisor tests remain green.
- [x] `git diff --check` passes.
- [x] Focused commit created; push not performed.
- [ ] Gateway activation and cross-session live drill completed after explicit runtime approval.

## Live-gate regression

- 2026-09-02 15:11 Europe/Moscow: real Telegram topic and private-chat drills bypassed managed admission and executed `bash` directly.
- Root cause: lifecycle handlers were registered with `api.registerHook`, which creates custom hooks; OpenClaw agent runtime consumes these events only from typed hooks registered with `api.on`.
- Repair gate: runtime inspection must show typed hooks for `before_agent_run`, `before_prompt_build`, and `before_tool_call` before another Telegram drill.
