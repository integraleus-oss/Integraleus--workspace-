Implement a fresh model-class runtime/schema contract from source commit
`6e56761`. Do not copy or apply the manual-005 worktree diff. Edit only
`src/core/policy.js`, `test/policy.test.js`, and
`schemas/agent-pack.schema.json`.

Export one deeply frozen grammar whose accepted classes are exactly `local`
and `cloud`, and use it in runtime selection. Preserve precedence:
`requestContext.modelClass`, then `pack.modelPolicy.default`, then `local`.
Treat undefined as an absent source and document that rule. Any consulted value
must be a primitive string exactly in the grammar; do not trim, lowercase, or
coerce. Reject invalid types, empty strings, unknown values, and case variants
with a stable controlled PolicyError before approval logic.

Pin `modelPolicy.default` in agent-pack JSON Schema to the same accepted class
list. Add an exact deep-equality test for the complete modelPolicy schema
subtree assembled from the exported runtime grammar. Use one shared invalid
value corpus for both runtime sources. Test accepted values, fallback,
precedence, explicit valid request class short-circuiting an invalid pack
default, undefined-as-absent behavior, both invalid sources, and existing
cloud/private-data approval behavior. Preserve all existing tests.

Use only Node built-ins and existing files. Do not add dependencies, access the
network, commit, transfer, push, deploy, or make external/system changes.
