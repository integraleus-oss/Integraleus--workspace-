#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="${OPENCLAW_TOKEN_LIMIT_STATE:-memory/heartbeat-token-limits-state.json}"
CODEX_5H_WARN="${CODEX_5H_WARN:-20}"
CODEX_WEEK_WARN="${CODEX_WEEK_WARN:-15}"
SESSION_CONTEXT_WARN="${SESSION_CONTEXT_WARN:-80}"
LOG_LIMIT="${LOG_LIMIT:-300}"
CLAUDE_USAGE_PROBE="${CLAUDE_USAGE_PROBE:-1}"
CLAUDE_5H_USED_WARN="${CLAUDE_5H_USED_WARN:-80}"
CLAUDE_WEEK_USED_WARN="${CLAUDE_WEEK_USED_WARN:-85}"

mkdir -p "$(dirname "$STATE_FILE")"
if [[ ! -f "$STATE_FILE" ]]; then
  printf '{"seenLogHashes":[]}\n' >"$STATE_FILE"
fi

warn=0
tmp_state="$(mktemp)"
trap 'rm -f "$tmp_state"' EXIT

echo "Token/limit heartbeat check:"

models_status="$(timeout 30 openclaw models status 2>&1 || true)"
usage_line="$(printf '%s\n' "$models_status" | grep -E '(openai-codex|openai) usage:' | tail -1 || true)"
if [[ -n "$usage_line" ]]; then
  five_left="$(printf '%s\n' "$usage_line" | sed -nE 's/.*5h ([0-9]+)% left.*/\1/p')"
  week_left="$(printf '%s\n' "$usage_line" | sed -nE 's/.*Week ([0-9]+)% left.*/\1/p')"
  five_reset="$(printf '%s\n' "$usage_line" | sed -E 's/.*5h [0-9]+% left[[:space:]]*//; s/[[:space:]]*Week .*//' | xargs || true)"
  week_reset="$(printf '%s\n' "$usage_line" | sed -nE 's/.*Week [0-9]+% left[[:space:]]*(.*)$/\1/p' | xargs || true)"

  echo "codex_usage: 5h=${five_left:-unknown}% reset='${five_reset:-unknown}' week=${week_left:-unknown}% reset='${week_reset:-unknown}'"
  if [[ -n "${five_left:-}" && "$five_left" -lt "$CODEX_5H_WARN" ]]; then
    echo "WARN: Codex 5h usage window is low: ${five_left}% left (<${CODEX_5H_WARN}%)."
    warn=1
  fi
  if [[ -n "${week_left:-}" && "$week_left" -lt "$CODEX_WEEK_WARN" ]]; then
    echo "WARN: Codex weekly usage window is low: ${week_left}% left (<${CODEX_WEEK_WARN}%)."
    warn=1
  fi
else
  echo "codex_usage: not exposed by 'openclaw models status'; using per-account Codex app-server check below."
fi

if [[ "${CODEX_ACCOUNT_AUTO_SWITCH:-0}" == "1" ]]; then
  echo "codex_account_auto_switch: enabled"
else
  echo "codex_account_auto_switch: disabled (set CODEX_ACCOUNT_AUTO_SWITCH=1 to allow auth order changes)"
fi

account_switch_output="$(timeout 120 scripts/codex-account-limit-switch.mjs 2>&1 || true)"
if [[ -n "$account_switch_output" ]]; then
  printf '%s\n' "$account_switch_output"
  if grep -q '^WARN:' <<<"$account_switch_output"; then
    warn=1
  fi
else
  echo "WARN: Codex per-account switch check produced no output."
  warn=1
fi

