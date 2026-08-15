# РТВ — Creative Imagination Development (divergence operators)

Structured after Petrov, "Развитие творческого воображения. ТРИЗ". This file completes the pre-analysis layer of `thinking_toolkit.md`: it holds the DIVERGENCE instruments — deliberate imagination operators that widen the search space before the convergent tools (matrix, standards, АРИЗ) narrow it. Load when: solutions keep gravitating to the existing design, the user asks to "think wilder / outside the box", concept generation feels samey, or a psychological-inertia cause below is visibly active.

## Psychological inertia — the six causes

Inertia = involuntarily reusing known solutions and framings. Useful in routine tasks, harmful in inventive ones. The six causes (each with its counter-move):

| # | Cause | Counter-move |
|---|---|---|
| 1 | Специальные термины ("ледокол" presumes ice must be BROKEN) | Replace with generic function words (intake rule of the main workflow) |
| 2 | Параметрические представления (habitual size/time/cost ranges) | Оператор РВС below |
| 3 | Система ценностей (what "counts" as a serious solution) | State the ИКР first; evaluate against it, not against convention |
| 4 | Привычный принцип действия | Функциональная формулировка + перебор альтернативных принципов (дерево принципов действия) |
| 5 | Привычная форма | ММЧ, fantasy operators УВЕЛИЧЕНИЕ–УМЕНЬШЕНИЕ / НАОБОРОТ |
| 6 | Традиции (professional, corporate, national…) | System Operator: надсистема and antisystem screens |

Diagnostic use: when a solution search stalls, name WHICH cause is active — the table then gives the targeted counter-move instead of generic "brainstorm harder".

## Оператор РВС (Размер — Время — Стоимость)

Altshuller's operator against parametric inertia (cause 2). For the object of the task, mentally drive three parameters to both limits and observe where the problem QUALITATIVELY changes:

- **Размер** → 0 (grain-sized iron: single instrument can't be held → a field or a swarm must do the work) and → ∞ (wardrobe-sized iron: the container itself becomes the worker).
- **Время** → 0 (whole surface processed at once → different physical principle) and → ∞ (processing happens continuously in idle time — while the object hangs unused).
- **Стоимость** → 0 (free iron: what if the function came with something already owned?) and → ∞ (unlimited budget: which principle would we choose then, and what cheap shadow of it exists?).

At each limit ask: what breaks, what becomes free, which new principle is forced. The value is not the fantastic object but the PRINCIPLES the limits force into view — carry them back to real scale. Software/agent reading: РВС is requirements stress-testing — context window → 0/∞, latency budget → 0/∞, token cost → 0/∞; each limit exposes an architecture that the habitual mid-range hides. Cite as `Source: rvs-<parameter>-<limit>`.

## 12 приёмов фантазирования (Amnuel's set)

Fantasy operators — apply to the object, its property, or its action; then translate the interesting fantasy back into a feasible mechanism. Most map onto inventive principles (noted), so a fantasy hit converts directly into a solution direction.

1. **НАОБОРОТ** — свойства → противоположные, действия → антидействия (↔ IP-13; antisystem axis)
2. **УВЕЛИЧЕНИЕ – УМЕНЬШЕНИЕ** — до качественного скачка (↔ РВС-размер)
3. **УСКОРЕНИЕ – ЗАМЕДЛЕНИЕ** — до качественного скачка (↔ РВС-время, IP-21)
4. **ДИНАМИЗАЦИЯ – СТАТИКА** — неизменное сделать меняющимся и наоборот (↔ IP-15; dynamization ladder)
5. **УНИВЕРСАЛИЗАЦИЯ – ОГРАНИЧЕНИЕ** — расширить/сузить класс действия (↔ IP-6)
6. **ДРОБЛЕНИЕ – ОБЪЕДИНЕНИЕ** (↔ IP-1/IP-5; paired principle 1)
7. **КВАНТОВАНИЕ – НЕПРЕРЫВНОСТЬ** — прерывистое ↔ непрерывное во времени/пространстве (↔ IP-19/IP-20)
8. **ВЫНЕСЕНИЕ – ВНЕСЕНИЕ** — отделить присущее свойство / приписать чужое (↔ IP-2)
9. **СМЕЩЕНИЕ** — действие сместить во времени вперёд или назад (↔ IP-10/IP-9)
10. **ОЖИВЛЕНИЕ** — неживому свойства живого и наоборот (agent reading: give a passive artifact agency — a config that renegotiates itself; or strip agency — freeze an agent into a deterministic pipeline)
11. **ИЗМЕНЕНИЕ СВЯЗЕЙ** — изменить связи объект↔среда вплоть до смены среды (↔ System Operator среда screen)
12. **ВОЛШЕБСТВО** — отменить закон природы/мировую константу; then ask which real mechanism gives 10% of the magic (the strongest inertia-breaker; pairs with ИКР: magic IS the ideal, engineering is its approximation)

Usage pattern in the workflow: at Step 4/5, if candidate concepts are homogeneous, run 3–4 operators over the conflict object, harvest the qualitative shifts, convert each into a principle-level direction, then return to the convergent track. Fantasy output itself is never the final answer — the translated principle is.

## Idea-processing methods

- **Фантограмма** — a morphological table for systematic sweeps when single operators run dry: rows = characteristics of the system (вещество, подсистемы, объект в целом, надсистема, энергопитание, способ передвижения, сфера обитания, воспроизведение, направление развития, уровень организации и управления), columns = the fantasy operators above; each cell forces one transformation. Fill selectively — the rows most coupled to the conflict, not all 10×12. Cite as `Source: fantogramma`.
- **Метод золотой рыбки** (разложение фантастических идей) — the bridge from an aggressive ИКР to a roadmap: split an "impossible" idea into its реальная часть (implement now) and фантастическая часть; recursively split the fantastic remainder until every fragment is either implementable or a named research gap. Use whenever a strong concept gets rejected as "unrealistic" — decompose instead of discarding. Cite as `Source: zolotaya-rybka`.
- **Метод снежного кома** (синтез фантастических ситуаций) — the inverse move: adopt one fantastic assumption and roll out its consequences level by level (system → надсистема → environment). Consequence-analysis for radical concepts before investing in them; for agents — the standard shape of a "what if we fully automate X" impact pass. Cite as `Source: snezhny-kom`.
- **Ступенчатое конструирование, метод ассоциаций, метод тенденций, взгляд со стороны, изменение системы ценностей, выявление скрытых свойств** — auxiliary divergence moves; apply freely, no fixed procedure required.
- **Шкала «Фантазия»** — triage generated ideas on novelty, convincingness, and human value before they enter Step 6 evaluation (the original scale also scores artistic worth — relevant only for fiction work).
