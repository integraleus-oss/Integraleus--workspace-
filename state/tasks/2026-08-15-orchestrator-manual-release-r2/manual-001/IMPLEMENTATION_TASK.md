Harden Home Agent Factory external-read domain policy validation.

Edit only `src/core/policy.js` and `test/policy.test.js`. Validate
`pack.permissions.externalRead.domains` fail closed before building the grant:
it must be an array whose entries are non-empty safe domain names, not URLs,
paths, wildcards, credentials, ports, whitespace, or non-string values. Invalid
input must raise a controlled `PolicyError`; valid existing empty and ordinary
domain arrays must remain supported. Add deterministic built-in Node tests. Do
not access the network, add dependencies, commit, push, deploy, or change any
external/system state.
