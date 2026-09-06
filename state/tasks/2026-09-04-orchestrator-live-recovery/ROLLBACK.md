# Rollback

1. R20 implementation is preserved in an isolated worktree before live restore.
2. Legacy state, evidence, and outbox files are copied into the incident backup directory before repair.
3. If stable restore fails, restore the exact pre-change live files from the incident backup and restart Gateway.
4. If legacy repair is inconsistent, restore the exact legacy backups and leave delivery disabled pending review.
