# Orchestrator Auth Boundary

Gateway-owned, in-memory authorization boundary for one foreground orchestrator packet.

It captures trusted owner metadata before the model, mints a short-lived opaque
grant for an exact packet digest, and atomically consumes that grant through a
Gateway RPC. Grants never persist to the agent-writable task tree and disappear
on restart. This is not an unattended runner and provides no commit, transfer,
push, deploy, cron, or rollback capability.

## Build

```bash
npm install
npm run plugin:build
npm run plugin:validate
npm test
```
