#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
UPDATER="$SCRIPT_DIR/openclaw-transactional-update.sh"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf -- "$TEST_ROOT"' EXIT

make_mocks() {
  local case_dir="$1"
  mkdir -p "$case_dir/bin" "$case_dir/state"
  printf 'active\n' >"$case_dir/service-state"
  : >"$case_dir/calls"

  apply_mock "$case_dir/bin/openclaw" <<'MOCK'
#!/usr/bin/env bash
set -eu
printf 'openclaw %s\n' "$*" >>"$MOCK_CALLS"
case "${1:-} ${2:-}" in
  "backup create")
    for arg in "$@"; do
      if [[ "$arg" == *.tar.gz ]]; then printf 'backup\n' >"$arg"; fi
    done
    ;;
  "update --yes")
    if [[ "${MOCK_FAIL_UPDATE:-0}" == 1 ]]; then
      printf 'inactive\n' >"$MOCK_SERVICE_STATE"
      exit 42
    fi
    ;;
  "gateway restart") printf 'active\n' >"$MOCK_SERVICE_STATE" ;;
  "gateway start") printf 'active\n' >"$MOCK_SERVICE_STATE" ;;
esac
MOCK

  apply_mock "$case_dir/bin/systemctl" <<'MOCK'
#!/usr/bin/env bash
set -eu
if [[ "$*" == *"is-active"* ]] && [[ "$(cat "$MOCK_SERVICE_STATE")" == active ]]; then exit 0; fi
exit 3
MOCK

  apply_mock "$case_dir/bin/timeout" <<'MOCK'
#!/usr/bin/env bash
set -eu
shift
exec "$@"
MOCK
}

apply_mock() {
  local path="$1"
  shift
  # Test fixture creation is intentionally local and ephemeral.
  sed 's/^+//' >"$path"
  chmod +x "$path"
}

run_case() {
  local name="$1" fail_update="$2" dry_run="$3" case_dir rc=0
  case_dir="$TEST_ROOT/$name"
  make_mocks "$case_dir"
  local args=()
  if [[ "$dry_run" == 1 ]]; then args+=(--dry-run); fi
  MOCK_CALLS="$case_dir/calls" \
  MOCK_SERVICE_STATE="$case_dir/service-state" \
  MOCK_FAIL_UPDATE="$fail_update" \
  PATH="$case_dir/bin:$PATH" \
  OPENCLAW_UPDATER_TEST_MODE=1 \
  OPENCLAW_UPDATER_STATE_DIR="$case_dir/state" \
  OPENCLAW_UPDATER_OPENCLAW_BIN=openclaw \
  OPENCLAW_UPDATER_SYSTEMCTL_BIN=systemctl \
  OPENCLAW_UPDATER_TIMEOUT_BIN=timeout \
    "$UPDATER" "${args[@]}" || rc=$?
  printf '%s\n' "$rc"
}

success_rc="$(run_case success 0 0)"
[[ "${success_rc##*$'\n'}" == 0 ]]
success_calls="$TEST_ROOT/success/calls"
[[ "$(grep -c '^openclaw gateway restart --safe$' "$success_calls")" == 1 ]]
[[ "$(grep -c '^openclaw update --yes --no-restart' "$success_calls")" == 1 ]]
[[ "$(grep -c '^openclaw config validate$' "$success_calls")" == 2 ]]
[[ "$(grep -c '^openclaw backup create .*--verify' "$success_calls")" == 1 ]]
grep -q '^outcome=SUCCEEDED$' "$TEST_ROOT/success/state/latest.status"

failure_rc="$(run_case failure 1 0)"
[[ "${failure_rc##*$'\n'}" == 42 ]]
! grep -q '^openclaw gateway restart' "$TEST_ROOT/failure/calls"
[[ "$(grep -c '^openclaw gateway start$' "$TEST_ROOT/failure/calls")" == 1 ]]
grep -q '^outcome=FAILED$' "$TEST_ROOT/failure/state/latest.status"

dry_rc="$(run_case dry_run 0 1)"
[[ "${dry_rc##*$'\n'}" == 0 ]]
grep -q '^openclaw update --dry-run --no-restart' "$TEST_ROOT/dry_run/calls"
! grep -Eq '^openclaw gateway (restart|start)' "$TEST_ROOT/dry_run/calls"
grep -q '^dry_run=1$' "$TEST_ROOT/dry_run/state/latest.status"

printf 'PASS: transactional updater success, failure, and dry-run cases\n'
