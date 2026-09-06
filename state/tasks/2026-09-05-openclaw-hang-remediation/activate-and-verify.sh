#!/usr/bin/env bash
set -Eeuo pipefail

task_dir="/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-09-05-openclaw-hang-remediation"
exec >"${task_dir}/activation.log" 2>&1

recovery_start() {
  if ! systemctl --user is-active --quiet openclaw-gateway.service; then
    openclaw gateway start
  fi
}
trap recovery_start EXIT

echo "ACTIVATION_STARTED $(date --iso-8601=seconds)"
openclaw config validate
openclaw doctor --fix --non-interactive --yes
openclaw gateway restart --force
sleep 8
openclaw --version
openclaw status --deep
openclaw logs --plain --limit 100 --timeout 30000
echo "ACTIVATION_FINISHED $(date --iso-8601=seconds)"
