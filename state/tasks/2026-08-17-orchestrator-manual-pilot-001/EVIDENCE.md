# Evidence — controlled manual OpenClaw pilot 001

## Admission

- Owner authorization: Telegram topic `2922`, message `3321`.
- Mode: foreground, one packet, manual, strict bounded cycle.
- Source fixed point: `8985b8e95427c471662562afa1b89a9e5b17a6a0`.
- Source repository clean at admission.
- Detached worktree clean at admission.
- Root guard, plugin, systemd, Gateway, cron, push and deploy are out of scope.

## Result

- Managed terminal status: `ESCALATED`, exit 4, one Codex implementation.
- Changed exactly the three allowed files; no source transfer or commit.
- Repeated verification: `npm test` 46/46; `git diff --check` PASS.
- Claude initial verdict required a format retry. The retry remained
  contract-invalid: finding evidence used `test_result` without its mandatory
  structured `command` block.
- No deterministic policy decision was admitted; the diff is not accepted and
  transfer is prohibited.
- Source `/home/stanislav/projects/home-agent-factory` remains clean at
  `8985b8e`.
- Root guard and Telegram plugin remain uninstalled research artifacts.
- Gateway, systemd, cron, push, deploy and unattended execution were untouched.
- Run evidence:
  `/home/stanislav/agent-runs/orchestrator-worktrees/manual-pilot-001-capability-grant-run`.
