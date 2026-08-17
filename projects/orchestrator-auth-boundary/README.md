# Orchestrator Auth Boundary

Two-phase authorization boundary for one foreground orchestrator snapshot.

`PREPARE ORCHESTRATOR PILOT` creates a bounded root-owned snapshot through
descriptor-relative, no-follow reads and returns its digest. A later exact
`RUN ORCHESTRATOR PILOT <snapshot-digest>` message consumes that snapshot once.
Prepared state disappears on restart. This is not an unattended runner and
provides no commit, transfer, push, deploy, cron, or rollback capability.

## Build

```bash
npm install
npm run plugin:build
npm run plugin:validate
npm test
```
