# Security precheck: OS authorization guard

Approval: Telegram topic `2922`, message `3301`, 2026-08-17.
Risk: HIGH (system user, root-owned files, systemd service/socket, Gateway plugin activation).

## Allowed change

- Create locked system user/group `orchestrator-guard`.
- Install a root-owned local Unix-socket guard under `/opt/orchestrator-guard`.
- Install and start `orchestrator-guard.socket/service`.
- Install/enable the reviewed OpenClaw plugin and restart Gateway once.
- Run one foreground controlled pilot with no automatic commit, transfer, push, deploy, or cron.

## Security properties

- No TCP listener; Unix socket only.
- Guard checks `SO_PEERCRED` and admits only the current OpenClaw Gateway PID,
  executable/cmdline/cgroup, owner sender id, fixed Telegram account/channel/chat/topic,
  fresh message id/timestamp, exact canonical packet path, and SHA-256 digest.
- Guard owns nonce/replay state and launches at most one foreground child.
- Packet root and runner command are fixed allowlists; symlinks are rejected.
- Root-owned code/config are not writable by `stanislav` or the orchestrator child.
- Structured audit excludes token/nonce secrets.

## Stop conditions

- Independent review reports blocker/major.
- Peer PID, metadata, path, digest, TTL, replay, or process identity check fails.
- Tests, service hardening check, Gateway health, or pilot evidence fails.
