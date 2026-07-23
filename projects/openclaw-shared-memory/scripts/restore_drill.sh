#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/openclaw-memory.dump" >&2
  exit 2
fi

DUMP="$1"
DRILL_URL="${OPENCLAW_MEMORY_DRILL_DATABASE_URL:-postgresql://openclaw_memory:openclaw_memory_dev@127.0.0.1:55432/openclaw_memory_drill}"
PROD_URL="${OPENCLAW_MEMORY_DATABASE_URL:-}"
AGE_IDENTITY="${OPENCLAW_MEMORY_RESTORE_AGE_IDENTITY:-}"
RESTORE_INPUT="$DUMP"
TMP_DECRYPTED=""
DRILL_DB="${DRILL_URL##*/}"
DRILL_DB="${DRILL_DB%%\?*}"
MAINTENANCE_URL="${DRILL_URL%/*}/postgres"
SAFE_DRILL_URL="$(printf '%s' "$DRILL_URL" | sed -E 's#(postgres(ql)?://)[^/@]+@#\1<redacted>@#')"

if [[ ! -f "$DUMP" ]]; then
  echo "Dump not found: $DUMP" >&2
  exit 2
fi

if [[ -n "$PROD_URL" && "$DRILL_URL" == "$PROD_URL" ]]; then
  echo "Refusing restore drill: drill URL equals production URL" >&2
  exit 2
fi

if [[ "$DRILL_URL" != *"drill"* && "$DRILL_URL" != *"test"* && "$DRILL_URL" != *"scratch"* ]]; then
  echo "Refusing restore drill: target DB URL must contain drill, test, or scratch" >&2
  exit 2
fi

if [[ -f "$DUMP.sha256" ]]; then
  (cd "$(dirname "$DUMP")" && sha256sum -c "$(basename "$DUMP").sha256")
else
  echo "Missing checksum file: $DUMP.sha256" >&2
  exit 2
fi

if [[ "$DUMP" == *.age ]]; then
  command -v age >/dev/null || {
    echo "age command is required for encrypted restore drill" >&2
    exit 2
  }
  if [[ -z "$AGE_IDENTITY" ]]; then
    echo "Set OPENCLAW_MEMORY_RESTORE_AGE_IDENTITY for encrypted restore drill" >&2
    exit 2
  fi
  TMP_DECRYPTED="$(mktemp)"
  trap 'rm -f "$TMP_DECRYPTED"' EXIT
  age -d -i "$AGE_IDENTITY" -o "$TMP_DECRYPTED" "$DUMP"
  RESTORE_INPUT="$TMP_DECRYPTED"
fi

createdb --maintenance-db="$MAINTENANCE_URL" "$DRILL_DB" 2>/dev/null || true
pg_restore --clean --if-exists --dbname="$DRILL_URL" "$RESTORE_INPUT"
psql "$DRILL_URL" -v ON_ERROR_STOP=1 -c "SELECT count(*) AS records FROM memory_records;"
echo "RESTORE_DRILL_OK $SAFE_DRILL_URL"
