#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

readonly TASK_DIR="/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-09-05-openclaw-hang-remediation"
readonly LOG_FILE="$TASK_DIR/activation.log"

exec >>"$LOG_FILE" 2>&1

printf 'started_at=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
openclaw --version
openclaw config validate
timeout 180s systemctl --user restart openclaw-gateway.service
timeout 90s bash -c 'until systemctl --user is-active --quiet openclaw-gateway.service; do sleep 1; done'
openclaw --version
openclaw status --deep
printf 'completed_at=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
