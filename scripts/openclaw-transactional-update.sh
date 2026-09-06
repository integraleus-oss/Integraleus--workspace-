#!/usr/bin/env bash
# Transactional OpenClaw updater. Run from an external managed job, never from
# the Gateway process tree whose availability it protects.
set -Eeuo pipefail

umask 077

readonly SCRIPT_NAME="${0##*/}"
readonly DEFAULT_STATE_DIR="/home/stanislav/.openclaw/state/transactional-update"
STATE_DIR="${OPENCLAW_UPDATER_STATE_DIR:-$DEFAULT_STATE_DIR}"
OPENCLAW_BIN="${OPENCLAW_UPDATER_OPENCLAW_BIN:-openclaw}"
SYSTEMCTL_BIN="${OPENCLAW_UPDATER_SYSTEMCTL_BIN:-systemctl}"
TIMEOUT_BIN="${OPENCLAW_UPDATER_TIMEOUT_BIN:-timeout}"
STEP_TIMEOUT="${OPENCLAW_UPDATER_STEP_TIMEOUT:-1800}"
DRY_RUN=0
TEST_MODE="${OPENCLAW_UPDATER_TEST_MODE:-0}"
WAS_RUNNING=0
FINAL_RESTART_ATTEMPTED=0
PHASE="initializing"
BACKUP_PATH=""
RUN_ID="$(date -u '+%Y%m%dT%H%M%SZ')-$$"
RUN_DIR=""
LOG_FILE=""
STATUS_FILE=""
LOCK_FILE=""

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [--dry-run] [--timeout SECONDS] [--state-dir PATH]

Updates OpenClaw without an implicit restart, validates configuration, creates
and verifies a pre-update backup, runs doctor, then performs exactly one final
Gateway restart when the service was running at entry.

  --dry-run          Validate and preview update/backup; change nothing.
  --timeout SECONDS  Per-step timeout (default: 1800).
  --state-dir PATH   Durable logs, status and backups directory.
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