sessions_json="$(timeout 30 openclaw sessions list --json --all-agents --active 1440 --limit all 2>/dev/null || true)"
if [[ -n "$sessions_json" && "$sessions_json" == \{* ]]; then
  high_sessions="$(
    printf '%s' "$sessions_json" |
      jq -r --argjson threshold "$SESSION_CONTEXT_WARN" '
        .sessions[]
        | select(.contextTokens and .totalTokens and .contextTokens > 0)
        | .ratio = ((.totalTokens / .contextTokens) * 100)
        | select(.ratio >= $threshold)
        | "\(.key) \(.selectedModel // .configuredModel // .modelProvider // "?")/\(.model // "?") \((.ratio * 10 | round / 10))% (\(.totalTokens)/\(.contextTokens))"
      ' 2>/dev/null || true
  )"
  if [[ -n "$high_sessions" ]]; then
    echo "WARN: active sessions over ${SESSION_CONTEXT_WARN}% context:"
    printf '%s\n' "$high_sessions" | sed 's/^/  - /'
    warn=1
  else
    echo "session_context: no active sessions over ${SESSION_CONTEXT_WARN}%."
  fi
else
  echo "WARN: could not read active OpenClaw sessions."
  warn=1
fi

claude_status="$(timeout 10 claude auth status 2>/dev/null || true)"
if [[ -n "$claude_status" && "$claude_status" == \{* ]]; then
  claude_logged="$(printf '%s' "$claude_status" | jq -r '.loggedIn // false' 2>/dev/null || echo false)"
  claude_sub="$(printf '%s' "$claude_status" | jq -r '.subscriptionType // "unknown"' 2>/dev/null || echo unknown)"
  echo "claude_auth: loggedIn=${claude_logged} subscription=${claude_sub}"
  if [[ "$claude_logged" != "true" ]]; then
    echo "WARN: Claude CLI is not logged in."
    warn=1
  fi
else
  echo "WARN: could not read Claude auth status."
  warn=1
fi

if [[ "$CLAUDE_USAGE_PROBE" == "1" && "$(command -v tmux || true)" != "" ]]; then
  claude_session="oc-claude-usage-$$"
  claude_usage="$(
    set +e
    tmux new-session -d -s "$claude_session" "cd '$PWD' && TERM=xterm-256color claude --no-chrome" >/dev/null 2>&1
    sleep 8
    tmux send-keys -t "$claude_session:0.0" -l -- "/usage" >/dev/null 2>&1
    tmux send-keys -t "$claude_session:0.0" Enter >/dev/null 2>&1
    sleep 8
    tmux capture-pane -t "$claude_session:0.0" -p -S - 2>/dev/null
    tmux kill-session -t "$claude_session" >/dev/null 2>&1
  )"
  tmux kill-session -t "$claude_session" >/dev/null 2>&1 || true

  claude_5h_used="$(printf '%s\n' "$claude_usage" | awk '
    /Current session/ {in_session=1; next}
    in_session && /% used/ {gsub(/[^0-9]/, "", $0); print $0; exit}
  ')"
  claude_5h_reset="$(printf '%s\n' "$claude_usage" | awk '
    /Current session/ {in_session=1; next}
    in_session && /Resets/ {sub(/^[[:space:]]*/, "", $0); print; exit}
  ')"
  claude_week_used="$(printf '%s\n' "$claude_usage" | awk '
    /Current week/ {in_week=1; next}
    in_week && /% used/ {gsub(/[^0-9]/, "", $0); print $0; exit}
  ')"
  claude_week_reset="$(printf '%s\n' "$claude_usage" | awk '
    /Current week/ {in_week=1; next}
    in_week && /Resets/ {sub(/^[[:space:]]*/, "", $0); print; exit}
  ')"

  if [[ -n "${claude_5h_used:-}" || -n "${claude_week_used:-}" ]]; then
    echo "claude_usage: 5h_used=${claude_5h_used:-unknown}% reset='${claude_5h_reset:-unknown}' week_used=${claude_week_used:-unknown}% reset='${claude_week_reset:-unknown}'"
    if [[ -n "${claude_5h_used:-}" && "$claude_5h_used" -ge "$CLAUDE_5H_USED_WARN" ]]; then
      echo "WARN: Claude 5h usage window is high: ${claude_5h_used}% used (>=${CLAUDE_5H_USED_WARN}%)."
      warn=1
    fi
    if [[ -n "${claude_week_used:-}" && "$claude_week_used" -ge "$CLAUDE_WEEK_USED_WARN" ]]; then
      echo "WARN: Claude weekly usage window is high: ${claude_week_used}% used (>=${CLAUDE_WEEK_USED_WARN}%)."
      warn=1
    fi
  else
    echo "WARN: could not read Claude /usage via tmux probe."
    warn=1
  fi
