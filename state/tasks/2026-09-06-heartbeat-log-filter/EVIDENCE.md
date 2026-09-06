# Evidence: heartbeat log-filter fix

Status: SUCCEEDED

## Cause

- Informational `info auto-reply/agent-turn-timing` records include internal
  stage names such as `fallback_prepare_harness` and
  `fallback_resolve_runtime`.
- The broad keyword matcher interpreted those stage names as actual model
  fallback events.

## Change

- `scripts/heartbeat-token-limits.sh` now excludes only timestamped
  `info auto-reply/agent-turn-timing` records before warning classification.
- Real warning/error records containing fallback, rate-limit, auth, or context
  signals remain eligible.
- Added `scripts/test_heartbeat_log_filter.sh` regression coverage.

## Verification

- Bash syntax checks: PASS.
- Regression fixture: `HEARTBEAT_LOG_FILTER_TEST_OK`; timing record excluded,
  genuine fallback and context-overflow records retained.
- `git diff --check`: PASS.
- Full `scripts/heartbeat-token-limits.sh` with a fresh isolated state file:
  exit 0.
- Full output: `heartbeat-after-fix.log`.
- Result: `logs: no matching limit/auth/fallback/context events in last 300 lines.`
- Both Codex OAuth profiles were checked; no auth-order change was needed.
- No queue mutation, message replay, Gateway restart, or auth-order change.
