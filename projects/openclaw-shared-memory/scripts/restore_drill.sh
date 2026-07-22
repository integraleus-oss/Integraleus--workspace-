#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/openclaw-memory.dump" >&2
  exit 2
fi

DUMP="$1"
DRILL_URL="${OPENCLAW_MEMORY_DRILL_DATABASE_URL:-postgresql://openclaw_memory:openclaw_memory_dev@127.0.0.1:55432/openclaw_memory_drill}"

if [[ ! -f "$DUMP" ]]; then
  echo "Dump not found: $DUMP" >&2
  exit 2
fi

createdb "$DRILL_URL" 2>/dev/null || true
pg_restore --clean --if-exists --dbname="$DRILL_URL" "$DUMP"
psql "$DRILL_URL" -v ON_ERROR_STOP=1 -c "SELECT count(*) AS records FROM memory_records;"
echo "RESTORE_DRILL_OK $DRILL_URL"

