#!/usr/bin/env bash
set -u

LOG="/home/stanislav/.openclaw/workspace/agents/main/state/openclaw-update-2026-06-19.log"

{
  echo "=== OpenClaw update job started: $(date '+%Y-%m-%d %H:%M:%S %Z (%z)') ==="
  echo

  echo "=== Pre-update versions ==="
  printf 'openclaw: '; openclaw --version 2>&1 || true
  printf 'codex: '; codex --version 2>&1 || true
  printf 'claude: '; claude --version 2>&1 || true
  printf 'node: '; node --version 2>&1 || true
  printf 'npm: '; npm --version 2>&1 || true
  npm list -g --depth=0 openclaw @openai/codex @anthropic-ai/claude-code npm 2>/dev/null || true
  echo

  echo "=== openclaw update ==="
  openclaw update
  UPDATE_RC=$?
  echo "openclaw update exit code: ${UPDATE_RC}"
  echo

  echo "=== openclaw doctor --fix ==="
  openclaw doctor --fix
  DOCTOR_RC=$?
  echo "openclaw doctor --fix exit code: ${DOCTOR_RC}"
  echo

  echo "=== openclaw logs --plain --limit 50 ==="
  openclaw logs --plain --limit 50
  LOGS_RC=$?
  echo "openclaw logs exit code: ${LOGS_RC}"
  echo

  echo "=== openclaw gateway restart ==="
  openclaw gateway restart
  RESTART_RC=$?
  echo "openclaw gateway restart exit code: ${RESTART_RC}"
  echo

  sleep 8

  echo "=== openclaw status --deep ==="
  openclaw status --deep
  STATUS_RC=$?
  echo "openclaw status --deep exit code: ${STATUS_RC}"
  echo

  echo "=== Post-update versions ==="
  printf 'openclaw: '; openclaw --version 2>&1 || true
  printf 'codex: '; codex --version 2>&1 || true
  printf 'claude: '; claude --version 2>&1 || true
  printf 'node: '; node --version 2>&1 || true
  printf 'npm: '; npm --version 2>&1 || true
  npm list -g --depth=0 openclaw @openai/codex @anthropic-ai/claude-code npm 2>/dev/null || true
  echo

  echo "=== Service checks ==="
  systemctl --user is-active openclaw-gateway.service 2>&1 || true
  systemctl --user is-enabled openclaw-gateway.service 2>&1 || true
  systemctl is-active docker containerd rustdesk ollama tailscaled 2>&1 || true
  docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1 || true
  tailscale status --peers=false 2>&1 || true
  systemctl --failed --no-pager 2>&1 || true
  echo

  echo "=== OpenClaw update job finished: $(date '+%Y-%m-%d %H:%M:%S %Z (%z)') ==="
  exit "${STATUS_RC}"
} >>"${LOG}" 2>&1

