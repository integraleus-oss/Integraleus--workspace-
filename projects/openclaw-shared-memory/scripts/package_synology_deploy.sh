#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/synology-openclaw-shared-memory"
ARCHIVE="$ROOT/dist/synology-openclaw-shared-memory.tar.gz"

rm -rf "$OUT"
mkdir -p "$OUT/migrations" "$OUT/data" "$OUT/backups" "$OUT/mirror"
rm -f "$ARCHIVE" "$ARCHIVE.sha256"
cp "$ROOT/deploy/synology/docker-compose.synology.yml" "$OUT/docker-compose.yml"
cp "$ROOT/deploy/synology/.env.synology.example" "$OUT/.env.synology.example"
cp "$ROOT/deploy/synology/README.md" "$OUT/README.md"
cp "$ROOT/deploy/synology/RUNBOOK.md" "$OUT/RUNBOOK.md"
cp "$ROOT/deploy/synology/CHECKLIST.md" "$OUT/CHECKLIST.md"
cp "$ROOT/deploy/synology/ROLLBACK.md" "$OUT/ROLLBACK.md"
cp "$ROOT/migrations/"*.sql "$OUT/migrations/"
grep -q 'OPENCLAW_MEMORY_BIND_HOST.*:' "$OUT/docker-compose.yml" || {
  echo "PACKAGE_FAIL missing explicit bind host guard" >&2
  exit 1
}
grep -q '0\.0\.0\.0' "$OUT/docker-compose.yml" && {
  echo "PACKAGE_FAIL wildcard bind found" >&2
  exit 1
}
test -f "$OUT/ROLLBACK.md"
tar -czf "$ARCHIVE" -C "$ROOT/dist" "synology-openclaw-shared-memory"
(cd "$ROOT/dist" && sha256sum "$(basename "$ARCHIVE")" > "$(basename "$ARCHIVE").sha256")
echo "PACKAGE_OK $OUT"
echo "ARCHIVE_OK $ARCHIVE"
