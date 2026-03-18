# OpenClaw Dashboard Skill

Real-time interactive dashboard for monitoring and controlling OpenClaw system.

## Features

- 📊 **Live monitoring**: Sessions, models, resources
- ⚡ **Interactive controls**: Switch models, spawn tasks  
- 📋 **Cron management**: View and control scheduled jobs
- 🔧 **System tools**: Diagnostics, restart, emergency controls
- 📱 **Multi-platform**: Telegram inline buttons, Discord embeds

## Quick Start

```
/dash          # Show dashboard
/status        # Quick system status
dashboard      # Alternative command
```

## Views

- **Summary** — Overview of all systems
- **Details** — Deep dive into metrics  
- **Extended** — Advanced analytics
- **Logs** — System activity and errors
- **Control** — Interactive management panel

## Installation

Copy the skill folder to your OpenClaw workspace skills directory:
```
skills/dashboard/
├── SKILL.md
├── dashboard.js  
└── README.md
```

## Telegram Commands

The skill automatically registers these commands:
- `/dash` — OpenClaw Dashboard
- `/status` — System Status  
- `/help` — Help & Commands

## Security

- Only responds to authorized users
- No sensitive data in public channels
- Safe system command execution