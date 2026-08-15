Close the externalRead runtime-versus-JSON-Schema divergence in one coherent
bounded change. Edit only `src/core/policy.js`, `test/policy.test.js`, and
`schemas/agent-pack.schema.json`.

Define one explicit grammar for ASCII DNS names, IPv4 literals, and supported
IPv6 literals. The same corpus must be evaluated against both runtime policy
compilation and the JSON Schema validator. Resolve IPv4-embedded/mapped IPv6
forms deliberately: either support them consistently in both layers with a
deterministic canonical representation, or reject them consistently in both
layers with tests. Do not leave acceptance dependent on `node:net.isIP` alone
when the schema grammar differs.

Preserve compatibility for missing externalRead/domains/methods as empty
allowlists. Keep methods GET-only and return controlled `PolicyError` for all
malformed containers, entries, and denied methods. Canonicalize accepted DNS
and IP values deterministically. Build defensive immutable copies: freeze the
arrays and the containing `allowedExternal` and grant objects so later pack
mutation cannot change compiled policy. Add deterministic positive, negative,
canonicalization, mutation, immutability, and runtime/schema agreement tests.

Use only existing dependencies and Node built-ins. No network access,
dependency changes, commit, transfer, push, deploy, or external/system change.
