#!/usr/bin/env bash
set -euo pipefail

MAX_OLD_APP_SERVER_PARENTS="${MAX_OLD_APP_SERVER_PARENTS:-0}"
APP_SERVER_OLD_AGE_SECONDS="${APP_SERVER_OLD_AGE_SECONDS:-900}"
MAX_GATEWAY_ANON_BYTES="${MAX_GATEWAY_ANON_BYTES:-2147483648}"

gateway_pid="$(systemctl --user show openclaw-gateway.service -p MainPID --value 2>/dev/null || true)"
cgroup_path="/sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/app.slice/openclaw-gateway.service"
memory_current="$(cat "$cgroup_path/memory.current" 2>/dev/null || true)"
memory_anon="$(awk '$1 == "anon" { print $2 }' "$cgroup_path/memory.stat" 2>/dev/null || true)"
memory_file="$(awk '$1 == "file" { print $2 }' "$cgroup_path/memory.stat" 2>/dev/null || true)"

if [[ ! "$gateway_pid" =~ ^[1-9][0-9]*$ ]]; then
  echo "WARN: Gateway MainPID is unavailable; Codex child-process watch could not run."
  exit 1
fi

mapfile -t app_server_parents < <(
  ps -eo pid=,ppid=,pgid=,etimes=,rss=,args= |
    awk -v gateway_pid="$gateway_pid" '
      $2 == gateway_pid && $0 ~ /[/ ]codex .*app-server/ {
        printf "%s:%s:%s:%s\n", $1, $3, $4, $5
      }
    '
)

count="${#app_server_parents[@]}"
old_count=0
for process in "${app_server_parents[@]}"; do
  age="$(cut -d: -f3 <<<"$process")"
  if [[ "$age" =~ ^[0-9]+$ ]] && (( age >= APP_SERVER_OLD_AGE_SECONDS )); then
    old_count=$((old_count + 1))
  fi
done
echo "codex_processes: app_server_parents=${count} old_parents=${old_count} gateway_pid=${gateway_pid} gateway_anon_bytes=${memory_anon:-unknown} gateway_file_cache_bytes=${memory_file:-unknown} gateway_total_bytes=${memory_current:-unknown}"
if (( count > 0 )); then
  printf '  - pid:pgid:age_seconds:rss_kib=%s\n' "${app_server_parents[@]}"
fi

warn=0
if (( old_count > MAX_OLD_APP_SERVER_PARENTS )); then
  echo "WARN: Codex app-server parent count older than ${APP_SERVER_OLD_AGE_SECONDS}s is ${old_count} (threshold ${MAX_OLD_APP_SERVER_PARENTS}); inspect active ownership before terminating exact process groups."
  warn=1
fi
if [[ "$memory_anon" =~ ^[0-9]+$ ]] && (( memory_anon > MAX_GATEWAY_ANON_BYTES )); then
  echo "WARN: Gateway cgroup anonymous memory is ${memory_anon} bytes (threshold ${MAX_GATEWAY_ANON_BYTES}); file cache is reported separately because it is reclaimable."
  warn=1
fi

exit "$warn"
