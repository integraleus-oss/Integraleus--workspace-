#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/synology-openclaw-shared-memory"

rm -rf "$OUT"
mkdir -p "$OUT/migrations" "$OUT/data" "$OUT/backups" "$OUT/mirror"
cp "$ROOT/deploy/synology/docker-compose.synology.yml" "$OUT/docker-compose.yml"
cp "$ROOT/deploy/synology/.env.synology.example" "$OUT/.env.synology.example"
cp "$ROOT/deploy/synology/README.md" "$OUT/README.md"
cp "$ROOT/deploy/synology/RUNBOOK.md" "$OUT/RUNBOOK.md"
cp "$ROOT/deploy/synology/CHECKLIST.md" "$OUT/CHECKLIST.md"
cp "$ROOT/migrations/"*.sql "$OUT/migrations/"
echo "PACKAGE_OK $OUT"
