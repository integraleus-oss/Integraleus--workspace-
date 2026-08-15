Fix the existing narrow pack-slug path-boundary defect in the isolated
home-agent-factory worktree. Change only `src/cli/factory.js`,
`test/cli.test.js`, and—if required to prove the reviewed entry-point behavior—
`test/cli-entrypoint.test.js`. Reject empty, absolute, separator-containing,
traversal, and malformed pack slugs before lookup while preserving valid pack
list/show behavior and symlinked CLI invocation. Do not commit, install
dependencies, or modify any other file.
