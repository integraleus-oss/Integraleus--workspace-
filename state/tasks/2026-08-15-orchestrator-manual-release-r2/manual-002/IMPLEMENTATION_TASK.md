Implement one coherent Home Agent Factory externalRead contract.

Edit only `src/core/policy.js`, `test/policy.test.js`, and
`schemas/agent-pack.schema.json`. Preserve backward compatibility: absent
externalRead/domains/methods means empty arrays. Validate domains as explicit
ASCII DNS hostnames (including single-label LAN and multi-label names) or raw
IPv4/IPv6 literals. Reject URLs, path/query/fragment, wildcard, credentials,
ports, whitespace, malformed labels, empty strings, and non-string entries.
Canonicalize DNS names to lowercase. Validate methods as a string array and
permit GET only, producing controlled PolicyError for malformed or denied
values. Return defensive frozen array copies in the compiled grant. Align the
JSON Schema container shape with runtime behavior and add deterministic Node
tests for compatibility, valid LAN/DNS/IP cases, invalid inputs, controlled
errors, canonicalization, and post-compilation source-array mutation. Use only
Node built-ins; no network access, dependencies, commit, push, deploy, or
external/system changes.
