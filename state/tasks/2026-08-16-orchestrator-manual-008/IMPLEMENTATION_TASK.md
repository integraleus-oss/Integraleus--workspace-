Harden project-owned JSON loading from source commit `8985b8e`. Edit only
`src/cli/factory.js`, a new `src/core/json-file.js`, and a new
`test/json-file.test.js`.

Create and export a focused JSON-file error type and a synchronous loader used
by the CLI for both pack and instance JSON. The loader must require a valid
project root and a non-empty project-relative path; reject absolute paths,
lexical traversal, final or ancestor symlink escape, missing/non-regular files,
files larger than 1 MiB, invalid UTF-8 (use fatal decoding), invalid JSON, and
JSON roots that are not plain objects. Return controlled stable error codes
without leaking file contents.

Resolve the real project root and real target, verify the target remains
inside the real root, then open/read the verified regular file in a bounded
way. Minimize path-swap exposure using Node built-ins available on Node 22;
state and test the practical boundary rather than claiming impossible complete
filesystem race elimination. The CLI must render these loader failures as one
controlled line and exit code 2, without a stack trace. Do not weaken existing
PolicyError handling.

Add deterministic temporary-directory tests for valid object JSON, null-
prototype-neutral parsed output, traversal and absolute paths, final and
ancestor symlinks, missing/directory/oversized files, malformed UTF-8,
malformed JSON, scalar/array/null roots, stable error codes, and absence of
secret/file-content disclosure in error messages. Exercise the CLI-facing
formatting through an exported side-effect-free helper or equivalent narrow
test seam; importing the CLI module must not accidentally execute a run.

Use only Node built-ins and existing files. Do not add dependencies, access the
network, commit, transfer, push, deploy, or change external/system state.
