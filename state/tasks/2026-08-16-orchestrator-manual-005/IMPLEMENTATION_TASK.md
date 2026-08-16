Harden requestedModelClass in one bounded change. Edit only
`src/core/policy.js` and `test/policy.test.js`.

Normalize the selected model class before any approval decision or grant
construction. Preserve precedence: `requestContext.modelClass`, then
`pack.modelPolicy.default`, then `local`. Accept only primitive strings exactly
equal to `local` or `cloud`. Reject invalid types, empty strings, unknown
values, and case variants with a stable controlled `PolicyError` code and clear
message. Do not silently coerce, trim, or lowercase values.

Test request-context and pack-default sources, fallback, precedence, both
accepted classes, invalid types and values, and the existing private-data cloud
approval behavior. Preserve all existing externalRead and immutability tests.
Use only existing Node facilities. Do not edit schemas or other files, add
dependencies, access the network, commit, transfer, push, deploy, or change
external/system state.
