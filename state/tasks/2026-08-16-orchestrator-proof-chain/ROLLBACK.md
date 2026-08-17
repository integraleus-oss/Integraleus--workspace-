# Rollback: OS authorization guard

1. Disable the OpenClaw plugin and restart Gateway normally.
2. Stop/disable `orchestrator-guard.socket` and `orchestrator-guard.service`.
3. Preserve audit/evidence, then remove only the explicitly installed unit files
   and `/opt/orchestrator-guard` after confirming paths.
4. Remove the locked `orchestrator-guard` user/group only if no files/processes remain.
5. Verify Gateway health and that no guard socket/process remains.

Rollback never removes task packets, source repositories, accepted diffs, or unrelated files.
