# Карта процесса разработки Alpha BPR

Статус: черновик рабочей инструкции v0.1
Дата: 2026-08-07
Область: разработка, демо-контур, HMI/BFF, evidence и упаковка Alpha BPR

Эта карта описывает практический процесс разработки Alpha BPR: от выбора
следующего среза до коммита, проверки публичного демо и передачи результата.
Документ не является customer-facing обещанием и не подтверждает production,
UAT/go-live, интеграцию с площадкой заказчика, SLA, Part 11/QMS validation или
сертифицированную электронную подпись.

## Карта Потока

```text
0. Направление и границы
   -> 1. Intake и выбор среза
   -> 2. Task artifact и checklist
   -> 3. Разведка по коду и данным
   -> 4. Реализация
   -> 5. Локальная проверка
   -> 6. Независимое ревью
   -> 7. Исправление и hardening
   -> 8. Evidence capture
   -> 9. Обновление docs/state/memory
   -> 10. Local commit / PR handoff
   -> 11. Public/demo gate, если затронут стенд
   -> 12. Show pack или handoff следующего среза
```

## Основано На

- `STATE.md` - текущая правда проекта.
- `DECISIONS.md` - устойчивые технические и процессные решения.
- `docs/team-development/02-delivery-workflow.md` - workflow разработки.
- `docs/team-development/08-evidence-traceability.md` - evidence и трассировка.
- Текущая автономная практика по Alpha BPR: маленькие инкременты,
  task-папка, bounded Codex/Claude review, smoke/evidence, commit.

## Предположения

- Один агент может вести работу end-to-end, но процесс должен оставаться
  пригодным для команды.
- Публичный route по умолчанию считается curated/demo route. Любой
  `live-sandbox` режим означает только внутреннюю закрытую проверку
  sandbox-данных и не является customer plant integration, go-live или UAT.
- Claude review полезен как независимый архитектурный/UX/wording review, но
  timeout или no-verdict должен честно фиксироваться и не блокировать
  маленький verified increment бесконечно.

## Роли

| Роль | За что отвечает | Ограничение |
|---|---|---|
| Main agent | Scope, правки, проверки, evidence, commit decision | Не скрывает gaps и не делает неподтверждённые claim'ы |
| Codex reviewer | Code, tests, contracts, evidence consistency | Не принимает финальное решение вместо владельца среза |
| Claude reviewer | Architecture, UX, wording, claim boundaries | Получает только маленькие non-secret packets |
| Human owner | Направление, внешнее использование, бизнес-решения | Отдельно подтверждает отправку/публикацию наружу |

## 0. Направление И Границы

Цель: не начать работу, которая выглядит как прогресс, но ломает честные
границы проекта.

Входы:

- запрос или roadmap track;
- `STATE.md`;
- `DECISIONS.md`;
- текущие product/demo boundaries;
- список запрещённых claim'ов.

Выход:

- одна фраза с целью среза;
- явно понятные ограничения;
- понимание, затрагивается ли public/default route.

Stop conditions:

- задача требует production, UAT/go-live, customer plant integration, SLA,
  Part 11/QMS validation или certified e-signature claim без отдельного gate;
- review packet требует секреты или прямое чтение `/opt/alpha-bpr/env/*.env`;
- planned/blocked behavior предлагается описать как implemented.

## 1. Intake И Выбор Среза

Цель: выбрать маленький, законченный и проверяемый инкремент.

Хороший срез:

- один экран или одна lane в HMI;
- один API/read-model contract;
- один smoke/evidence hardening package;
- один customer-safe документ;
- один public monitor gate;
- один read-only proof перед будущим write gate.

Выход:

- названы файлы и модули;
- acceptance criteria проверяемы;
- requirement/backlog ID или причина отсутствия ID записаны;
- затронутые baseline docs названы или явно отмечены как not affected;
- внешние зависимости названы или явно отсутствуют;
- risk level оценён как low, medium, high или release-blocking;
- generated evidence не смешивается с source changes без осознанного решения;
- срез можно объяснить в одном коммите.

Definition of Ready: этот stage не заменяет
`docs/team-development/02-delivery-workflow.md`; work item считается Ready
только если выполнены требования Definition of Ready из
`docs/team-development/02-delivery-workflow.md`.

## 2. Task Artifact И Checklist

Цель: создать материальный артефакт до долгой автономной работы.

Обязательный минимум:

- `state/tasks/<date>-<topic>/TODO.md`, или
- целевой документ в `docs/`, или
- checklist рядом с изменяемым пакетом.

Checklist должен показывать:

- intake captured;
- relevant files inspected;
- implementation done;
- checks run;
- Codex/Claude review run или no-verdict recorded;
- evidence captured;
- docs/state/memory updated;
- commit/export status.

## 3. Разведка По Коду И Данным

Цель: сначала понять существующую систему, потом править.

Типовые действия:

- искать через `rg`, читать точечные фрагменты через `sed`;
- смотреть текущий `git status --short`;
- находить владельцев route, payload, UI render, smoke;
- отделять read model от write path;
- использовать Codex explorer для одного bounded вопроса, если это экономит
  время или снижает риск.

Выход:

- известны source-of-truth модели;
- известны существующие smokes/tests;
- известны места, где нельзя делать overclaim.

## 4. Реализация

Цель: сделать минимальный полезный change.

Правила:

- использовать существующие паттерны и helper'ы;
- не добавлять backend write behavior, если срез не является write gate;
- сохранять public/default route в curated-safe состоянии;
- писать UI wording честно: `read-only`, `preview`, `curated`, `evidence`,
  `report/read model`, если именно это и показано;
