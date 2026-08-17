Freshly fix the capability-grant runtime/schema mismatch from source commit
`8985b8e`. Do not inspect, copy, or reuse the rejected manual-009 worktree diff.
Edit only `src/core/policy.js`, `schemas/capability-grant.schema.json`, and
`test/policy.test.js`.

Export one deeply frozen capability-grant grammar/shape description from policy
code and use tests to pin the exact complete JSON Schema contract. The Schema
must cover and require every property always returned by
`compileCapabilityGrant`, including `requestedModelClass`, and close the
top-level and `allowedExternal` objects.

Resolve the known major explicitly: neither `requestContext.channel.type` nor
`instance.channel.type` may let runtime emit a non-string
`allowedOutputChannels` entry while the Schema requires strings. Validate the
selected channel type as a non-empty primitive string before compiling the
grant, return a controlled `PolicyError` for invalid values, and test precedence
and invalid request/instance channel inputs. Do not weaken the Schema to accept
arbitrary JSON values.

Accurately describe arrays, external-read domains/methods, model class,
booleans, approval identifiers, and modelPolicy as emitted. Preserve the
accepted external-read and model-class contracts and deep immutability.

Add a dependency-free deterministic contract harness sufficient to prove that
representative local, cloud, approval-required, external-read, and default
runtime grants satisfy the Schema-derived contract. Required negative coverage:
missing required fields, extra top-level/allowedExternal fields, invalid
methods/model classes, wrong primitives, malformed arrays, and invalid channel
types. Tests must prove exact schema/grammar equality and deep freezing of the
exported grammar and compiled grants.

Use only Node built-ins and existing files. Do not add dependencies, access the
network, commit, transfer, push, deploy, or change system/external state.
