Harden the run-log writer from source commit `f25e001`. Edit only
`src/core/run-log.js`, `schemas/run-log.schema.json`, and a new
`test/run-log.test.js`.

Define and export one deeply frozen run-log grammar and use it in runtime and
the exact schema-subtree test. Keep generated IDs compatible with
`run-YYYYMMDDTHHMMSSZ-<six lowercase hex characters>`. Reject caller run IDs
that do not match exactly, including traversal, separators, dot segments,
control characters, whitespace, extensions, and case variants. Define event as
a bounded lowercase ASCII identifier suitable for current events (letters,
digits, underscore; must start with a letter). Require `now` to be a valid Date.

Require `data` to be a plain JSON object. Produce a detached serialized value;
reject arrays, null, non-plain objects, undefined, functions, symbols, bigint,
non-finite numbers, cycles, and other values that cannot be represented by the
schema. Complete validation and JSON serialization before any `mkdirSync` or
`appendFileSync` call. On rejection, no runs directory or file may be created
and no partial line may be appended.

Pin the complete run-log JSON Schema subtree exactly against the exported
grammar, including RFC3339 date-time format, runId/event patterns, required
data, closed top-level properties, and data object type. Test createRunId with a
fixed date, successful and repeated JSONL writes, exact path and newline, parsed
records, traversal/control/date/event/data rejects, and filesystem no-side-
effect behavior. Use temporary directories only and clean them in tests.

Use only Node built-ins and existing files. Do not add dependencies, access the
network, commit, transfer, push, deploy, or change external/system state.
