#!/usr/bin/env bash
set -euo pipefail

result="/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-09-05-attempt-scoped-auth-profile/ACTIVATION_RESULT.txt"
exec >"${result}" 2>&1

date --iso-8601=seconds
/usr/bin/systemctl --user restart openclaw-gateway.service

for attempt in $(seq 1 30); do
  if /usr/bin/openclaw health >/tmp/openclaw-auth-profile-health.txt 2>&1; then
    echo "readiness_attempt=${attempt}"
    /usr/bin/systemctl --user show openclaw-gateway.service -p MainPID -p ActiveEnterTimestamp --no-pager
    /usr/bin/openclaw --version
    /usr/bin/openclaw status --deep
    exit 0
  fi
  sleep 1
done

echo "Gateway readiness timed out"
/usr/bin/systemctl --user status openclaw-gateway.service --no-pager
exit 1
