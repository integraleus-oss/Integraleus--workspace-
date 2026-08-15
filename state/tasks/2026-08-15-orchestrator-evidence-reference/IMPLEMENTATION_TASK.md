Fix the existing narrow pack-slug path-boundary defect in the isolated
home-agent-factory worktree. Change only `src/cli/factory.js` and
`test/cli.test.js`. Reject empty, absolute, separator-containing, traversal,
and malformed pack slugs before lookup while preserving valid pack list/show
behavior. Do not commit, install dependencies, or modify any other file.