is_positive_integer() {
  [[ "$1" =~ ^[1-9][0-9]*$ ]]
}

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --timeout)
      (($# >= 2)) || die "--timeout requires a value"
      STEP_TIMEOUT="$2"; shift 2 ;;
    --state-dir)
      (($# >= 2)) || die "--state-dir requires a value"
      STATE_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

is_positive_integer "$STEP_TIMEOUT" || die "timeout must be a positive integer"

mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"
RUN_DIR="$STATE_DIR/runs/$RUN_ID"
LOG_FILE="$RUN_DIR/update.log"
STATUS_FILE="$STATE_DIR/latest.status"
LOCK_FILE="$STATE_DIR/update.lock"
mkdir -p "$RUN_DIR" "$STATE_DIR/backups"
chmod 700 "$RUN_DIR" "$STATE_DIR/backups"
touch "$LOG_FILE"
chmod 600 "$LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

write_status() {
  local outcome="$1" rc="$2" tmp
  tmp="$RUN_DIR/status.tmp"
  {
    printf 'run_id=%s\n' "$RUN_ID"
    printf 'outcome=%s\n' "$outcome"
    printf 'phase=%s\n' "$PHASE"
    printf 'exit_code=%s\n' "$rc"
    printf 'dry_run=%s\n' "$DRY_RUN"
    printf 'gateway_was_running=%s\n' "$WAS_RUNNING"
    printf 'final_restart_attempted=%s\n' "$FINAL_RESTART_ATTEMPTED"
    printf 'backup_path=%s\n' "$BACKUP_PATH"
    printf 'log_file=%s\n' "$LOG_FILE"
    printf 'updated_at=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  } >"$tmp"
  chmod 600 "$tmp"
  mv -f "$tmp" "$RUN_DIR/status"
  cp "$RUN_DIR/status" "$STATUS_FILE.tmp"
  mv -f "$STATUS_FILE.tmp" "$STATUS_FILE"
}

gateway_is_running() {
  "$SYSTEMCTL_BIN" --user is-active --quiet openclaw-gateway.service
}

on_exit() {
  local rc=$? recovery_rc=0 outcome="FAILED"
  trap - EXIT

  if ((WAS_RUNNING == 1 && DRY_RUN == 0)) && ! gateway_is_running; then
    PHASE="gateway-recovery-start"
    printf 'Gateway is inactive during exit; attempting recovery start.\n'
    "$TIMEOUT_BIN" "${STEP_TIMEOUT}s" "$OPENCLAW_BIN" gateway start || recovery_rc=$?
    if ((recovery_rc != 0)); then
      printf 'ERROR: Gateway recovery start failed with exit code %s.\n' "$recovery_rc" >&2
      rc="$recovery_rc"
    fi
  fi

  if ((rc == 0)); then outcome="SUCCEEDED"; fi
  write_status "$outcome" "$rc"
  printf 'Outcome: %s (phase=%s, rc=%s)\n' "$outcome" "$PHASE" "$rc"
  exit "$rc"
}
trap on_exit EXIT

exec 9>"$LOCK_FILE"
flock -n 9 || die "another transactional update is already running"

command -v "$OPENCLAW_BIN" >/dev/null 2>&1 || die "OpenClaw executable not found"
command -v "$SYSTEMCTL_BIN" >/dev/null 2>&1 || die "systemctl executable not found"
command -v "$TIMEOUT_BIN" >/dev/null 2>&1 || die "timeout executable not found"

if gateway_is_running; then WAS_RUNNING=1; fi
write_status "RUNNING" 0

run_step() {
  local name="$1"
  shift
  PHASE="$name"
  write_status "RUNNING" 0
  printf '\n=== %s ===\n' "$name"
  "$TIMEOUT_BIN" "${STEP_TIMEOUT}s" "$@"
}

run_step "preflight-config-validation" "$OPENCLAW_BIN" config validate

PHASE="backup"
write_status "RUNNING" 0
printf '\n=== backup ===\n'
if ((DRY_RUN == 1)); then
  run_step "backup-dry-run" "$OPENCLAW_BIN" backup create --no-include-workspace --dry-run --json
else
  BACKUP_PATH="$STATE_DIR/backups/$RUN_ID.tar.gz"
  run_step "backup-create-verify" "$OPENCLAW_BIN" backup create \
    --no-include-workspace --verify --output "$BACKUP_PATH"
  [[ -s "$BACKUP_PATH" ]] || die "backup archive was not created: $BACKUP_PATH"
fi

if ((DRY_RUN == 1)); then
  run_step "update-dry-run" "$OPENCLAW_BIN" update --dry-run --no-restart --timeout "$STEP_TIMEOUT" --json
  PHASE="dry-run-complete"
  exit 0
fi

# The Gateway remains live on the old loaded code throughout installation.
run_step "update-no-restart" "$OPENCLAW_BIN" update --yes --no-restart --timeout "$STEP_TIMEOUT" --json
run_step "post-update-config-validation" "$OPENCLAW_BIN" config validate
run_step "post-update-doctor" "$OPENCLAW_BIN" doctor --fix --non-interactive --yes

if ((WAS_RUNNING == 1)); then
  PHASE="final-gateway-restart"
  FINAL_RESTART_ATTEMPTED=1
  write_status "RUNNING" 0
  printf '\n=== final-gateway-restart ===\n'
  "$TIMEOUT_BIN" "${STEP_TIMEOUT}s" "$OPENCLAW_BIN" gateway restart --safe
  run_step "post-restart-status" "$OPENCLAW_BIN" status --deep
  run_step "post-restart-logs" "$OPENCLAW_BIN" logs --plain --limit 50 --timeout 30000
else
  printf '\nGateway was inactive at entry; leaving it inactive.\n'
fi

PHASE="complete"
exit 0
