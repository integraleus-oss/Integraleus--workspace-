# Alpha BPR - план реализации полноценного продукта

Статус: черновик плана реализации, 2026-07-21.

## Назначение

Этот документ превращает аудит меню и процедур в практический план реализации
полноценного Alpha BPR product trial: что нужно сделать по backend, HMI/BFF,
UI-меню, проверкам, документации и демонстрационным границам.

## Исходное состояние

По аудиту от 2026-07-21:

- backend уже содержит lifecycle рецептов, партий, EBR, QA release, audit и
  report endpoints;
- HMI/BFF и Alpha BPR API доступны на Home;
- текущий public `recipe-workbench` намеренно отдаёт `source=trial-curated`;
- integrated HMI показывает полный пользовательский маршрут, но часть меню
  работает как curated/evidence demo;
- полноценный live-authoring через все меню ещё не включён.

Главный продуктовый разрыв: пользователь видит полноценный интерфейс, но не все
кнопки в нём являются live API действиями.

## Целевая граница продукта

Цель ближайшей реализации: сделать Alpha BPR полноценным live product trial,
где пользователь через HMI/BFF может пройти сквозной workflow:

```text
создать рецепт -> заполнить формулу -> заполнить процедуру ->
отправить на согласование -> утвердить -> make-effective ->
создать партию -> вести EBR -> QA review -> report/audit
```

Это остаётся non-production product trial. План не включает:

- regulated production go-live;
- Part 11/QMS validation;
- certified electronic signatures;
- production identity/TLS;
- customer plant integration;
- SLA/24x7;
- off-machine backup/retention automation.

## Принцип реализации

1. Сначала убрать двусмысленность `trial-curated` vs live API.
2. Затем подключить живое создание и редактирование рецепта.
3. Потом подключить live batch/EBR/QA/report.
4. После этого довести UX: фильтры, статусы, ошибки, empty states.
5. Каждый этап закрывать smoke/evidence, а не словами.

## Этап 0. Зафиксировать режим product trial

### Цель

Принять один честный режим для публичной поверхности:

- `curated showcase` - всё явно демо/evidence, без ожидания live authoring;
- `live sandbox authoring` - пользователь реально создаёт и меняет sandbox
  recipes/batches через API.

Для полноценного продукта нужен второй режим: `live sandbox authoring`.

### Работы

- Добавить явный config flag в HMI/BFF:
  `HMI_BFF_TRIAL_MODE=curated|live-sandbox`.
- В `live-sandbox` вернуть live recipe list из Alpha BPR API.
- В `curated` показывать на UI заметный badge `Trial curated`.
- Не смешивать curated recipes и live actions в одном payload без явной метки.

### Файлы

- `scripts/demo/hmi_bff_demo_server.py`;
- `docs/hmi/prototype/alpha-bpr-integrated-hmi-prototype.html`;
- `deploy/hmi-bff-webviewer-demo.env.example`;
- `docs/hmi/prototype/README.md`.

### Acceptance criteria

- `/api/demo/recipe-workbench` возвращает `source=live-api` в live-sandbox
  режиме и recipes с `apiId`.
- `/api/demo/recipe-workbench` возвращает `source=trial-curated` только в
  curated режиме.
- UI header показывает `Данные: сервер`, `Данные: trial` или `Данные: демо`
  без скрытой логики.

### Проверки

```bash
HMI_BFF_TRIAL_MODE=live-sandbox python3 scripts/demo/hmi_bff_demo_server.py --port 5198 --bpr-base http://127.0.0.1:5088
curl -fsS http://127.0.0.1:5198/api/demo/recipe-workbench | jq '{source, recipeCount:(.recipes|length), selectedRecipeId}'
```

## Этап 1. Live library и карточка рецепта

### Цель

Меню `Библиотека рецептов` должно показывать реальные sandbox recipes из
Alpha BPR API и позволять открыть карточку live recipe.

### Работы

