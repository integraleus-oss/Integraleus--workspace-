# Independent review: OpenClaw plugin and systemd boundary

Review the selected commit and only the listed plugin/systemd files for blocker
or major security defects. The Python root guard is separately accepted.

Threat model and required properties:

- Only a fresh inbound Telegram message from owner `109592643`, chat
  `-1004417478336`, topic `2922`, account `default` may authorize an action.
- PREPARE must bind the exact packet relative path and SHA-256 digest.
- RUN must bind the opaque prepared snapshot returned by the root guard.
- Authorization must be single-use and fail closed across mismatch, replay,
  timeout, plugin/Gateway restart, malformed guard output, or socket failure.
- The model/tool caller must not be able to fabricate trusted inbound metadata,
  choose a different snapshot, bypass the fixed packet root, or invoke the
  root guard from an arbitrary same-UID process.
- systemd must keep guard code/runtime root-owned and narrowly expose only the
  Unix socket needed by the active OpenClaw Gateway.
- No automatic commit, transfer, push, deploy, cron, or unattended execution.

Return `ACCEPT` only with zero blocker and zero major. List minor/nit findings
separately. Do not modify files.
