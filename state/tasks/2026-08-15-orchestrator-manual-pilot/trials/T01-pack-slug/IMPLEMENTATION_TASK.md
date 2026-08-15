Fix the pack-slug path-boundary defect in Home Agent Factory.

Only edit `src/cli/factory.js` and add `test/cli.test.js`. Pack lookup must
reject traversal, absolute paths, separators, empty values, and malformed slug
forms before reading a file. Preserve valid `pack list` and `pack show
private-archive-rag`. Add deterministic Node tests. Do not install dependencies,
touch run logs, commit, push, deploy, or change external/system state.