- Вернуть/доработать live загрузку `GET /api/recipes`.
- Сохранять `apiId` в каждой recipe card.
- Поддержать статусы `Draft`, `InReview`, `Approved`, `Active`,
  `Superseded`, `Archived`.
- Добавить фильтры по статусам, которые работают на live dataset.
- Показывать empty state, если recipes нет.
- Не показывать internal sandbox codes в public health/readiness payloads.

### Файлы

- `scripts/demo/hmi_bff_demo_server.py`;
- `docs/hmi/prototype/alpha-bpr-integrated-hmi-prototype.html`;
- `src/AlphaBpr.Api/Recipes/RecipeEndpoints.cs` при необходимости расширения
  query parameters.

### Acceptance criteria

- `Библиотека рецептов` отображает live recipes с `apiId`.
- Выбор рецепта открывает live formula/procedure/equipment summary.
- Кнопки procedure/formula/approval становятся live-доступными для live recipe.
- Фильтры не являются toast-заглушками.

### Проверки

```bash
curl -fsS http://127.0.0.1:5095/api/demo/recipe-workbench | jq '.source, [.recipes[].apiId] | length'
HMI_BFF_URL=http://127.0.0.1:5095 scripts/demo/hmi-bff-mvp-v0-1-smoke.sh
```

## Этап 2. Создание рецепта из UI

### Цель

Меню `Создать рецепт` должно реально создавать draft recipe в Alpha BPR API,
а не только локальный объект в браузере.

### Работы

- Добавить HMI/BFF endpoint `POST /api/demo/recipe-workbench/create`.
- Маппить поля UI:
  - code -> recipe code;
  - name -> recipe name;
  - batch size -> governance preferred/min/max или base volume;
  - equipment -> governance equipmentId;
  - template -> starter components/steps;
  - author/reason -> forwarded attribution/changeComment.
- Вернуть созданный recipe с `apiId`.
- После создания автоматически выбрать live draft в библиотеке.
- Заблокировать `К согласованию`, пока формула/процедура не проходит
  server validation.

### Backend/API

Используются существующие endpoints:

- `POST /api/products/` при необходимости создать product;
- `POST /api/recipes/`;
- `GET /api/recipes/{id}/validation`.

Если product обязательный для выбранного сценария, HMI/BFF должен либо выбрать
существующий sandbox product, либо создать его явно и показать это в result.

### Acceptance criteria

- Нажатие `Создать черновик` приводит к `POST /api/recipes/`.
- Новый рецепт появляется после refresh `/api/demo/recipe-workbench`.
- У рецепта есть `apiId`, status `Draft`, author/change reason.
- Ошибки backend validation показываются пользователю без stack trace.

### Проверки

```bash
curl -fsS -X POST http://127.0.0.1:5095/api/demo/recipe-workbench/create \
  -H 'Content-Type: application/json' \
  -d '{"code":"MR-UI-SMOKE-001","name":"UI smoke recipe","template":"mix","equipmentId":"MIX01","reason":"UI create smoke"}' | jq '{recipe:.recipe.code,status:.recipe.status,apiId:.recipe.id}'
```

## Этап 3. Редактор формулы как live authoring

### Цель

Меню `Формулы` должно редактировать live draft/successor recipe и сохранять
изменения через API.

### Работы

- Уточнить mapping UI rows:
  - material rows -> recipe `components`;
  - process parameter rows -> recipe `parameters`;
  - units and tolerances -> typed values, не свободный текст где возможно.
- Добавить preview преобразования перед сохранением.
- Поддержать создание successor при редактировании active recipe.
- После `PUT /api/recipes/{id}` перечитывать recipe и обновлять UI.
- Вынести parser setpoint/tolerance в тестируемые функции.

### Acceptance criteria

- Сохранение формулы требует reason.
- Невалидная числовая уставка/допуск блокируется до API call.
- Valid save меняет live recipe или создаёт successor.
- Audit/changeComment присутствует в ответе recipe.

### Проверки

