#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${OPENCLAW_MEMORY_BACKUP_DIR:-$ROOT/backups}"
DATABASE_URL="${OPENCLAW_MEMORY_BACKUP_DATABASE_URL:-${OPENCLAW_MEMORY_DATABASE_URL:-postgresql://openclaw_memory:openclaw_memory_dev@127.0.0.1:55432/openclaw_memory}}"
REAL_DATA="${OPENCLAW_MEMORY_REAL_DATA:-0}"
AGE_RECIPIENT="${OPENCLAW_MEMORY_BACKUP_AGE_RECIPIENT:-}"
STAMP="$(date +%Y%m%dT%H%M%S%z)"
OUT="$BACKUP_DIR/openclaw-memory-$STAMP.dump"

mkdir -p "$BACKUP_DIR"
if [[ "$REAL_DATA" == "1" && -z "$AGE_RECIPIENT" ]]; then
  echo "Refusing real-data plaintext backup; set OPENCLAW_MEMORY_BACKUP_AGE_RECIPIENT" >&2
  exit 2
fi

pg_dump --format=custom --file="$OUT" "$DATABASE_URL"

if [[ -n "$AGE_RECIPIENT" ]]; then
  command -v age >/dev/null || {
    echo "age command is required for encrypted backup" >&2
    rm -f "$OUT"
    exit 2
  }
  age -r "$AGE_RECIPIENT" -o "$OUT.age" "$OUT"
  (cd "$(dirname "$OUT.age")" && sha256sum "$(basename "$OUT.age")" > "$(basename "$OUT.age").sha256")
  rm -f "$OUT"
  echo "BACKUP_OK encrypted $OUT.age"
else
  (cd "$(dirname "$OUT")" && sha256sum "$(basename "$OUT")" > "$(basename "$OUT").sha256")
  echo "BACKUP_OK plaintext-test-only $OUT"
fi
