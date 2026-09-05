# Rollback

1. Stop activation work and preserve evidence.
2. Restore the scoped live orchestrator files to commit `92ee5436` without touching unrelated files.
3. Restore the previous managed-worker configuration and protected runtime paths from the activation backup.
4. Recreate the sandbox if its mount/config changed.
5. Restart with `openclaw gateway restart`.
6. Verify `openclaw status --deep`, Telegram, logs, and absence of recovery loops.
7. Mark the managed job `FAILED` or `CRASHED`; emit one notification to Telegram topic 2922.

Rollback trigger: any failed mandatory check or unverified terminal/delivery behavior.

