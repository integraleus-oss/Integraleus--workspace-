# Independent review: Gateway authorization boundary

Review the current uncommitted changes for the owner-controlled foreground
orchestrator authorization boundary. Read only these files and their directly
used OpenClaw SDK types:

- `projects/orchestrator-auth-boundary/src/index.ts`
- `projects/orchestrator-auth-boundary/openclaw.plugin.json`
- `projects/orchestrator-auth-boundary/package.json`
- `state/tasks/2026-08-12-orchestrator-integration/openclaw_foreground_adapter.py`
- `state/tasks/2026-08-12-orchestrator-integration/tests/test_openclaw_foreground_adapter.py`
- `state/tasks/2026-08-16-orchestrator-proof-chain/TASK_PACKET.md`

Spec axis: verify trusted owner metadata, exact packet path/digest binding,
short TTL, single use, restart invalidation, atomic consume, replay resistance,
fail-closed behavior, and no autonomous commit/transfer/push/deploy capability.

Standards axis: check OpenClaw plugin API correctness, races/TOCTOU, unsafe path
handling, response parsing, secret/token exposure, cleanup, error handling, and
test gaps. Return ACCEPT only with zero blocker and zero major; otherwise REWORK
with precise file/line findings. Do not edit files.
