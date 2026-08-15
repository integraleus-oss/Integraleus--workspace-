This is a single bounded transport retry. The previous fresh review verified
the actual synthetic HEAD and test, and produced the correct review contract,
but Markdown fences caused strict admission to reject it.

Re-check `calc.py`, `test_calc.py`, current HEAD, and `python3 -m unittest -v`.
Use the trusted bindings and contract shape in
`../live-provenance-trial/honest-closure/manifest.json` and
`../live-provenance-trial/honest-closure/expected-verdict.json`.

Return exactly one JSON object. The first output character must be `{` and the
last output character must be `}`. No ``` fences, no `json` label, no prose,
no headings. Do not add an acceptance decision; policy decides.
