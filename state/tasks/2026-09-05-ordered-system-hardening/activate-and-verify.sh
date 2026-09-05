#!/usr/bin/env bash
set -Eeuo pipefail

task_dir="/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-09-05-ordered-system-hardening"
exec >"${task_dir}/activation.log" 2>&1

printf 'started_at=%s\n' "$(date --iso-8601=seconds)"
systemctl --user restart openclaw-gateway.service

ready=0
for attempt in $(seq 1 45); do
  if systemctl --user is-active --quiet openclaw-gateway.service &&
    timeout 15 openclaw status --deep --json >"${task_dir}/post-restart-status.json" 2>/dev/null &&
    jq -e '.health.ok == true and ([.health.channels.telegram.accounts[] | .connected == true] | all)' "${task_dir}/post-restart-status.json" >/dev/null; then
    ready=1
    printf 'ready_attempt=%s\n' "$attempt"
    break
  fi
  sleep 2
done

if (( ready == 0 )); then
  printf 'result=FAILED\n'
  systemctl --user status openclaw-gateway.service --no-pager -l || true
  exit 1
fi

openclaw --version
openclaw secrets audit --json >"${task_dir}/post-restart-secrets-audit.json"
openclaw security audit --json >"${task_dir}/post-restart-security-audit.json"
systemctl --user show openclaw-gateway.service -p MainPID -p MemoryCurrent -p ActiveEnterTimestamp
scripts/heartbeat-main-bounded.sh || true
printf 'result=SUCCEEDED\n'
printf 'finished_at=%s\n' "$(date --iso-8601=seconds)"
