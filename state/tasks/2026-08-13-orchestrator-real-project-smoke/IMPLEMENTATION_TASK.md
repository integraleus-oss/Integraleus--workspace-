Fix the pack-slug path-boundary defect in Home Agent Factory.

Only edit `src/cli/factory.js` and add `test/cli.test.js`. Pack lookup must
reject traversal, absolute paths, separators, and other invalid slug forms
before reading a file. Preserve valid `pack list` and `pack show
private-archive-rag`. Add deterministic Node tests that prove valid behavior
and fail-closed invalid slug behavior. Do not install dependencies, change
package metadata, touch run logs, commit, push, or deploy.