```bash
python3 -m py_compile scripts/demo/hmi_bff_demo_server.py
dotnet test tests/AlphaBpr.Tests -c Release --filter Recipe
```

## Этап 4. Редактор процедур как live authoring

### Цель

Меню `Редактор процедур` должно редактировать реальные recipe steps, phases,
durations и critical points.

### Работы

- Перестать кодировать critical только через `unit=critical`, если для продукта
  нужен отдельный typed field.
- Сохранить или явно редактировать:
  - step number;
  - operation name;
  - target duration;
  - phase/parameter list;
  - tag bindings;
  - equipment phases.
- Добавить validation summary перед отправкой на согласование.
- Поддержать copy-from-template для нового рецепта.

### Возможная backend доработка

Если текущая модель `RecipeStepParameter` недостаточно выражает фазу, добавить
или расширить DTO для UI-level phase representation без потери совместимости.

### Acceptance criteria

- Добавление/удаление операции сохраняется в live recipe.
- Добавление/удаление фазы сохраняется в live recipe.
- Длительность сохраняется как typed duration.
- Existing tag/equipment bindings не теряются при UI save.
- Backend validation видит обновлённые steps.

### Проверки

```bash
dotnet test tests/AlphaBpr.Tests -c Release --filter RecipeStep
python3 -m py_compile scripts/demo/hmi_bff_demo_server.py
```

## Этап 5. Согласование и версии

### Цель

Меню `Согласование` и `Версии и аудит` должны работать с live review queue,
diff и audit evidence.

### Работы

- Использовать `GET /api/recipes/review-queue`.
- Для выбранного item читать:
  - `GET /api/recipes/{id}`;
  - `GET /api/recipes/{id}/diff`;
  - `GET /api/audit/export?entityId={id}`.
- Кнопки:
  - `УТВЕРДИТЬ` -> `POST /api/recipes/{id}/approve`;
  - `ВЕРНУТЬ НА ДОРАБОТКУ` -> `POST /api/recipes/{id}/return-review`;
  - `Сделать effective` -> `POST /api/recipes/{id}/make-effective`.
- Разделить status `Approved` и `Active`: approved ещё не обязательно
  executable для batch.
- Добавить audit checksum/record count в owner package.

### Acceptance criteria

- Queue показывает live рецепты на согласовании.
- Diff строится из backend response.
- Approve/return реально меняет status.
- Make-effective supersedes предыдущую active версию без изменения batch
  snapshots.
- UI не разрешает batch start из Approved-but-not-effective recipe.

### Проверки

```bash
dotnet test tests/AlphaBpr.IntegrationTests -c Release --filter Recipe
curl -fsS http://127.0.0.1:5095/api/demo/recipe-workbench | jq '.approvalQueue'
```

## Этап 6. Партии и EBR как live menu

### Цель

Меню `Партии` должно показывать реальные sandbox batches и EBR, а не встроенный
JS-набор.

### Работы

- В `recipe-workbench` вернуть `hmiBatches` из:
  - `GET /api/batches`;
  - `GET /api/batches/{id}/ebr`;
  - `GET /api/batches/{id}/report-dataset`.
- Поддержать создание batch из active recipe через UI:
  - create order;
  - release order;
  - create batch;
  - start/complete или controlled demo execution.
- Материалы, line clearance, dose records и QA exceptions читать из backend
  read model.
- Явно показывать fallback, если batch EBR не найден.

### Acceptance criteria

- `Партии` отображает live batch list.
- Открытие batch показывает live EBR.
- Empty queue не показывает fake batch cards.
- `Печать / PDF` ведёт к backend report или явно названа browser preview.

### Проверки

```bash
curl -fsS http://127.0.0.1:5095/api/demo/recipe-workbench | jq '.hmiBatches | length'
dotnet test tests/AlphaBpr.IntegrationTests -c Release --filter Batch
```

## Этап 7. Ревью QA и report/audit closeout

### Цель

Меню `Ревью QA` должно закрывать live QA review для выбранной партии.

### Работы

