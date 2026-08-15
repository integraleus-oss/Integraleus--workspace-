# Separation Principles for Physical Contradictions

A **physical contradiction** arises when a single element must exhibit two opposite properties (e.g. *hot* and *cold*, *present* and *absent*, *rough* and *smooth*). Unlike technical contradictions — which the 39×39 matrix resolves via the 40 principles — physical contradictions are resolved by **separation**: forcing the opposing properties to coexist along an orthogonal axis.

Four canonical separation axes (Altshuller; extended by Mann and Souchkov):

| # | Axis | Mechanism | Sample sub-principles (linked to 40 IP) |
|---|------|-----------|------------------------------------------|
| 1 | **Space** | Property A in region X, property B in region Y of the same element | #1 Segmentation, #3 Local quality, #4 Asymmetry, #7 Nested doll, #17 Another dimension, #30 Flexible shells |
| 2 | **Time** | Property A during interval t₁, property B during interval t₂ | #9 Preliminary anti-action, #10 Preliminary action, #15 Dynamics, #18 Mechanical vibration, #19 Periodic action, #20 Continuity of useful action, #21 Skipping, #34 Discarding and recovering |
| 3 | **Condition (interface / scale)** | Property A on one interaction, property B on another (different load, observer, scale, energy level) | #28 Mechanics substitution, #31 Porous materials, #32 Color changes, #35 Parameter changes, #36 Phase transitions, #37 Thermal expansion, #38 Strong oxidants, #39 Inert atmosphere |
| 4 | **System level (parts ↔ whole)** | Property A at the component level, property B at the system or supersystem level | #1 Segmentation, #5 Merging, #6 Universality, #25 Self-service, #33 Homogeneity, #40 Composite materials |

## Decision procedure

For a physical contradiction `Element X must be P and ¬P`:

1. **Test separation in space first** — is there any region of X where only P matters and another where only ¬P matters? If yes, restructure geometry (often principles #1, #3, #17).
2. **Test separation in time** — does P need to hold only during phase t₁ and ¬P only during phase t₂? If yes, sequence actions (often #10, #15, #19, #34).
3. **Test separation by condition** — does P apply under one stimulus / scale / observer and ¬P under another? If yes, switch interaction modality (often #28, #35, #36).
4. **Test separation by system level** — can the component carry P while the whole carries ¬P (or vice versa)? If yes, redesign as a composite or hierarchical structure (often #1, #5, #40).

If **none** of the four axes admits separation, the contradiction is mis-framed: re-examine whether both P and ¬P are truly required, or whether the underlying need can be reformulated.

## Worked micro-example

**Contradiction**: an aircraft landing gear must be *long* (clearance for takeoff/landing) AND *short* (compact stowage in flight).

- Space — no, the same structural element carries the load in both states.
- **Time — yes**: long during takeoff/landing, short during flight. → retract mechanism (principles #15 Dynamics, #34 Discarding-and-recovering inverted, #10 Preliminary action).

## Full Russian-canon list: 11 способов разделения противоречивых свойств

The 4 axes above are the compact modern taxonomy. The original Altshuller list (as taught in the Russian tradition; cross-checked against Petrov, "Основы ТРИЗ", 2nd ed.) is finer-grained — use it when the 4-axis pass stalls, especially системные and фазовые переходы, which the 4-axis version compresses:

1. Разделение противоречивых свойств **в пространстве**
2. Разделение противоречивых свойств **во времени**
3. **Системный переход 1а**: объединение однородных или неоднородных систем в надсистему
4. **Системный переход 1б**: от системы к антисистеме или к сочетанию системы с антисистемой
5. **Системный переход 1в**: вся система наделяется свойством С, её части — свойством анти-С
6. **Системный переход 2**: переход к системе, работающей на микроуровне
7. **Фазовый переход 1**: замена фазового состояния части системы или внешней среды
8. **Фазовый переход 2**: «двойственное» фазовое состояние одной части системы (переход из состояния в состояние в зависимости от условий работы)
9. **Фазовый переход 3**: использование явлений, сопутствующих фазовому переходу
10. **Фазовый переход 4**: замена однофазового вещества двухфазовым
11. **Физико-химический переход**: возникновение—исчезновение вещества за счёт разложения—соединения, ионизации—рекомбинации

Mapping to the 4 axes: items 1–2 ↔ axes 1–2; items 3–6 ↔ axis 4 (system level); items 7–11 ↔ axis 3 (condition), with phase transitions as the dominant physical mechanism. Cite as `Source: separation-<n>`.

## Парные приёмы (приём — антиприём)

A second Russian-canon tool for physical contradictions: each pair holds two opposite actions, and the resolution applies BOTH — one to one part/phase/condition, the other to another. Strongest when the contradiction resists single-axis separation because both opposite actions are genuinely required (classic worked case: a file made of stacked blade-like plates — «дробление» to self-clean, «объединение» to cut; both applied, contradiction gone).

1. Объединение — разъединение
2. Симметрия — асимметрия
3. Однородность — неоднородность
4. Увеличение — уменьшение
5. Предварительное действие — предварительное антидействие
6. Динамика — статика (подвижность — неподвижность)
7. Прерывность — непрерывность
8. Частичное действие — избыточное действие
9. Непосредственное действие — косвенное действие
10. Массовость — уникальность
11. Отброс — регенерация частей
12. Прямое действие — обратное действие

Procedure: state the PC as `X must be P and ¬P` → find the pair whose poles correspond to P and ¬P → assign each pole its own space region, time interval, condition, or system level (i.e., pairs still resolve THROUGH a separation axis — they tell you *what* to separate, the axes tell you *where*). Cite as `Source: paired-principle-<n>`.

## How to use this file

In Step 2 of the main workflow, after classifying the contradiction as physical: pick the separation axis (4-axis table above); if stalled, escalate to the 11-item Russian-canon list; if both opposite ACTIONS are required rather than opposite static properties, use the paired principles. Then jump to the linked principles in `40_principles.md` rather than the Contradiction Matrix.
