#!/usr/bin/env bash
set -euo pipefail

task_root="$(cd "$(dirname "$0")" && pwd)"
project_root="$task_root/source/hmi"
evidence_root="$task_root/evidence"
display_id=":132"

mkdir -p "$evidence_root"
mkdir -p "$task_root/xdg/config" "$task_root/xdg/data" "$task_root/xdg/cache"
Xvfb "$display_id" -screen 0 1600x1000x24 >"$evidence_root/designer-xvfb.log" 2>&1 &
xvfb_pid=$!

cleanup() {
  kill "${designer_pid:-}" >/dev/null 2>&1 || true
  kill "$xvfb_pid" >/dev/null 2>&1 || true
  wait "${designer_pid:-}" >/dev/null 2>&1 || true
  wait "$xvfb_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 1
cd "$project_root"
DISPLAY="$display_id" XDG_RUNTIME_DIR="/run/user/$(id -u)" \
  XDG_CONFIG_HOME="$task_root/xdg/config" \
  XDG_DATA_HOME="$task_root/xdg/data" \
  XDG_CACHE_HOME="$task_root/xdg/cache" \
  QTWEBENGINE_DISABLE_SANDBOX=1 \
  /usr/local/bin/alpha.hmi.designer kns.hmi \
  >"$evidence_root/hmi-designer.log" 2>&1 &
designer_pid=$!

sleep 8
DISPLAY="$display_id" xwininfo -root -tree >"$evidence_root/hmi-designer-window.txt"
sleep 25
DISPLAY="$display_id" scrot "$evidence_root/hmi-designer.png"
identify -format '%w %h %k %[mean]\n' "$evidence_root/hmi-designer.png" \
  >"$evidence_root/hmi-designer-image-check.txt"
ps -p "$designer_pid" -o pid=,stat=,etime=,cmd= \
  >"$evidence_root/hmi-designer-process.txt" || true
