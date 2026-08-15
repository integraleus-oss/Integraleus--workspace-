# TRIZ for Business & Innovation (heuristic mode, primary-source backed)

Structured after Petrov & Petrov, "Инновации. Бизнес. ТРИЗ" — 65 worked business cases (banking, taxi, SaaS, retail, education, IT security, software business models). This upgrades business problems from "do not trigger" to an explicit heuristic mode, analogous to `software_ai_systems.md`: the contradiction DISCIPLINE transfers with primary-source support; the contradiction MATRIX does not (its statistics are physical-domain). Mark all output `Source: business-heuristic` (or a more specific tag below); name validated business-native alternatives (unit economics, JTBD, competitive analysis) alongside the TRIZ pass when the user is making a real decision.

## Terminology — the business contradiction chain

Business TRIZ renames the chain (English resources' IDs unchanged; see also `ru_reference.md`):

- **ПП — поверхностное противоречие** (surface contradiction; ≈ administrative): a single requirement — a desired effect «А» or an undесirable effect «анти-Б». Notation: ПП(ПЭ): А or ПП(НЭ): анти-Б.
- **ПТ — противоречие требований** (requirements contradiction; ≈ technical): two conflicting requirements. ПТ: А — анти-Б (improving А unacceptably worsens Б), or анти-А — Б.
- **ИКР**: both satisfied. ИКР: А, Б.
- **ПС — противоречие свойств** (properties contradiction; ≈ physical): the element that fails the ИКР must hold С to deliver Б and анти-С to keep А. Notation: ПС: С → Б, анти-С → А.
- *(Same chain as АРИЗ-2010's ПП→УП→ОП — see `ariz_2010.md`; mapping table in `ru_reference.md`.)*
- **Deepening**: if ПС resists separation, find the deeper property behind С: С1 → С, then С2 → С1, … — walk the causal chain down until a separable level appears.

## Анализ ПТ и ПС — pre-separation analysis

Before separating properties, interrogate the requirements themselves (this step is business TRIZ's main addition to the standard workflow; cite as `Source: pt-ps-analysis.<n>`):

1. **Rank the requirements.** Which of А/Б is immutable? Keep the property serving it fixed; separate the other. Corollaries: if both must hold at the same TIME → separate in space or structure; if in the same SPACE → separate in time; or engineer conditions under which the key requirement is guaranteed regardless.
2. **Decompose a requirement.** If both are equally important, split each into constituent features and test the necessity of each part; features tied to the improvement stay, the rest are free to change — the contradiction often lives in a dispensable part.
3. **Reformulate via function.** Name the system's function and ask for the simplest different principle of action delivering it.
4. **Go up.** Name the надсистема's function and look for a way to achieve IT without the system's function at all (the ultimate свертывание — the business analogue of "the best subsystem is no subsystem").

## What transfers well (with case-pattern tags)

- **ИКР discipline** — "the client is served, the cost/asset does not exist": the strongest single transfer. Asset-light patterns (marketplace owns no cars/rooms) are ИКР solutions. `Source: business-ikr`
- **Ресурсы** — idle capacity, waste streams, customer actions, data exhaust, partners' assets as ВПР. Self-service = the client's own labor as a resource; crowdsourcing / открытая бизнес-модель / «армия разработчиков» = надсистема labor as a resource. `Source: business-resources`
- **Разделение ПС** — in space (segmented offerings), time (peak pricing, freemium periods), structure (holding vs. brand separation), condition (personalization tiers). `Source: separation-<axis>`
- **Приёмы as reframing prompts** — the 40 principles read naturally in business (посредник = intermediary/platform; предварительное действие = pre-commitment, subscriptions; обратить вред в пользу = monetize the complaint stream; дешёвая недолговечность = disposable/entry tier). Use the principle translations pattern from `software_ai_systems.md`; drop any forced reading.
- **Законы эволюции** — идеальность (asset-light, disintermediation), свертывание (bundling then collapsing the bundle), переход в надсистему (platformization, ecosystems), моно→би→поли (product line evolution), применение по новому назначению (pivot patterns). Use the ladders in `zrts_full.md` for roadmap questions. `Source: zrts-<law>`

## MPV — Main Parameters of Value (choose the RIGHT parameter first)

Before resolving anything, separate the parameters the customer actually pays for (MPVs) from the ones engineers improve because they can. Procedure: list the parameters currently being optimised → for each, ask what the end customer's outcome depends on and what they would notice if it changed → rank by willingness to pay / switching influence → run the TRIZ pass ONLY on contradictions involving top MPVs. A brilliantly resolved contradiction in a non-MPV parameter is wasted work; a modest gain in an MPV moves the market. Pairs with the false-problem check (`ariz_2010.md`) and the Выбор задачи module — same discipline, applied to value rather than causality. Cite as `Source: mpv`.

## What does NOT transfer

- The 39×39 matrix (physical parameters); do not map "brand strength" onto "прочность" to force a lookup.
- Substance-field mechanics in the physical sense; use the ЭлДЗ/ДаФЗ reading (`vepol_deep.md`) if a structural model is needed — business processes are information processes.
- Guaranteed-solution framing: business systems include adversarial actors (competitors respond, regulators react); every TRIZ-derived move needs a second-order pass — "who counter-moves, and does the resolution survive it?" — which classic TRIZ does not model.

## Workflow adaptation

Run the standard workflow with these substitutions: intake in business terms (main function = the client outcome, not the org chart) → ПП → ПТ (both directions) → ИКР: А, Б → Анализ ПТ и ПС (above) → ПС with С/анти-С notation → separation + resource pass → concepts with second-order (competitor/regulator) check → evaluation against ИКР. Skip the matrix entirely.