- не делать unrelated refactor.

Выход:

- изменение видно в UI/API/doc;
- fallback, empty и error states обработаны;
- имена новых contract fields стабильны.

## 5. Локальная Проверка

Цель: поймать дефекты до ревью.

Узкие проверки сначала:

- syntax checks: `py_compile`, `bash -n`, JS parse;
- direct function regression check;
- focused API/DOM smoke;
- `git diff --check`.

Широкие проверки по риску:

- `dotnet build`;
- `dotnet test`;
- integration tests;
- public monitor;
- browser screenshot/DOM evidence.

Выход:

- проверки соответствуют blast radius;
- failures исправлены или явно записаны как unrelated/blocking.

## 6. Независимое Ревью

Цель: поймать регрессии, слабые contracts и небезопасные claim'ы.

Codex review:

- code, tests, contracts, evidence consistency;
- bounded diff или список файлов;
- findings с file/line references.

Claude review:

- architecture, UX, wording, claim boundaries;
- packet 10-30 KB, максимум около 50 KB без отдельной причины;
- без секретов, raw env, huge DOM dumps и лишних screenshots;
- timeout/no-verdict фиксируется как evidence, а не скрывается.

Выход:

- blockers исправлены или работа остановлена;
- accepted findings применены;
- rejected findings имеют короткое объяснение.

## 7. Исправление И Hardening

Цель: применить ревью так, чтобы дефект был закрыт в источнике.

Типовые действия:

- выровнять BFF contract с существующей backend/read-model семантикой;
- добавить missing empty/error state;
- усилить smoke assertion;
- убрать overclaim wording;
- добавить regression check на найденный edge case.

Выход:

- finding исправлен не только визуально, но и в контракте/данных;
- финальные проверки перезапущены после фикса.

## 8. Evidence Capture

Цель: оставить воспроизводимый след результата.

Формы evidence:

- task `README.md` или `TODO.md`;
- JSON endpoint capture;
- rendered DOM;
- screenshots, если важна визуальная рамка;
- monitor output;
- checksums для packages;
- review packets и review results.

Границы:

- не коммитить секреты;
- не включать raw private URL/env/token wording в customer bundles;
- internal presenter brief держать отдельно от customer show pack.

## 9. Обновление Docs/State/Memory

Цель: синхронизировать репозиторий с фактическим состоянием.

Обновлять при значимой работе:

- `STATE.md` - текущая правда проекта;
- `DECISIONS.md` - устойчивые решения;
- `memory/YYYY-MM-DD.md` - дневной лог;
- затронутые `docs/`;
- task `TODO.md` с evidence и gaps.

Выход:

- implemented, planned и blocked не смешаны;
- следующие шаги понятны без истории чата.

## 10. Local Commit / PR Handoff

Цель: создать проверяемый локальный checkpoint и подготовить путь к командному
PR/merge gate.

Pre-commit:

- `git status --short`;
- staged diff содержит только нужный срез;
- `git diff --cached --check`;
- generated evidence добавлено осознанно или осознанно оставлено вне commit.

Формат:

```text
<type>: <short outcome>
```

Примеры:

- `feat: add Track E read-first plan fact lane`
- `docs: close Alpha BPR public demo gate`
- `test: harden HMI overview smoke with Claude review`

Выход:

- commit hash известен;
- worktree clean или содержит только известные unrelated untracked files;
- для командной работы следующий gate - branch/PR/review/required checks/merge
  из `docs/team-development/02-delivery-workflow.md`;
- локальный autonomous commit не заменяет protected-main, PR review и merge
  policy из controlled team workflow.

## 11. Public/Demo Gate

Цель: доказать, что demo surface всё ещё можно показывать в заявленных границах.

Использовать, если изменились:

- public HMI/BFF route;
- customer show pack;
- public monitor contract;
- ontology/public readiness claim;
- customer-facing wording.

Проверки:

- public monitor;
- ontology guard, если применимо;
- stop-string scan;
- raw host/localhost/env/token wording scan;
- desktop/mobile DOM или screenshots.

Выход:

- public route остаётся curated-safe;
- wording говорит, что demo доказывает и чего не доказывает.
- если проверялся `live-sandbox`, результат формулируется только как
  внутренняя закрытая sandbox-проверка на подготовленном стенде; это не
  customer route, не production/UAT, не интеграция с площадкой заказчика и не
  разрешение на внешнее использование.

## 12. Show Pack Или Handoff Следующего Среза

Цель: превратить increment в понятный следующий шаг.

Выходы:

- customer-safe one-pager или show pack;
- internal presenter brief;
- следующий технический slice с boundaries;
- known gaps и stop conditions.

## Quality Checklist

- Scope = один coherent increment.
- Task artifact создан до глубокой автономной работы.
- `STATE.md`, `DECISIONS.md` и дневная память проверены.
- Реализация использует существующие patterns.
- Read/write boundary явно проговорен.
- Public/default route остаётся safe.
- Claims подкреплены evidence.
- Codex/Claude review применён для non-trivial slice или no-verdict записан.
- Accepted findings исправлены.
- Checks/evidence записаны.
- Docs/state/memory обновлены.
- Commit сделан только после verified slice.

## Открытые Вопросы

- Сделать ли эту карту controlled guidance v0.2 после ещё 1-2 автономных
  инкрементов.
- Нужен ли reusable review-packet template для HMI/BFF slices.
- Нужно ли отделить большие DOM evidence от source commits в более лёгкий
  archive pattern.
