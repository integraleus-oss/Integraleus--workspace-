# Deep Su-Field Analysis (harmful links, effect finding, ЭлДЗ/ДаФЗ)

Structured after Petrov, "Структурный анализ систем. Вепольный анализ. ТРИЗ". This file DEEPENS the Su-Field layer: `76_standard_solutions.md` gives the class taxonomy; come here for the systematic harmful-link elimination tree, the effect-finding rule, and the full Element–Action–Knowledge apparatus for information systems. Notation: В = substance, П = field, В' = modified form of a substance, wavy arrow = harmful action.

## Harmful-link elimination tree

Identify WHICH pair carries the harmful link, then walk that branch's transformations in order — earlier entries are cheaper (closer to the ИКР), later ones add more control at more cost. Cite as `Source: vepol-harmful-<branch>.<step>`.

**Branch 1 — вещество ↔ вещество** (В1 harms В2 or vice versa):
1. Introduce a third substance В3 between them (macro- or micro-level: a coating, a layer, an additive).
2. В3 = modification of the substances already present (В3 = В'1 or В'2) or the substances themselves (В3 = В1, В2) — the strongest form: the barrier is made of what's already in the system (foam of the same liquid, ice of the same water, the product's own crust).
3. В3 = В'1/В'2 plus a field П2 that produces or maintains the modification (freeze the layer, magnetize the powder).

**Branch 2 — поле ↔ вещество** (П1 harms В1):
1. «Оттягивание» — draw the harmful action off onto a sacrificial element (lightning rod pattern).
2. Introduce a counteracting field П2.
3. Introduce В3 that generates П2 itself (self-protection from an internal source).
4. Introduce В3 that generates П2 under an external field П3 (controllable protection).

**Branch 3 — вещество ↔ поле** (the system's OUTPUT field П2 is wrong/insufficient — a control problem):
1. Add В2 + П2 to shape the output.
2. Replace В1 with В2 and add a control field П3 governing the output П2.

Agent/software reading of the branches: В3-barrier = sandbox/adapter/rate-limiter between two components; В3 = В'1 = the barrier built from the system's own artifacts (validating input with the schema the system already emits); оттягивание = honeypot / dead-letter queue; П2 counter-field = compensating policy; В3 generating П2 under П3 = a guard activated by an external signal (feature flag, kill-switch).

## Effect-finding rule (Глава 5)

When the solution's vepol requires a substance to convert field П1 into field П2 (or change a field's parameter), the NAME of the needed technological effect is the concatenation of the two fields: акустическое → электрическое = acoustoelectric (→ piezoelectric effect); тепловое → электрическое = thermoelectric, etc. Then look the concrete effect up in an effects index. This turns "what physics do we need?" from an open question into a lookup key. For measurement/detection problems the same rule applies with the measured parameter as the input field (see class 4 of the standards).

## ЭлДЗ / EAK — parametric analysis (Глава 8)

The Element–Action–Knowledge model (`zrts_full.md` has the knowledge-integration ladder). The parametric pass — before transforming an ЭлДЗ, tabulate:
- **Элемент (E)**: what it is, its state, changeable parameters, what it can be replaced with;
- **Действие (A)**: what it changes in the element, sufficiency (insufficient / normal / excessive / harmful), controllability;
- **Знание (K)**: where it lives (outside / built-in / self-managed), what it governs, how it updates.

Knowledge-development regularities (закономерности развития знаний) — the four moves available on the K component: расширение ↔ сжатие (свертывание) of the knowledge base; дифференциация — специализация; комбинация — интеграция of known knowledge; интеллектуализация (knowledge starts producing knowledge). These mirror the substance-fragmentation and convolution lines from `zrts_full.md`, applied to knowledge.

## ДаФЗ / DFK analysis — information-processing systems

For systems whose main process is data processing, the model specializes: **Данные (Data, D)** — incoming information; **Функция (Function, F)** — the processing action; **Знание (Knowledge, K)** — structured, active information set at design/update time, available independently of the incoming data.

Diagnostic ladder (cite as `Source: dfk-<level>`):
1. **Неполный ДаФЗ** — the function is constant and ignores the data → uncontrolled system (hardcoded pipeline).
2. **Полный (простой) ДаФЗ** — pre-set knowledge adjusts the function per class of incoming data (config/rules-driven).
3. Higher rungs — knowledge updates from data, then knowledge manages knowledge (learned policies; self-improving systems) — merge with the controllability ladder in `zrts_full.md`.

Agent reading: an LLM agent in one frame — D = user input + tool results, F = generation/tool calls, K = weights + system prompt + skills + memory. A skill file is literally externalized K (level 2); memory-from-history is K updating from D (level 3); an agent editing its own skills is K managing K (level 4). Use ДаФЗ to name which component a proposed improvement actually changes — many "agent improvements" are K-level changes disguised as F-level ones.
