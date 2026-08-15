# Full System of Laws of System Evolution (Petrov's hierarchy)

Structured after Petrov, "Законы развития систем (ТРИЗ)", 2nd ed. — the most complete modern treatment of ЗРТС. This file EXTENDS `evolution_trends.md` (8-trend compact model): use the 8 trends for quick prognosis; come here when the question needs the full hierarchy, an operational development line, a maturity audit, or system-evolution work on software/AI (see EAK section). IDs of the 8 trends are cross-referenced as (→ trend N).

## The hierarchy

Development is driven top-down: needs evolve → functions serving them evolve → systems delivering the functions evolve. Diagnose at the highest level that has changed.

```
Всеобщие законы (universal): S-curve development (→ trend lifecycle), dialectics
└─ Законы развития потребностей (needs): идеализация, динамизация,
   согласование, объединение, специализация потребностей
   └─ Закономерности изменения функций (functions): идеализация, динамизация,
      согласование, переход к моно-/полифункциональности
      └─ Законы развития технических систем:
         ├─ ЗАКОНЫ ОРГАНИЗАЦИИ (viability of a NEW system):
         │    полнота и избыточность частей · проводимость потоков ·
         │    минимальное согласование частей и параметров
         └─ ЗАКОНЫ ЭВОЛЮЦИИ (development of an EXISTING system):
              идеальность (→1) · неравномерность частей (→2) ·
              управляемость и динамичность (→5,8) · надсистема/подсистема (→3) ·
              микро-/макроуровень (→4) · согласование—рассогласование (→7) ·
              свертывание—развертывание (→6)
```

Practical split: building a system from scratch → check the three organization laws first (does energy/information flow reach every part? is every needed part present, with deliberate redundancy where reliability demands it?). Improving an existing system → evolution laws.

**Тренд—анти-тренд**: every evolution law has a legitimate counter-trend (идеальность↔анти-идеальность, динамизация↔стабилизация, свертывание↔развертывание, переход в надсистему↔в подсистему, микро↔макро). A system may deliberately run the anti-trend for a phase (e.g., развертывание: hybridize, absorb functions, THEN свертывание: collapse the hybrid into fewer parts). If a recommendation from a trend looks wrong for the system's stage, test the anti-trend before discarding the law.

## Operational development lines

These ladders answer "what is the next step for THIS system?" — locate the system's current rung; the next rung is the forecast. Cite as `Source: zrts-line-<name>`.

### Controllability ladder (управляемость)
неуправляемая → управление по разомкнутому контуру → обратная связь
(отрицательная = стабилизация, положительная = усиление) → самонастраивающаяся →
самообучающаяся → самоорганизующаяся → саморазвивающаяся → самовоспроизводящаяся

### Dynamization ladder (динамизация) — WHAT becomes changeable
изменяемые параметры → изменяемая структура → изменяемый алгоритм →
изменяемый принцип действия → изменяемая функция → изменяемые потребности → изменяемые цели

### Substance-fragmentation line (дробление вещества)
монолит → монолит из соединённых частей → части через посредника → гибкое состояние →
порошок → гель → паста/суспензия → аэрозоль → газ → поле (плюс ветка: пена,
капиллярно-пористые материалы, рост «пустотности»)

### Field/energy-information line
переход к более управляемым полям (гравитационное → механическое → тепловое →
электромагнитное → химическое/оптическое) · моно-поле → би- → поли- · динамизация полей ·
рост концентрации энергии и информации (с легитимным анти-трендом уменьшения)

### Свертывание mechanisms (convolution, →6)
удалить элемент, передав его функцию другому элементу системы · вытеснить часть в надсистему ·
миниатюризация · переход в подсистему. Развертывание: гибридизация → later свертывание
«лишних» частей гибрида → максимальное использование ресурсов.

### Согласование axes (→7)
согласуй (или намеренно РАСсогласуй — обе операции законны) элементы, связи,
параметры, ритмику (частоты, такты, периодичность действий).

## EAK: Su-Field for information systems (Petrov's extension)

For information systems Petrov replaces вещество/поле: **Element (E)** — what is acted on, **Action (A)** — the operation (replaces field), **Knowledge (K)** — the third component governing the action. Model: K controls A, A transforms E. This is a PRIMARY-SOURCE extension of TRIZ to information systems — cite as `Source: zrts-eak` (still distinct from the contradiction matrix, which remains physical-domain statistics).

**Knowledge-integration ladder** (the EAK development law; canonical worked example — drilling: manual worker → jig → CNC machine → self-programming machine):
1. K outside the system (human operator holds all knowledge)
2. Partial K built in at design time (fixtures, defaults, hard-coded rules)
3. All process K inside; knowledge MANAGEMENT outside (programmable system, human writes the program)
4. Knowledge management inside the system (K₂ governs K₁ — the system reprograms itself)

AI-agent reading: rule-based tool → configured pipeline → learned policy with human retraining → self-improving agent. Combined with the controllability ladder, this gives a two-axis maturity grid for agentic systems (see `software_ai_systems.md`).

## Прогноз (forecasting procedure)

**Экспресс-прогноз** = three parallel passes, then merge into one roadmap:
1. **S-curve pass**: locate the stage (зарождение/рост/зрелость/спад) → strategy (invest in growth / seek transition to the next-principle system at maturity).
2. **Standards pass**: classify the system as изменение (transformation; standards classes 1→2→3, then always 5) or измерение (measurement/detection; class 4, then 5); the forecast = continue along the class sequence from the system's current standard (see `76_standard_solutions.md`).
3. **Laws pass**: for each evolution law, locate the system on its line (ladders above) → next rung = direction; check the anti-trend as an alternative branch.

**Углубленный прогноз** adds: needs/functions levels of the hierarchy, тренд—анти-тренд branching for every law, and resource analysis. Offer it when the user asks for a roadmap, not just a next step.

## Audit: степень использования законов

Petrov's maturity audit, simplified for agent use: for each evolution law, list its mechanisms (the rungs/axes above); score each mechanism's degree of use in the system from 0 to 1; a law's score = mean of its mechanisms; the system profile = the vector of law scores. Low-scoring laws with high relevance to the user's goal = the development reserves — name them explicitly in prognostic output as `развитие по закону <name>: текущая ступень → следующая`.
