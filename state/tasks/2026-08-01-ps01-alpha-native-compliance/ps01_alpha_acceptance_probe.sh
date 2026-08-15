#!/usr/bin/env bash
set -u

ROOT="/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731"
OUT_DIR="${ROOT}/logs/acceptance_probe_$(date +%Y%m%d_%H%M%S)"
PUBLIC_BASE="https://alpha-bpr.31.10.95.23.sslip.io/ps01-scada/build/index.html"

mkdir -p "$OUT_DIR"

{
  echo "# PS01 Alpha acceptance probe"
  echo
  echo "Timestamp: $(date --iso-8601=seconds)"
  echo
  echo "## Services"
  for svc in \
    alpha.server.service \
    alpha-bpr-ps01-simulator.service \
    alpha-bpr-ps01-bridge.service \
    alpha.historian.server.service \
    alpha.reports.service \
    alpha.security.service \
    alpha.security.useractivity.service \
    ps01-webviewer-root.service
  do
    printf -- "- %s: " "$svc"
    systemctl is-active "$svc" 2>&1 || true
  done

  echo
  echo "## Ports"
  ss -ltnp 2>/dev/null | grep -E ':18080|:4600|:5000|:62544' || true

  echo
  echo "## Public WebViewer endpoints"
  for entity in MainForm SetpointsForm PS01TrendsWindow PS01ArchiveWindow PS01AlarmsWindow ReportsForm; do
    url="${PUBLIC_BASE}?entity=${entity}"
    code="$(curl -k -sS -o /dev/null -w '%{http_code}' "$url" 2>/dev/null || echo FAIL)"
    echo "- ${entity}: ${code} ${url}"
  done

  echo
  echo "## Alpha.Historian"
  /opt/Automiq/Alpha.Historian/alpha.historian.cli --output-format csv stat > "${OUT_DIR}/historian_stat.csv" 2>&1
  hist_status=$?
  /opt/Automiq/Alpha.Historian/alpha.historian.cli config_status > "${OUT_DIR}/historian_config_status.txt" 2>&1
  hist_cfg_status=$?
  echo "- stat exit: ${hist_status}; evidence: ${OUT_DIR}/historian_stat.csv"
  echo "- config_status exit: ${hist_cfg_status}; evidence: ${OUT_DIR}/historian_config_status.txt"
  grep -E '^Instance.Version|^Config.Status|^Db.default.State|^Db.default.Content.DataMetrics.NumStored|^Db.default.Content.Proc.Insert.NumTotalFailures|^License.StateDesc' "${OUT_DIR}/historian_stat.csv" || true

  echo
  echo "## Alpha.Reports"
  reports_code="$(curl -sS -o "${OUT_DIR}/alpha_reports_root.html" -w '%{http_code}' http://127.0.0.1:5000/ 2>"${OUT_DIR}/alpha_reports_curl.err" || echo FAIL)"
  echo "- HTTP / status: ${reports_code}; evidence: ${OUT_DIR}/alpha_reports_root.html"
  systemctl status alpha.reports.service --no-pager --full > "${OUT_DIR}/alpha_reports_service.txt" 2>&1 || true
  journalctl -u alpha.reports.service --since '30 minutes ago' --no-pager > "${OUT_DIR}/alpha_reports_recent_journal.txt" 2>&1 || true
  grep -E 'Version|Подключение к базе|OPC UA|License received|No license|Changed license status|Hosting failed' "${OUT_DIR}/alpha_reports_recent_journal.txt" | tail -30 || true

  echo
  echo "## Alpha.Security"
  systemctl status alpha.security.service alpha.security.useractivity.service --no-pager --full > "${OUT_DIR}/alpha_security_services.txt" 2>&1 || true
  echo "- service evidence: ${OUT_DIR}/alpha_security_services.txt"
  echo "- role contract: ${ROOT}/config/security-roles.json"

  echo
  echo "## Static project evidence"
  for f in \
    "${ROOT}/PS01_FullAlphaPlatform.hmi" \
    "${ROOT}/objects/MainForm.omobj" \
    "${ROOT}/objects/SetpointsForm.omobj" \
    "${ROOT}/objects/PS01TrendsWindow.omobj" \
    "${ROOT}/objects/PS01ArchiveWindow.omobj" \
    "${ROOT}/objects/PS01AlarmsWindow.omobj" \
    "${ROOT}/objects/ReportsForm.omobj" \
    "${ROOT}/reports/ps01-alpha-reports.json" \
    "${ROOT}/config/alarm-matrix.csv" \
    "${ROOT}/config/historian-plan.json" \
    "${ROOT}/config/security-roles.json"
  do
    if [ -f "$f" ]; then
      sha="$(sha256sum "$f" | awk '{print $1}')"
      echo "- OK ${f} sha256=${sha}"
    else
      echo "- MISSING ${f}"
    fi
  done
} | tee "${OUT_DIR}/SUMMARY.md"

echo "$OUT_DIR"
