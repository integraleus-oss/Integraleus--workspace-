# Task Packet: Execution supervisor and managed continuation

Status: RUNNING
Risk: MEDIUM
Owner: main agent
Started: 2026-09-01 15:30 MSK
Execution mechanism: current foreground Codex turn
Expected output: verified supervisor, TaskFlow integration path, heartbeat recovery, and delivery proof

## Authorization

- Stanislav Pavlovskiy: “Тогда реализуй все, что нужно.”
- Telegram `HOME:2922`, message `4627`, 2026-09-01 15:29 MSK.
- Runtime activation approval: Telegram `HOME:2922`, message `4630`,
  2026-09-01 15:49 MSK. This explicitly authorizes local plugin
  install/enable, Gateway restart, and one synthetic notification in this topic.

## Scope

Allowed:

- workspace execution-truth scripts, tests, heartbeat instructions and task evidence;
- local OpenClaw TaskFlow integration code/configuration that does not require Gateway restart;
- synthetic local processes and local notification sinks;
- read-only inspection of OpenClaw runtime/plugin APIs.

Forbidden:

- Gateway restart or runtime/config activation beyond message `4630`;
- cron/systemd/daemon installation;
- external/public/customer sends;
- automatic commit, push, deploy, source transfer, destructive actions;
- unrelated project changes.

## Required Behavior

- [x] Foreground supervisor binds a concrete PID and evidence file.
- [x] Outcomes: success, timeout, crash, escalation, interrupt.
- [x] Evidence is updated atomically and cannot remain falsely `RUNNING`.
- [x] Notification is exactly-once and local delivery acknowledgement is verifiable.
- [x] Persisted state supports restart recovery.
- [x] Heartbeat fallback audits and resumes/finalizes eligible supervisors.
- [x] Managed TaskFlow identity/state adapter is implemented and integration-tested.
- [x] Synthetic tests cover terminal outcomes, recovery and deduplication.
- [ ] Install/enable plugin, restart Gateway, and verify real TaskFlow/Telegram delivery (approved by message `4630`).

## Acceptance

- focused test suite passes;
- end-to-end synthetic delivery proof passes;
- execution-truth audit passes;
- `git diff --check` passes;
- evidence records exact files, commands, process/job identity, and residual activation boundary.
