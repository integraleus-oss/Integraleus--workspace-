# TRIZ Zip Inspection Report

## Verdict

The attached package is useful and stronger than a plain prompt dump. It should not be installed into OpenClaw wholesale, but it is a good candidate for a curated OpenClaw skill proposal.

Best use: adapt it as a local `triz-problem-solving` or `triz-contradiction-solver` skill with stricter routing, OpenClaw privacy/approval gates, and a smaller main `SKILL.md` that lazy-loads references.

## Contents

- Outer zip: 5 files, 264 KB.
- `triz-gpt-instructions.md`: compact 72-line GPT instruction.
- `triz-standalone.md`: 2,801-line standalone version with matrix and references in one file.
- `triz.skill`: nested zip package with `triz/SKILL.md`, README, resources, examples, and `scripts/matrix_lookup.py`.
- `triz-rag.zip`: 57 RAG chunks plus manifest, 199,901 bytes uncompressed.
- `triz-evals.json`: 15-scenario regression set, 71 expectations.

## Strengths

- Clear "no compromise" discipline: the skill tries to resolve contradictions rather than split the difference.
- Good routing: engineering TRIZ, software/AI heuristic mode, business heuristic mode, AFD/subversion analysis, trimming, OTSM networks, ARIZ, and forecasting are separated.
- Strong honesty guardrails: matrix is explicitly not authoritative for software/business; no invented percentages or benchmarks.
- Russian support is intentional: Russian triggers, Petrov references, Russian terminology resource.
- `matrix_lookup.py` works and protects against matrix-axis transposition by showing the reverse pair.
- Evals are practical and include restraint tests where TRIZ must not trigger.

## Issues

- `triz/SKILL.md` has an internal contradiction: "When NOT to use" says business/organizational strategy, while "Special modes" adds business/innovation heuristic mode. This must be reconciled before adaptation.
- The main `SKILL.md` is too large and can dominate unrelated tasks if installed as-is. It needs OpenClaw-style progressive disclosure.
- The `.skill` archive references `evals/evals.json`, but the archive does not contain `evals/`; the eval file is only present in the outer zip as `triz-evals.json`.
- `triz-standalone.md` is useful for one-file GPTs but too heavy for our live skill style.
- It should not become a default problem-solving lens for UX, ordinary brainstorming, or simple engineering questions without a real contradiction.

## Checks

- `unzip -t` outer zip: OK.
- `unzip -t` nested `triz.skill`: OK.
- `unzip -t` `triz-rag.zip`: OK.
- JSON validation for `contradiction_matrix.json`: OK.
- JSON validation for `triz-evals.json`: OK.
- Smoke run: `python3 .../matrix_lookup.py 9 10` returns principles 13, 28, 15, 19 and reports reverse pair 13, 28, 15, 12.

## Recommendation

Create a Skill Workshop proposal, not a direct install.

Proposed adaptation:

1. Main skill: concise trigger/routing and output contract.
2. References: reuse the package resources under `references/` or `resources/` only if licensing attribution is preserved.
3. Fix routing: business/innovation is allowed only when the user explicitly asks for TRIZ/business contradiction analysis; generic business strategy should not trigger automatically.
4. Keep software/AI as heuristic mode only, with explicit source tags and domain-native alternatives.
5. Include `matrix_lookup.py` and evals as support files, with eval path fixed.

## Proposal Created

Skill Workshop proposal `triz-contradiction-solver-20260728-8603e44b92` was created after Stanislav explicitly requested the adaptation.

Final inspected state: `pending`, `create`, `v2`, `clean`.

Included fixes:

- Business routing conflict resolved: generic business strategy does not trigger automatically; business/innovation mode is allowed only for explicit TRIZ-style business contradiction analysis.
- Main skill is compact and uses progressive disclosure through references.
- MIT license and attribution are included in `references/LICENSE-MIT.txt` and `references/ATTRIBUTION.md`.
- `scripts/matrix_lookup.py` is included and patched to read from `references/`.
- Evals are packaged at `references/evals.json`.
- Patched `scripts/` + `references/` layout was smoke-tested in `candidate-test/`; `matrix_lookup.py 9 10` returned the expected principles and reverse-pair notice.

## Live Apply

Stanislav explicitly approved applying the proposal.

Applied proposal: `triz-contradiction-solver-20260728-8603e44b92`.

Final inspected state: `applied`, `create`, `v2`, `clean`.

Live skill files are now under `skills/triz-contradiction-solver/`, including compact `SKILL.md`, `references/`, and `scripts/matrix_lookup.py`.

Post-apply smoke check:

`python3 skills/triz-contradiction-solver/scripts/matrix_lookup.py 9 10`

Result: expected principles `13, 28, 15, 19` and reverse-pair notice `13, 28, 15, 12`.

## Memory Note

Existing long-term memory already had a TRIZ watchlist note for `NiiyazG/triz` from 2026-07-14. This attached package appears to be a richer TRIZ skill bundle and should supersede that watchlist only after Stanislav approves a memory update.
