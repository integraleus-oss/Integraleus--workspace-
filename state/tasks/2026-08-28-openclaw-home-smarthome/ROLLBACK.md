# ROLLBACK

If deployment verification fails:

1. Run `docker compose down` only in `/opt/smarthome`.
2. Disable/remove only `smarthome-backup.timer` and its paired service if created.
3. Preserve `/opt/smarthome` for diagnosis unless Stanislav asks to remove it.
4. Confirm all pre-existing container IDs, names, and running states match the before snapshot.

Never restart Docker globally and never modify existing containers to resolve a conflict.
