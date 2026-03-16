#!/bin/bash
# Dashboard metrics collector - runs every 10 min via system crontab
# Collects system metrics and pushes JSON to hosting

set -e

HOSTING="u1920081@server203.hosting.reg.ru"
REMOTE_PATH="~/www/integraleus.ru/api-status.json"
TMP="/tmp/dashboard-metrics.json"

# System metrics
CPU=$(top -bn1 | grep 'Cpu(s)' | awk '{printf "%.1f", 100-$8}')
RAM_USED=$(free -m | awk 'NR==2{print $3}')
RAM_TOTAL=$(free -m | awk 'NR==2{print $2}')
RAM_PCT=$(free -m | awk 'NR==2{printf "%.0f", $3*100/$2}')
DISK_USED=$(df -BG / | awk 'NR==2{gsub("G","",$3); print $3}')
DISK_TOTAL=$(df -BG / | awk 'NR==2{gsub("G","",$2); print $2}')
DISK_PCT=$(df / | awk 'NR==2{gsub("%","",$5); print $5}')
UPTIME_SEC=$(cat /proc/uptime | awk '{printf "%.0f", $1}')
UPTIME_DAYS=$((UPTIME_SEC / 86400))
UPTIME_HOURS=$(( (UPTIME_SEC % 86400) / 3600 ))

# OpenClaw sessions
SESSIONS=$(openclaw status 2>/dev/null | grep -c '│ agent' || echo "0")

# Server checks
GARDEN_OK=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@31.128.32.68 'echo 1' 2>/dev/null || echo "0")
VPN_OK=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@157.22.180.83 'echo 1' 2>/dev/null || echo "0")
DOCKER_VPN=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@157.22.180.83 'docker ps --format "{{.Names}}:{{.Status}}" 2>/dev/null | head -1' 2>/dev/null || echo "none")

# UFW
UFW_STATUS=$(sudo /usr/sbin/ufw status 2>/dev/null | head -1 || echo "unknown")

# Timestamp
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TS_MSK=$(TZ=Europe/Moscow date +"%d.%m %H:%M")

# Build JSON
cat > "$TMP" << JSONEOF
{
  "updated": "$TS",
  "updated_msk": "$TS_MSK",
  "system": {
    "cpu_pct": $CPU,
    "ram_used_mb": $RAM_USED,
    "ram_total_mb": $RAM_TOTAL,
    "ram_pct": $RAM_PCT,
    "disk_used_gb": $DISK_USED,
    "disk_total_gb": $DISK_TOTAL,
    "disk_pct": $DISK_PCT,
    "uptime_days": $UPTIME_DAYS,
    "uptime_hours": $UPTIME_HOURS
  },
  "openclaw": {
    "version": "2026.3.13",
    "sessions": $SESSIONS,
    "telegram": true,
    "discord": true
  },
  "servers": {
    "main": {"status": "online", "ip": "155.212.227.115"},
    "garden": {"status": "$([ "$GARDEN_OK" = "1" ] && echo online || echo offline)", "ip": "31.128.32.68"},
    "vpn": {"status": "$([ "$VPN_OK" = "1" ] && echo online || echo offline)", "ip": "157.22.180.83", "docker": "$DOCKER_VPN"}
  },
  "security": {
    "ufw": "$UFW_STATUS",
    "ssh": "key-only"
  }
}
JSONEOF

# Upload to hosting
scp -o StrictHostKeyChecking=no -q "$TMP" "$HOSTING:$REMOTE_PATH"
ssh -o StrictHostKeyChecking=no -q "$HOSTING" "chmod 644 $REMOTE_PATH"

# Upload events log
EVENTS="/root/.openclaw/workspace/agents/main/data/events.json"
if [ -f "$EVENTS" ]; then
  scp -o StrictHostKeyChecking=no -q "$EVENTS" "$HOSTING:~/www/integraleus.ru/api-events.json"
  ssh -o StrictHostKeyChecking=no -q "$HOSTING" "chmod 644 ~/www/integraleus.ru/api-events.json"
fi

rm -f "$TMP"
