#!/usr/bin/env bash
set -u -o pipefail

run_check() {
  local name="$1"
  local seconds="$2"
  shift 2
  printf 'CHECK_START %s\n' "$name"
  timeout --signal=TERM --kill-after=5 "$seconds" "$@"
  local status=$?
  if (( status == 0 )); then
    printf 'CHECK_OK %s\n' "$name"
    return 0
  fi
  printf 'CHECK_WARN %s exit=%s timeout_seconds=%s\n' "$name" "$status" "$seconds"
  return 1
}

failed=0
run_check codex_processes 30 scripts/openclaw-codex-process-watch.sh || failed=1
run_check execution_truth 30 python3 scripts/execution-truth-watch.py --root state/tasks || failed=1
run_check supervisor_recovery 60 python3 scripts/execution-supervisor-recover-all.py --root state/tasks || failed=1
run_check token_limits 180 scripts/heartbeat-token-limits.sh || failed=1
run_check gateway_status 30 openclaw status --deep || failed=1

if (( failed )); then
  printf 'HEARTBEAT_MAIN_WARN\n'
  exit 1
fi
printf 'HEARTBEAT_MAIN_OK\n'
