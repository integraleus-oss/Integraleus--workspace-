# Independent review: OS orchestrator authorization guard

Review commit `a9a830e` read-only. Return ACCEPT only with zero blocker and zero
major; otherwise REWORK with file/line findings.

Spec axis:

- only a fresh owner message from Telegram account `default`, fixed chat/topic,
  owner sender id, and exact packet digest may start one run;
- root guard must verify the real OpenClaw Gateway peer PID/UID/executable/cmdline/cgroup;
- exact request shape, freshness, canonical non-symlink path, digest, and replay
  identity fail closed;
- root-owned snapshot is launched once in foreground; the old user-space adapter
  and direct hidden CLI flag fail closed outside the guard parent/cgroup;
- no token crosses argv; no cron, commit, transfer, push, or deploy capability;
- systemd unit minimizes root exposure and has a practical rollback.

Standards axis:

- OpenClaw hook/tool API correctness and actual inbound metadata availability;
- Unix socket framing, SO_PEERCRED use, PID/cgroup races, replay atomicity,
  TOCTOU, privilege drop, environment, subprocess and timeout behavior;
- root service attack surface, filesystem permissions and systemd hardening;
- evidence leakage, partial failure state, interruption and test gaps.

The change is not installed. Assess whether it is safe to install for one
controlled pilot. Do not edit files.
