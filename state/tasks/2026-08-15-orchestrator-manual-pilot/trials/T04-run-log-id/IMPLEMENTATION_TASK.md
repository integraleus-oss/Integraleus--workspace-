Harden Home Agent Factory run-log file naming.

Only edit `src/core/run-log.js` and add `test/run-log.test.js`. An externally
supplied run ID must not escape the dated `runs/<date>/` directory, introduce
path separators, special path components, or unsafe file names. Reject invalid
IDs before append and preserve valid append-first JSONL behavior. Use temporary
directories and built-in Node tests. No dependencies, commit, push, deploy, or
external/system changes.
