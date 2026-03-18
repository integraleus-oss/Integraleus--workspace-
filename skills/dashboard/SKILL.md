# Dashboard Skill

Interactive OpenClaw system dashboard with real-time monitoring and control capabilities.

## Usage

### Commands
- `/dash` or `/dashboard` — Show main dashboard
- `/status` — Quick system status
- `dashboard` — Alternative trigger

### Features
- **Real-time monitoring**: Sessions, subagents, cron jobs, system resources
- **Interactive controls**: Model switching, subagent management, system actions
- **Multi-view**: Summary, Details, Extended analytics, Logs, Control panel
- **Platform support**: Telegram (inline buttons), Discord (rich embeds)

## Implementation

The dashboard provides:

1. **Main Dashboard** (`dash_refresh`)
   - Active sessions and models
   - Subagent status
   - Cron job overview  
   - System health
   - Token usage estimates

2. **Detailed View** (`dash_details`)
   - Full session statistics
   - Individual cron job status
   - System resources (CPU, memory, disk)
   - Network connectivity

3. **Extended Analytics** (`dash_extended`)
   - Process information
   - Token usage analysis
   - Performance metrics
   - Heartbeat status

4. **Log Viewer** (`dash_logs`)
   - Recent system activity
   - API call statistics
   - Error tracking
   - Health monitoring

5. **Control Panel** (`dash_control`)
   - Model switching
   - Subagent spawning
   - Cron management
   - System controls
   - Emergency actions

## Callback Handlers

- `dash_*` — Dashboard navigation
- `ctrl_*` — Control panel actions
- `logs_*` — Log viewer functions

## Technical Notes

- Uses `sessions_list`, `subagents`, `cron`, `session_status` tools
- Collects system metrics via shell commands
- Maintains state through callback data
- Supports both Telegram and Discord platforms
- Implements proper error handling and fallbacks

## Security

- Only responds to authorized users
- No sensitive information exposure in public channels
- Safe system command execution
- Controlled access to management functions