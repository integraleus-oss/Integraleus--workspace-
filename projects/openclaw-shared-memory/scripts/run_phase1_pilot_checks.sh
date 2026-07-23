#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADMIN_URL="${OPENCLAW_MEMORY_PHASE1_ADMIN_DATABASE_URL:-${OPENCLAW_MEMORY_DATABASE_URL:-}}"
WORK_DIR="${OPENCLAW_MEMORY_PHASE1_WORK_DIR:-$(mktemp -d)}"
KEEP_WORK_DIR="${OPENCLAW_MEMORY_PHASE1_KEEP_WORK_DIR:-0}"
RUN_CONTAINER_CHECK="${OPENCLAW_MEMORY_PHASE1_CONTAINER_CHECK:-0}"
PYTHON_BIN="${PYTHON:-python3}"

cleanup() {
  if [[ "$KEEP_WORK_DIR" != "1" ]]; then
    rm -rf "$WORK_DIR"
  fi
}
trap cleanup EXIT

if [[ -z "$ADMIN_URL" ]]; then
  echo "Set OPENCLAW_MEMORY_PHASE1_ADMIN_DATABASE_URL or OPENCLAW_MEMORY_DATABASE_URL" >&2
  exit 2
fi

DB_NAME="${ADMIN_URL##*/}"
DB_NAME="${DB_NAME%%\?*}"
if [[ "$DB_NAME" != *phase1* && "$DB_NAME" != *drill* && "$DB_NAME" != *test* && "$DB_NAME" != *scratch* ]]; then
  echo "Refusing Phase 1 checks against non-disposable database: $DB_NAME" >&2
  exit 2
fi

mkdir -p "$WORK_DIR/mirror" "$WORK_DIR/backups"

cd "$ROOT"

echo "PHASE1_STEP role_scoped_local_pilot"
OPENCLAW_MEMORY_PHASE1_ADMIN_DATABASE_URL="$ADMIN_URL" \
  "$PYTHON_BIN" scripts/run_phase1_local_pilot.py

echo "PHASE1_STEP mirror_allowlist_export"
OPENCLAW_MEMORY_DATABASE_URL="$ADMIN_URL" \
OPENCLAW_MEMORY_MIRROR_DIR="$WORK_DIR/mirror" \
OPENCLAW_MEMORY_MIRROR_PRIVACY_CLASSES="shared_safe" \
  "$PYTHON_BIN" scripts/export_markdown_mirror.py
test -f "$WORK_DIR/mirror/INDEX.md"
if rg -q "external_forbidden|personal_stanislav|must not be visible|must not be listed" "$WORK_DIR/mirror"; then
  echo "Mirror export leaked forbidden pilot content" >&2
  exit 1
fi

echo "PHASE1_STEP plaintext_test_backup"
OPENCLAW_MEMORY_DATABASE_URL="$ADMIN_URL" \
OPENCLAW_MEMORY_BACKUP_DATABASE_URL="${OPENCLAW_MEMORY_BACKUP_DATABASE_URL:-$ADMIN_URL}" \
OPENCLAW_MEMORY_BACKUP_DIR="$WORK_DIR/backups" \
OPENCLAW_MEMORY_REAL_DATA=0 \
  scripts/backup_memory.sh
BACKUP_FILE="$(find "$WORK_DIR/backups" -maxdepth 1 -type f -name 'openclaw-memory-*.dump' | head -n 1)"
if [[ -z "$BACKUP_FILE" ]]; then
  echo "Backup file not found" >&2
  exit 1
fi

echo "PHASE1_STEP restore_drill"
DRILL_URL="${OPENCLAW_MEMORY_DRILL_DATABASE_URL:-${ADMIN_URL%/*}/${DB_NAME}_drill}"
OPENCLAW_MEMORY_DATABASE_URL="$ADMIN_URL" \
OPENCLAW_MEMORY_DRILL_DATABASE_URL="$DRILL_URL" \
  scripts/restore_drill.sh "$BACKUP_FILE"

if [[ "$RUN_CONTAINER_CHECK" == "1" ]]; then
  echo "PHASE1_STEP local_container_stop_start"
  command -v docker >/dev/null || {
    echo "docker command is required for container stop/start check" >&2
    exit 2
  }
  docker compose -f docker-compose.yml stop postgres
  if pg_isready -d "$ADMIN_URL" >/dev/null 2>&1; then
    echo "Database stayed reachable after local container stop" >&2
    docker compose -f docker-compose.yml start postgres >/dev/null
    exit 1
  fi
  docker compose -f docker-compose.yml start postgres
  for _ in $(seq 1 30); do
    if pg_isready -d "$ADMIN_URL" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  pg_isready -d "$ADMIN_URL" >/dev/null
else
  echo "PHASE1_STEP local_container_stop_start skipped set OPENCLAW_MEMORY_PHASE1_CONTAINER_CHECK=1"
fi

echo "PHASE1_PILOT_CHECKS_OK work_dir=$WORK_DIR"
