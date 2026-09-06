Review only these files in the supplied worktree diff:

- src/agents/auth-profiles/session-override.ts
- src/agents/auth-profiles/session-override.test.ts
- src/agents/auth-profiles/session-override.selection.test.ts
- src/agents/auth-profiles/session-override.rotation.test.ts
- src/agents/auth-profiles/session-override.user-pin.test.ts
- src/cron/isolated-agent/run-session-state.ts
- src/cron/isolated-agent/run-session-state.test.ts

Ignore unrelated delivery-queue changes already present in the dirty worktree.

Objective: automatic auth-profile selection must be attempt-scoped, legacy persisted auto pins must be safely cleared, blocked/cooldown state must be re-evaluated before every turn, explicit user pins must remain session-scoped, and concurrent session updates must not be overwritten.

Report correctness bugs, concurrency hazards, regressions, and missing tests. End with APPROVE or REQUEST_CHANGES.

The implementation deliberately does not persist automatic selections. A legacy
`source: auto` pin is cleared with compare-and-swap; explicit user pins remain
stable. Cron synchronization must likewise discard live automatic selections.
Please verify the final implementation after the first review's requested
changes, including the steady-state no-write and blocked-profile re-evaluation
tests.

After the second review, the missing-profile branch again clears its local
selection, the private dead `isNewSession` parameter was removed, cooldown is
checked against the current attempt model id, and the misleading test name was
fixed. The existing parameterized concurrency test in
`session-override.test.ts` covers persisted and in-memory user-pin races on the
healthy-profile path. Cross-route selection follows configured auth order by
design; the runtime auth fingerprint invalidates an incompatible native resume
binding and forces a compatible reseed.
