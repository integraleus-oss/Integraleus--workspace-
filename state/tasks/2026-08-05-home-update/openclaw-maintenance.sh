#!/usr/bin/env bash
set -Eeuo pipefail

TASK_DIR="/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-05-home-update"
LOG="$TASK_DIR/openclaw-maintenance.log"

mkdir -p "$TASK_DIR"
exec > >(tee -a "$LOG") 2>&1

echo "=== OpenClaw maintenance started: $(date --iso-8601=seconds) ==="
echo "Before:"
openclaw --version || true

on_error() {
  local status=$?
  echo "ERROR: maintenance failed with status $status at $(date --iso-8601=seconds)"
  echo "Attempting to start gateway before exit..."
  openclaw gateway start || true
  exit "$status"
}
trap on_error ERR

echo "--- stopping gateway ---"
openclaw gateway stop || true
sleep 3

echo "--- installing openclaw@2026.7.1-2 ---"
sudo npm install -g openclaw@2026.7.1-2
hash -r

echo "After install:"
openclaw --version

echo "--- doctor --fix ---"
openclaw doctor --fix --non-interactive --yes

echo "--- recent logs before gateway start ---"
openclaw logs --plain --limit 50 || true

echo "--- starting gateway ---"
openclaw gateway start
sleep 8

echo "--- final status --deep ---"
openclaw status --deep

echo "=== OpenClaw maintenance completed: $(date --iso-8601=seconds) ==="
