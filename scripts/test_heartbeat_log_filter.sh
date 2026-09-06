#!/usr/bin/env bash
set -euo pipefail

filter_logs() {
  grep -Ei 'rate_limit|subscription usage limit|Next reset|refresh_token_reused|fallback|context-overflow|anthropic|claude' |
    grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}T' |
    grep -Ev '^[^ ]+ info +auto-reply/agent-turn-timing ' |
    grep -Ev '^[[:space:]]*(-|•|[0-9]+[.)])[[:space:]]' |
    grep -Eiv '^[0-9T:+.-]+ info +(Fallbacks|Image fallbacks|Providers w/|- |gateway: auto-enabled plugins|agent model:|anthropic plugin config present|gateway/reload config change detected|Stored [A-Z0-9_]+ \(secret\))' || true
}

fixture='2026-09-06T11:29:51.788+03:00 info auto-reply/agent-turn-timing agent turn milestone stages=fallback_prepare_harness:1ms,fallback_resolve_runtime:0ms
2026-09-06T11:30:00.000+03:00 warn agent/model fallback activated after rate_limit
2026-09-06T11:31:00.000+03:00 error agent context-overflow detected'

actual="$(printf '%s\n' "$fixture" | filter_logs)"
if grep -q 'agent-turn-timing' <<<"$actual"; then
  echo 'FAIL: agent-turn-timing was not excluded' >&2
  exit 1
fi
grep -q 'fallback activated' <<<"$actual"
grep -q 'context-overflow detected' <<<"$actual"
echo 'HEARTBEAT_LOG_FILTER_TEST_OK'
