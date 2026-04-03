# HEARTBEAT.md

## System monitoring (rotate, don't do all every time)

### 1. SSH & Security (every 2-3 heartbeats)
- Check `last -5` for new logins
- Check sshd effective config hasn't changed: `sshd -T 2>/dev/null | grep -E 'passwordauth|permitroot'`
- Check for new users: `grep -E '/bin/(ba)?sh$' /etc/passwd`
- Check UFW status (use absolute path: `/usr/sbin/ufw status` or `/sbin/ufw status`; do not rely on `ufw` being in PATH)
- Check for new files in `/etc/ssh/sshd_config.d/`
- If anything changed since last check → alert user
- Important: in non-login shells `PATH` may omit `/usr/sbin` and `/sbin`; for admin tools (`ufw`, `iptables`, `sshd`) prefer absolute paths or `command -v` checks before concluding a tool is missing

### 2. OpenClaw health (every 2-3 heartbeats)
- Quick `openclaw status` — gateway reachable? Telegram OK?
- Any new sessions from unknown sources?
- Check error count in recent logs

### 2a. Telegram liveness (EVERY heartbeat — mandatory)
- Run `openclaw status --deep 2>&1 | grep -A2 'Telegram'` — check State column
- If State is NOT "OK":
  1. Restart gateway via `gateway restart`
  2. Alert user: "⚠️ Telegram был недоступен, перезапустил gateway."
- Also check: is the last Telegram session older than 2× heartbeat interval?
  - Get last telegram session age from `sessions_list` (filter kinds=["direct","group"], look for channel=telegram)
  - If no telegram sessions in recent activeMinutes AND user was recently active → this is suspicious but not actionable (user may just not be writing)
- Log telegram status to `memory/heartbeat-state.json` under `telegramHealth`
- Track consecutive failures: if 3+ heartbeats in a row Telegram is down → escalate alert

### 3. System changes (every 4-5 heartbeats)
- Check pending OS updates: `apt list --upgradable 2>/dev/null | wc -l`
- Disk usage: `df -h / | tail -1`
- Uptime / recent reboots

### 3a. Garden server monitoring (every 3-4 heartbeats)
Garden: root@31.128.32.68 (Beget VPS, no Docker)
Services: openclaw-gateway, fail2ban, ssh, NetworkManager
Known user IPs: 157.22.180.83, 31.10.95.23 (Станислав), 193.9.244.115, 79.104.12.133 (Билайн Томск)
Baseline SSH: permitrootlogin=without-password, passwordauthentication=no
Baseline users: root (/bin/bash), ops (/bin/bash)

Via SSH (`ssh -o ConnectTimeout=10 root@31.128.32.68 "..."`):
- **Security:** `last -5`, check for unknown IPs; `sshd -T | grep -E 'permitroot|passwordauth'`; `grep -E '/bin/(ba)?sh$' /etc/passwd`; UFW status via absolute path (`/usr/sbin/ufw status` or `/sbin/ufw status`)
- **Health:** `uptime`; `df -h / | tail -1`; `systemctl is-active openclaw-gateway fail2ban ssh`
- **Updates:** `apt list --upgradable 2>/dev/null | wc -l`
- **OAuth health:** `journalctl -u openclaw-gateway --since '2 hours ago' --no-pager 2>&1 | grep -iE 'oauth|refresh.*fail|token.*fail|auth.*error'` — if any matches → alert user: "⚠️ Garden: OAuth токен OpenAI Codex сбоит, нужна переавторизация: `openclaw configure --section model`"
- If SSH fails to connect → alert user immediately
- If unknown login IP → alert user
- If openclaw-gateway is down → alert user
- If OAuth errors detected → alert user immediately
- **Codex OAuth check (EVERY garden heartbeat):** `journalctl -u openclaw-gateway --since '2 hours ago' --no-pager 2>&1 | grep -iE 'codex.*refresh|codex.*token.*fail|codex.*oauth'` on MAIN server too — if refresh fails, alert user IMMEDIATELY with "⚠️ Codex OAuth refresh сломался, нужна переавторизация"
- Log results to `memory/heartbeat-state.json` under `garden`

### 4. Logging
- After each check, update `memory/heartbeat-state.json` with timestamps
- If something important found → write to `memory/YYYY-MM-DD.md` and alert user

### 5. Review cron results + auto-failover (every heartbeat)
- Check `cron list` for recent runs
- If any cron job returned a result since last heartbeat — read it
- Evaluate: is the result adequate? Missing something? Wrong?
- If cron result looks bad or incomplete → alert user with specifics
- If all cron results look fine → no need to mention

**Auto-failover rule:**
If a cron job has `lastRunStatus: "error"` and error contains "timed out":
1. Switch that job's model to `openai-codex/gpt-5.4` via `cron update` (patch payload.model)
2. Immediately re-run the job via `cron run`
3. Alert user: "Задача [name] зависла на Claude, переключил на Codex и перезапустил."
4. Do NOT switch back automatically — user decides when to try Claude again

**Optimal timeout guidance:**
- Simple checks (status, last, df): 3-5 min is enough
- Web research (BBQ digest): 5 min
- If a job consistently fails even on Codex → disable it and alert user

### 6. Cron resource tracking (every 3-4 heartbeats)
- Check `cron runs` for each job — look at `usage` (input_tokens, output_tokens, total_tokens) and `durationMs`
- Calculate totals per day/week
- Compare with previous check in `memory/heartbeat-state.json`
- Alert user if:
  - Single job used >50k tokens in one run
  - Total daily cron token usage >200k
  - Single job took >3 minutes for a simple check
  - Costs are growing without obvious reason
- Log token stats to `memory/heartbeat-state.json` under `cronUsage`
- Format alert: "Cron расход: [job] съел [N]k токенов за [duration]. Всего за день: [N]k."

### 7. Cross-session awareness (один раз в день, утренний heartbeat)
- Просканировать все активные сессии через `sessions_list` (activeMinutes=1440, messageLimit=1)
- Для каждой сессии с активностью за последние 24ч — прочитать последние сообщения через `sessions_history`
- Записать краткую сводку в `memory/YYYY-MM-DD.md` с тегом сессии:
  - `[телеграм:группа]` — что обсуждалось
  - `[discord:#канал]` — какие решения приняты
  - `[крон:имя]` — результаты задач
- Обновить `STATE.md` если в других сессиях произошли значимые изменения (деплои, решения, новые сервисы)
- Цель: main session всегда знает, что происходило в других контекстах

## Rules
- Late night (23:00-07:00 Moscow) → only alert if critical
- Don't spam user with "all ok" messages
- Aggregate findings into one message if multiple issues
- If nothing changed → HEARTBEAT_OK
