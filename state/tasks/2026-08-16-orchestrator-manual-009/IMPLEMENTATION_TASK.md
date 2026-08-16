Align the emitted capability-grant runtime contract with
`schemas/capability-grant.schema.json` from source commit `8985b8e`. Edit only
`src/core/policy.js`, `schemas/capability-grant.schema.json`, and
`test/policy.test.js`.

Export one deeply frozen capability-grant grammar/shape description from
policy code and use it to pin an exact complete Schema contract in tests. The
Schema must cover every property currently returned by
`compileCapabilityGrant`, including `requestedModelClass`, require every
always-emitted property, close the top-level and `allowedExternal` objects,
and accurately describe arrays, external-read domains/methods, model class,
booleans, approval identifiers, and modelPolicy as actually emitted. Do not
claim stricter validation than runtime enforces. Preserve the previously
accepted external-read and model-class contracts and deep immutability.

Add a small dependency-free test validator or equivalent deterministic
contract harness sufficient to prove that representative local, cloud,
approval-required, external-read, and empty/default runtime grants satisfy the
Schema-derived contract, while missing required fields, extra top-level or
allowedExternal fields, invalid methods/model classes, wrong primitive types,
and malformed arrays are rejected. Tests must also prove exact schema/grammar
equality and that the exported grammar and compiled grants are deeply frozen.

Use only Node built-ins and existing files. Do not add dependencies, access the
network, commit, transfer, push, deploy, or change external/system state.
