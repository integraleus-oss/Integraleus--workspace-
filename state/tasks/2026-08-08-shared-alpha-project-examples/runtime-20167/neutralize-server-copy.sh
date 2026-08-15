#!/usr/bin/env bash
set -euo pipefail

task_root="$(cd "$(dirname "$0")" && pwd)"
omx="$task_root/source/server/Bachat_KNS/Bachat_KNS/Bachat_KNS.omx"

perl -0pi -e '
  s/anonimous-can-write="true"/anonimous-can-write="false"/g;
  s/write-values-on-activation="true"/write-values-on-activation="false"/g;
  s/(<srv:modbus-(?:tcp|rtu)-master\b[^>]*\bactive=")true(")/$1false$2/g;
  s{<srv:modbus-(tcp|rtu)-master\b(?![^>]*\bactive=)([^>]*)>}{<srv:modbus-$1-master$2 active="false">}g;
  s/192\.168\.13\./192.0.2./g;
' "$omx"

if rg -n 'anonimous-can-write="true"|write-values-on-activation="true"|<srv:modbus-(tcp|rtu)-master[^>]*active="true"|192\.168\.13\.' "$omx"; then
  echo "Neutralization validation failed" >&2
  exit 1
fi

rg -n 'anonimous-can-write="false"|write-values-on-activation="false"|<srv:modbus-(tcp|rtu)-master[^>]*active="false"|192\.0\.2\.' "$omx"