elif [[ "$CLAUDE_USAGE_PROBE" == "1" ]]; then
  echo "WARN: tmux is not available for Claude /usage probe."
  warn=1
fi

logs="$(
  timeout 30 openclaw logs --plain --limit "$LOG_LIMIT" 2>/dev/null |
    grep -Ei 'rate_limit|subscription usage limit|Next reset|refresh_token_reused|fallback|context-overflow|anthropic|claude' |
    grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}T' |
    grep -Ev '^[[:space:]]*(-|•|[0-9]+[.)])[[:space:]]' |
    grep -Eiv '^[0-9T:+.-]+ info (Fallbacks \([0-9]+\):|- |gateway: auto-enabled plugins|agent model:|anthropic plugin config present)' || true
)"
if [[ -n "$logs" ]]; then
  old_hashes="$(jq -r '.seenLogHashes[]? // empty' "$STATE_FILE" 2>/dev/null || true)"
  new_events=""
  new_hashes=""
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    hash="$(printf '%s' "$line" | sha256sum | awk '{print $1}')"
    if ! grep -qxF "$hash" <<<"$old_hashes"; then
      new_events+="${line}"$'\n'
      new_hashes+="${hash}"$'\n'
    fi
  done <<<"$logs"

  if [[ -n "$new_events" ]]; then
    echo "WARN: new limit/auth/fallback/context log events:"
    printf '%s' "$new_events" | tail -20 | while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      ts="$(printf '%s' "$line" | awk '{print $1}')"
      kind="matched_event"
      if grep -qi 'subscription usage limit' <<<"$line"; then
        kind="codex_subscription_limit"
      elif grep -qi 'refresh_token_reused' <<<"$line"; then
        kind="codex_refresh_token_reused"
      elif grep -qi 'context-overflow\|context_overflow' <<<"$line"; then
        kind="context_overflow"
      elif grep -qi 'rate_limit' <<<"$line"; then
        kind="rate_limit"
      elif grep -qi 'fallback' <<<"$line"; then
        kind="model_fallback"
      elif grep -qi 'anthropic' <<<"$line"; then
        kind="anthropic_event"
      elif grep -qi 'claude' <<<"$line"; then
        kind="claude_event"
      fi
      summary="$(printf '%s' "$line" | sed -E 's/.*rawErrorPreview":"([^"]+)".*/\1/; s/.*errorPreview":"([^"]+)".*/\1/; s/.*error":"([^"]+)".*/\1/; s/[[:space:]]+/ /g; s/\\n/ /g' | cut -c1-180)"
      printf '  - %s %s: %s\n' "$ts" "$kind" "$summary"
    done
    warn=1
  else
    echo "logs: no new matching limit/auth/fallback/context events."
  fi

  {
    printf '%s\n' "$old_hashes"
    printf '%s\n' "$new_hashes"
  } | awk 'NF && !seen[$0]++' | tail -200 |
    jq -R -s --arg checkedAt "$(date -Is)" '{lastCheckedAt:$checkedAt, seenLogHashes:(split("\n") | map(select(length > 0)))}' >"$tmp_state"
  mv "$tmp_state" "$STATE_FILE"
else
  echo "logs: no matching limit/auth/fallback/context events in last ${LOG_LIMIT} lines."
fi

if [[ "$warn" -eq 1 ]]; then
  exit 1
fi
