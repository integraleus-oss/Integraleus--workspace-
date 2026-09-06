#!/usr/bin/env bash
set -euo pipefail

task_dir="/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-09-05-openclaw-hang-remediation"
log="$task_dir/final-activation.log"
exec >"$log" 2>&1

printf 'started_at=%s\n' "$(date --iso-8601=seconds)"
systemctl --user restart openclaw-gateway.service

ready=0
for attempt in $(seq 1 30); do
  if systemctl --user is-active --quiet openclaw-gateway.service &&
    timeout 10 openclaw status --deep >/tmp/openclaw-final-status.txt 2>&1 &&
    grep -q 'Telegram.*OK' /tmp/openclaw-final-status.txt; then
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
systemctl --user show openclaw-gateway.service -p MainPID -p MemoryCurrent -p ActiveEnterTimestamp
bash /home/stanislav/.openclaw/workspace/agents/main/scripts/openclaw-codex-process-watch.sh || true
journalctl --user -u openclaw-gateway.service --since '-2 minutes' --no-pager |
  grep -Ei 'retry|drain|ERR_MODULE_NOT_FOUND|409 Conflict|requires capability consent' || true
printf 'result=SUCCEEDED\n'
printf 'finished_at=%s\n' "$(date --iso-8601=seconds)"