- Строить QA queue из live batches:
  - completed but not released;
  - held;
  - with open QA exceptions;
  - released for audit review.
- Для выбранной партии читать live EBR/report/audit.
- Кнопки:
  - `ОТКРЫТЬ ЭЗП` -> live EBR;
  - `ОТЧЁТ PDF` -> backend report endpoint;
  - `ПОДПИСЬ QA` -> в trial режиме `qa-release`, не certified signature.
- Записывать QA release через `POST /api/batches/{id}/qa-release`.
- Audit review rows читать из `/api/audit/reviews`.

### Acceptance criteria

- QA queue не является static list.
- QA release меняет batch release state.
- Report link/download открывает backend artifact.
- UI явно говорит, что подпись trial не certified e-signature.

### Проверки

```bash
curl -fsS http://127.0.0.1:5095/api/demo/reviewer | jq '{source, auditReviews:.auditReviews.ok, ebr:(.ebr!=null)}'
dotnet test tests/AlphaBpr.IntegrationTests -c Release --filter Qa
```

## Этап 8. UX hardening и product polish

### Цель

Сделать продукт понятным и честным для пользователя, без скрытых заглушек.

### Работы

- Везде добавить одинаковые source badges:
  - `Live API`;
  - `Trial curated`;
  - `Evidence fallback`;
  - `Offline`.
- Заменить toast-заглушки на disabled state или real filters.
- Добавить loading/error/empty states для каждого меню.
- Убрать неоднозначные действия, если нет `apiId`.
- Разделить `PDF preview` и `backend report PDF`.
- Добавить route/hash coverage:
  - `#library`;
  - `#create`;
  - `#procedure`;
  - `#formula`;
  - `#approval`;
  - `#versions`;
  - `#batches`;
  - `#qa`.
- Добавить screenshot smoke для desktop/mobile.

### Acceptance criteria

- Пользователь всегда понимает, какие данные live.
- Нет кнопок, которые выглядят live, но только меняют локальный JS.
- Все меню имеют empty/error state.
- Текст не заявляет production/compliance claims.

### Проверки

```bash
HMI_BFF_URL=http://127.0.0.1:5095 scripts/demo/hmi-bff-mvp-v0-1-smoke.sh
python3 -m py_compile scripts/demo/hmi_bff_demo_server.py
dotnet test -c Release
```

## Меню -> требуемые функции

| Меню | Must-have для полноценного product trial | Backend/API | HMI/BFF | UI |
| --- | --- | --- | --- | --- |
| Библиотека рецептов | Live list, filters, selected card, active/effective state | `GET /api/recipes`, `GET /api/recipes/{id}` | `recipe-workbench` live mode | Cards with `apiId`, source badge |
| Создать рецепт | Real draft creation | `POST /api/products`, `POST /api/recipes` | `POST /recipe-workbench/create` | Wizard writes to API |
| Формулы | Edit formula/components/parameters | `PUT /api/recipes/{id}` | `/{id}/formula` | Typed rows, validation |
| Редактор процедур | Edit steps/phases/duration/bindings | `PUT /api/recipes/{id}`, validation | `/{id}/procedure` | Step/phase editor with reason |
| Согласование | Live queue, approve, return, make-effective | `review-queue`, `approve`, `return-review`, `make-effective` | queue facade/actions | Owner package + action states |
| Версии и аудит | Live versions, diff, audit export | `versions`, `diff`, `audit/export` | diff/audit facade | Diff table from API |
| Партии | Live batch list and EBR | `batches`, `ebr`, report endpoints | `hmiBatches` from API | No fake cards in live mode |
| Ревью QA | Live QA queue and release decision | `qa-release`, `audit/reviews` | reviewer facade | Release/hold/reject flow |

## Recommended implementation order

