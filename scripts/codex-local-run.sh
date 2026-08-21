#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/codex-local-run.sh [options] -- "prompt"
  scripts/codex-local-run.sh [options] -- "prompt" < context.txt

Options:
  --cd DIR             Run Codex from DIR. Default: current directory.
  --read-only          Use read-only sandbox. Default.
  --write              Use workspace-write sandbox scoped to --cd DIR.
  --add-dir DIR        Add a bounded writable directory (repeatable).
  --danger             Use danger-full-access sandbox. Avoid unless explicitly approved.
  --model MODEL        Pass an explicit Codex model.
  --no-route-check     Skip OpenAI VPN route check.
  -h, --help           Show this help.

Purpose:
  Preferred OpenClaw helper for local user Codex. It unsets OpenClaw CODEX_HOME
  via /home/stanislav/.local/bin/codex-local, verifies login, checks that OpenAI
  traffic routes through the NL VPN, and runs a narrow codex exec in the target
  workspace.
EOF
}

workdir="$PWD"
sandbox="read-only"
model=""
route_check=1
add_dirs=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cd)
      [[ $# -ge 2 ]] || { echo "ERROR: --cd needs a directory" >&2; exit 2; }
      workdir="$2"
      shift 2
      ;;
    --read-only)
      sandbox="read-only"
      shift
      ;;
    --write)
      sandbox="workspace-write"
      shift
      ;;
    --add-dir)
      [[ $# -ge 2 ]] || { echo "ERROR: --add-dir needs a directory" >&2; exit 2; }
      add_dirs+=("$2")
      shift 2
      ;;
    --danger)
      sandbox="danger-full-access"
      shift
      ;;
    --model)
      [[ $# -ge 2 ]] || { echo "ERROR: --model needs a value" >&2; exit 2; }
      model="$2"
      shift 2
      ;;
    --no-route-check)
      route_check=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "ERROR: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$workdir" ]]; then
  echo "ERROR: workdir does not exist: $workdir" >&2
  exit 2
fi

codex_local="/home/stanislav/.local/bin/codex-local"
if [[ ! -x "$codex_local" ]]; then
  echo "ERROR: codex-local wrapper is missing or not executable: $codex_local" >&2
  exit 1
fi

login_status="$("$codex_local" login status 2>&1 || true)"
if ! grep -q "Logged in using ChatGPT" <<<"$login_status"; then
  echo "ERROR: local Codex is not logged in:" >&2
  echo "$login_status" >&2
  exit 1
fi

check_route() {
  local host="$1"
  local ip route

  ip="$(getent ahostsv4 "$host" | awk '{print $1; exit}')"
  if [[ -z "${ip:-}" ]]; then
    echo "ERROR: could not resolve $host" >&2
    return 1
  fi

  route="$(ip route get "$ip" 2>&1 || true)"
  if ! grep -q " dev awg0 " <<<"$route" || ! grep -q " src 10.8.1.19" <<<"$route"; then
    echo "ERROR: $host ($ip) is not routed through NL VPN awg0/src 10.8.1.19:" >&2
    echo "$route" >&2
    return 1
  fi
}

if [[ "$route_check" -eq 1 ]]; then
  check_route api.openai.com
  check_route chatgpt.com
  check_route auth.openai.com
fi

cmd=("$codex_local" exec --cd "$workdir" --sandbox "$sandbox" --skip-git-repo-check)
for add_dir in "${add_dirs[@]}"; do
  [[ -d "$add_dir" ]] || { echo "ERROR: add-dir does not exist: $add_dir" >&2; exit 2; }
  [[ ! -L "$add_dir" ]] || { echo "ERROR: add-dir must not be a symlink: $add_dir" >&2; exit 2; }
  resolved_add_dir="$(realpath "$add_dir")"
  [[ "$resolved_add_dir" == /tmp/* ]] || { echo "ERROR: add-dir must be below /tmp: $add_dir" >&2; exit 2; }
  cmd+=(--add-dir "$resolved_add_dir")
done
if [[ -n "$model" ]]; then
  cmd+=(--model "$model")
fi

exec "${cmd[@]}" "$@"
