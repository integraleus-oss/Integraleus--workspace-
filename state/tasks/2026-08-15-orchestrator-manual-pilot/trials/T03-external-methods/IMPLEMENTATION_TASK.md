Harden external-read method validation in Home Agent Factory policy.

Only edit `src/core/policy.js` and `test/policy.test.js`. Malformed method
values, including non-strings, must be rejected fail-closed using a stable
`PolicyError` code instead of leaking an uncontrolled TypeError. Preserve the
GET-only rule and valid grants. Add deterministic tests. No dependencies,
commit, push, deploy, generated logs, or external/system changes.
