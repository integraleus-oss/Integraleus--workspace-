#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${OPENCLAW_MEMORY_BACKUP_DIR:-$ROOT/backups}"
DATABASE_URL="${OPENCLAW_MEMORY_DATABASE_URL:-postgresql://openclaw_memory:openclaw_memory_dev@127.0.0.1:55432/openclaw_memory}"
STAMP="$(date +%Y%m%dT%H%M%S%z)"
OUT="$BACKUP_DIR/openclaw-memory-$STAMP.dump"

mkdir -p "$BACKUP_DIR"
pg_dump --format=custom --file="$OUT" "$DATABASE_URL"
sha256sum "$OUT" > "$OUT.sha256"
echo "BACKUP_OK $OUT"

