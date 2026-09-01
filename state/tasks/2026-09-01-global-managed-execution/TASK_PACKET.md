# Task packet: global managed execution

- Owner: main agent / Stanislav owner sessions
- Started: 2026-09-01 19:01 MSK
- Mechanism: current foreground Codex turn; activation requires Gateway restart
- Goal: make managed execution and terminal notification route correctly from every owner Telegram topic and direct chat.
- Expected output: dynamic owner delivery, restart-safe automatic recovery, policy/evidence gates, tests, three-surface live proof, scoped commit.
- Timeout: current turn; no claim of background RUNNING without a live managed job.
- Failure mode: fail closed and report the exact unsupported surface.
- Notification target: originating owner session.
- Disable path: disable `plugins.entries.execution-supervisor-taskflow` and restart Gateway.

## Boundaries

- Allowed: workspace plugin/scripts/tests/evidence; OpenClaw plugin config; clean Gateway restart; synthetic owner-context tests.
- Forbidden: production/Alpha BPR data changes, Synology changes, unrelated worktree changes, push.

## Acceptance

- [ ] Delivery context is captured from the originating tool context, not a fixed topic.
- [ ] New and existing owner Telegram topics and direct chat are accepted safely.
- [ ] Terminal state is recovered and delivered without a manual user prompt.
- [ ] Exactly-once acknowledgement survives restart.
- [ ] Codex/subagent boundary is documented and enforced honestly.
- [ ] Unit/integration tests pass.
- [ ] Live tests pass for an ordinary topic, Alpha BPR, and direct chat.
- [ ] Evidence records IDs, delivery messages, commit and dirty-worktree boundary.
