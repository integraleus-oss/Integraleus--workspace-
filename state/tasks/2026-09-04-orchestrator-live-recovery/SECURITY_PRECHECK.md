# Security Precheck

- Risk: HIGH — live Gateway and durable execution state.
- Approval: Telegram message 5101 explicitly approves restore, restart, and two legacy repairs.
- External send: none.
- Secrets: no secret files are in scope.
- Destructive boundary: exact-file backups are required before restore or state repair.
- Stop condition: inability to reconstruct the original legacy outcome from repository evidence.