1. `P0-mode`: introduce explicit `curated|live-sandbox` mode and source badges.
2. `P1-live-library`: restore live recipe list with `apiId`.
3. `P1-create-recipe`: make `Создать рецепт` write to API.
4. `P1-edit-formula-procedure`: make formula/procedure edits round-trip to API.
5. `P1-approval-diff`: wire live review queue, diff, approve/return/make-effective.
6. `P2-batches-ebr`: make `Партии` read live batches/EBR.
7. `P2-qa-report`: make `Ревью QA` close live QA release/report/audit.
8. `P2-polish`: remove placeholder filters, improve empty/error states, screenshots.

## Task packaging recommendation

Do not implement this as one huge run. Use bounded agent packets:

### Packet A - Source Mode And Live Library

Goal: make `recipe-workbench` honestly switch between curated and live-sandbox,
and make `Библиотека рецептов` consume live recipes with `apiId`.

Acceptance:

- live mode returns `source=live-api`;
- curated mode returns `source=trial-curated`;
- UI badges match payload source;
- tests/smoke pass.

### Packet B - Create Recipe Wizard

Goal: connect `Создать рецепт` to HMI/BFF + Alpha BPR API.

Acceptance:

- new recipe persists;
- created recipe appears in library;
- validation errors are visible;
- no stack traces leak to UI.

### Packet C - Formula/Procedure Authoring

Goal: make `Формулы` and `Редактор процедур` reliable live editors.

Acceptance:

- formula changes survive refresh;
- procedure changes survive refresh;
- reason is mandatory;
- tag/equipment binding loss is tested.

### Packet D - Approval And Versions

Goal: live queue, diff, approve/return/make-effective.

Acceptance:

- status transitions are server-backed;
- approved and active/effective are visually distinct;
- audit evidence appears in owner package.

### Packet E - Batches, EBR, QA

Goal: replace static batch cards with live sandbox batch/EBR/QA release.

Acceptance:

- `Партии` shows live batches;
- `Ревью QA` acts on live selected batch;
- report/PDF route is backend-backed or clearly preview-only.

## Verification matrix

| Level | Check |
| --- | --- |
| Static | `python3 -m py_compile scripts/demo/hmi_bff_demo_server.py` |
| Unit | `dotnet test tests/AlphaBpr.Tests -c Release` |
| Integration | `dotnet test tests/AlphaBpr.IntegrationTests -c Release` |
| HMI smoke | `HMI_BFF_URL=http://127.0.0.1:5095 scripts/demo/hmi-bff-mvp-v0-1-smoke.sh` |
| Runtime | curl `/readyz`, `/api/demo/recipe-workbench`, `/api/demo/reviewer` |
| UX evidence | desktop/mobile screenshots of every menu in live mode |
| Regression | `git diff --check`, no secrets, no internal paths in public payloads |

## Stop conditions

Stop and ask for owner decision before:

- enabling production identity/TLS;
- claiming Part 11/QMS/e-signature compliance;
- exposing private/internal recipe codes in public payloads;
- connecting to customer plant/runtime write paths;
- changing backup/retention/off-machine copy behavior;
- deploying as production instead of product trial.

## Definition of done for "full product trial"

The product trial can be called functionally complete when:

1. every top-level menu has either live behavior or an explicit visible
   trial/evidence label;
2. recipe creation, formula editing, procedure editing, approval and
   make-effective work from UI without Swagger;
3. batches and EBR shown in `Партии` come from backend read models;
4. QA review can close a live sandbox batch;
5. report/audit evidence is reachable from UI;
6. MVP smoke passes after restart;
7. docs/user guide and audit report match the actual behavior;
8. no customer-facing text claims production/compliance readiness.

## Основано на

- `docs/audit/alpha-bpr-menu-procedure-audit-20260721.md`;
- `docs/user/alpha-bpr-menu-procedure-guide-ru.md`;
- `docs/release/alpha-bpr-mvp-v0-1-product-trial-20260716.md`;
- `docs/hmi/prototype/alpha-bpr-integrated-hmi-prototype.html`;
- `scripts/demo/hmi_bff_demo_server.py`;
- `src/AlphaBpr.Api/**`;
- runtime checks from the 2026-07-21 audit.
