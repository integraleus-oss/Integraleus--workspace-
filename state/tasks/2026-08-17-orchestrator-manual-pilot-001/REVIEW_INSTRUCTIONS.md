Review controlled manual pilot 001 against all sealed criteria and the actual
three-file diff. Separate Standards from Spec findings. Verify especially that
runtime can never emit a non-string output channel, the Schema covers every
emitted grant property, required/closed object semantics match runtime, shared
grammar is exact and deeply frozen, prior external-read/model-class contracts
remain intact, and the dependency-free validator is not a misleading partial
Schema emulator. Use read-only inspection only; do not rerun commands or write
files. Every `command_output` evidence item must contain the required structured
`command` block; otherwise use the correct evidence kind. Cover AC-1 through
AC-8 and return only the sealed review-verdict JSON contract.
