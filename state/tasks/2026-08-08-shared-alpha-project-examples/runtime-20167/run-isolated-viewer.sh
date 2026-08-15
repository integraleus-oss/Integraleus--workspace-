#!/usr/bin/env bash
set -euo pipefail

task_root="$(cd "$(dirname "$0")" && pwd)"
project_root="$task_root/source/hmi"
evidence_root="$task_root/evidence"
display_id=":131"
unit_name="alpha-20167-viewer"

mkdir -p "$evidence_root"
mkdir -p "$task_root/xdg-viewer/config" "$task_root/xdg-viewer/data" "$task_root/xdg-viewer/cache"
Xvfb "$display_id" -screen 0 1600x1000x24 >"$evidence_root/xvfb.log" 2>&1 &
xvfb_pid=$!

cleanup() {
  systemctl --user stop "$unit_name.service" >/dev/null 2>&1 || true
  kill "$xvfb_pid" >/dev/null 2>&1 || true
  wait "$xvfb_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 1
systemd-run --user --unit="$unit_name" --collect \
  --property=PrivateNetwork=yes \
  --property=IPAddressDeny=any \
  --property="WorkingDirectory=$project_root" \
  --setenv="DISPLAY=$display_id" \
  --setenv="XDG_RUNTIME_DIR=/run/user/$(id -u)" \
  --setenv="XDG_CONFIG_HOME=$task_root/xdg-viewer/config" \
  --setenv="XDG_DATA_HOME=$task_root/xdg-viewer/data" \
  --setenv="XDG_CACHE_HOME=$task_root/xdg-viewer/cache" \
  --setenv=QTWEBENGINE_DISABLE_SANDBOX=1 \
  /usr/local/bin/alpha.hmi.viewer build-safe/kns.ni.binom Main_GK_KNS

sleep 20
if [[ -f "$evidence_root/hmi-viewer.png" ]]; then
  mv -f "$evidence_root/hmi-viewer.png" "$evidence_root/hmi-viewer-previous.png"
fi
DISPLAY="$display_id" scrot "$evidence_root/hmi-viewer.png"
identify -format '%w %h %k %[mean]\n' "$evidence_root/hmi-viewer.png" \
  >"$evidence_root/hmi-viewer-image-check.txt"
systemctl --user show "$unit_name.service" \
  -p ActiveState -p SubState -p Result -p ExecMainStatus -p PrivateNetwork \
  >"$evidence_root/hmi-viewer-unit.txt"
journalctl --user -u "$unit_name.service" --no-pager \
  >"$evidence_root/hmi-viewer-journal.txt"
