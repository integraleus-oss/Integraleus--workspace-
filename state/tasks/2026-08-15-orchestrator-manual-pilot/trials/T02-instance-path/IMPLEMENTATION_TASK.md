Harden Home Agent Factory's `--instance` file lookup.

Only edit `src/cli/factory.js` and add `test/cli-instance.test.js`. Resolve an
explicit or default instance path inside the project root and reject traversal,
absolute paths, malformed or missing option values, and symlink escapes before
reading JSON. Preserve a valid local run. Use only built-in Node facilities.
Do not install dependencies, touch generated run logs in the repository,
commit, push, deploy, or change external/system state.
