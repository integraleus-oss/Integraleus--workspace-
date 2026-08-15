Close the externalRead contract in one bounded change. Edit only
`src/core/policy.js`, `test/policy.test.js`, and
`schemas/agent-pack.schema.json`.

Implement one explicit grammar for accepted ASCII DNS names, IPv4, and
colon/hextet IPv6. Reject IPv4-embedded/mapped dotted-tail IPv6 consistently in
runtime and schema. Preserve missing externalRead/domains/methods as empty
allowlists; reject malformed values with controlled PolicyError; keep methods
GET-only; canonicalize accepted values deterministically.

Replace the manual-003 partial-schema-interpreter approach. Pin the complete
externalRead JSON Schema subtree by exact deep equality against an expected
contract assembled from the exported runtime grammar, so any added, removed,
or changed keyword fails loudly. Exercise one shared domain corpus directly
against the exact schema patterns and runtime. Include explicit rejects for
scheme URLs, paths, ports, credentials, wildcards, leading/trailing/internal
whitespace, trailing newline, IPv6 zone IDs, brackets, and dotted-tail IPv6.

Make every compiled grant field a detached immutable value. Deep-clone and
deep-freeze nested plain objects and arrays in `modelPolicy`; reject unsupported
non-JSON-like mutable values if necessary with controlled PolicyError. Add a
nested source-mutation test and frozen-nested-container assertions.

Use only Node built-ins and existing files. Do not add dependencies, access the
network, commit, transfer, push, deploy, or make external/system changes.
