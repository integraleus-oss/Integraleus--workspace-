# Alpha BPR R6 controlled continuation

Work only in the supplied isolated worktree. The worktree already contains the
partial R6 implementation copied byte-for-byte from the canonical Alpha BPR
worktree and recorded as isolated seed commit `f043b05` over base `7b38ff4`.
This seed exists only to satisfy the orchestrator's clean-baseline invariant.

Finish the narrow R6 vertical slice:

1. Persist immutable baseline-scoped ontology evidence with versioned canonical
   bytes and hash, and bind its identity/hash into the recipe provenance.
2. Evaluate compatibility and ontology exclusively from the exact pinned
   payload/evidence. Preserve existing c14n-v1/v2 frozen bytes.
3. Keep submit, approve, activate and make-effective fail-closed and
   transactional. Add durable audit evidence for rejected transitions without
   allowing audit failure to open the gate.
4. Add Draft-only re-pin preview plus exact baseline/ontology/formula/procedure
   impact. Applying a re-pin requires optimistic revision and an explicit,
   preview-bound request; never silently choose the active baseline.
5. Expose actionable compatibility/pin state through the existing recipe API
   and HMI surface. Remove only deprecated `POST /publish`; preserve governed
   `POST /make-effective`.
6. Add focused negative tests for unpinned, stale, revoked, malformed/hash
   mismatch, concurrent pointer/pin changes, audit and role boundaries.

Do not commit, push, deploy, access network services, alter external databases,
touch Synology, or edit outside the allowlist. If the safe design requires a new
business ontology rule, a second migration, or a file outside the allowlist,
stop and escalate instead of expanding scope.
