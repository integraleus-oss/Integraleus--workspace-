# Alpha BPR - аудит меню и процедур

Статус: черновик аудита, 2026-07-21.

## Назначение

Этот документ фиксирует, какие меню и процедуры в текущем Alpha BPR HMI/BFF
product trial уже работают на live API, какие работают частично, а какие
являются статическим демо/fallback или заглушкой.

## Проверенная поверхность

Проверялась текущая Home HMI/BFF поверхность:

- локальный маршрут: `http://127.0.0.1:5095/`;
- публичный маршрут готовности:
  `http://alpha-bpr.31.10.95.23.sslip.io/alpha-bpr-hmi/readyz`;
- основной UI: `docs/hmi/prototype/alpha-bpr-integrated-hmi-prototype.html`;
- HMI/BFF facade: `scripts/demo/hmi_bff_demo_server.py`;
- Alpha BPR API endpoints: `src/AlphaBpr.Api/**`.

Runtime-проверка на момент аудита:

```text
GET /readyz -> status=ready, bpr.status=reachable
GET /api/demo/recipe-workbench -> source=trial-curated, apiReachable=true,
  recipeCount=3, selectedRecipeId=null, hmiBatchesCount=0
GET /api/demo/reviewer -> source=evidence, healthOk=true, readyOk=true,
  auditReviewsOk=true, ebrPresent=true, reportPresent=true
```

Вывод: BFF и Alpha BPR API доступны, но текущая публичная recipe workbench
поверхность намеренно показывает curated trial-набор, а не полную live
библиотеку рецептов/партий.

## Легенда статусов

| Статус | Значение |
| --- | --- |
| Работает | Действие реально читает или меняет Alpha BPR API через HMI/BFF или прямой API. |
| Частично работает | Экран есть, часть данных live/evidence-backed, но ключевое действие ограничено или не связано с текущим объектом. |
| Trial/demo | Экран показывает заранее подготовленный trial/evidence/fallback сценарий; полезен для демонстрации, но не является полноценным рабочим контуром. |
| Заглушка | Элемент интерфейса есть, но действие только переключает UI/показывает toast/не ведёт к live API. |

## Сводка по верхним меню

| Меню | Что показывает | Текущий статус | Основание |
| --- | --- | --- | --- |
| Библиотека рецептов | Список рецептов, карточка рецепта, операции, формула, оборудование, карточки партий | Trial/demo | `/api/demo/recipe-workbench` возвращает `source=trial-curated`; рецепты curated, `selectedRecipeId=null`; batch cards берутся из JS fallback-набора. |
| Создать рецепт | Мастер карточки: код, название, партия, оборудование, шаблон, автор, причина | Trial/demo | UI создаёт черновик в массиве `RECIPES` в браузере; нет `POST /api/recipes/` из этой формы. |
| Редактор процедур | Операции, фазы, критичность, длительность, причина изменения | Частично работает | UI умеет локально править trial-данные; HMI/BFF имеет live endpoint `/api/demo/recipe-workbench/{id}/procedure`, но текущие curated рецепты не несут `apiId`, поэтому public trial не вызывает live save. |
| Формулы | Компоненты, уставки, допуски, тип строки, проверки, причина изменения | Частично работает | Аналогично процедурам: live endpoint есть (`/{id}/formula`), но текущий public trial работает по curated объектам без `apiId`. |
| Партии | EBR: материалы, лоты, дозирование, line clearance, QA, snapshot, release gates, печать/PDF | Trial/demo | Integrated UI показывает встроенный batch fallback-набор; `recipe-workbench` сейчас отдаёт `hmiBatches=[]`. Отдельные live API для batch/EBR существуют. |
| Ревью QA | Очередь QA, гейты выпуска, дозирование, подпись QA, audit review | Частично работает | `/api/demo/reviewer` читает health/ready/audit reviews live, но EBR/report берёт live только при `state.batch_id`; без batch использует evidence JSON. |
| Версии и аудит | Diff версий рецепта, сводка изменений, approve из diff | Trial/demo / частично работает | HMI/BFF содержит методы live diff, но текущий workbench возвращает `apiDiff.ok=false` и сообщение, что public trial diff curated in HMI. |
| Согласование | Очередь решений, пакет владельца, проверки, журнал, approve/return | Trial/demo / частично работает | Очередь строится из curated рецепта в согласовании; кнопки approve/return активны только при `apiId`, которого в текущем public trial нет. |

## Процедуры внутри продукта

### 1. Создание рецепта / процедуры

Ожидаемый продуктовый смысл:

1. технолог создаёт черновик рецепта;
2. заполняет формулу и процедуру;
3. отправляет черновик на согласование;
4. reviewer утверждает;
5. версия становится effective и может использоваться для партии.

Что реализовано в backend:

- `POST /api/products/` - создать продукт;
- `POST /api/recipes/` - создать рецепт;
- `PUT /api/recipes/{id}` - изменить рецепт или создать successor для active;
- `POST /api/recipes/{id}/submit-review` - отправить на согласование;
- `POST /api/recipes/{id}/approve` - утвердить;
- `POST /api/recipes/{id}/return-review` - вернуть на доработку;
- `POST /api/recipes/{id}/make-effective` - сделать effective;
- `POST /api/recipes/{id}/activate` - активировать;
- `POST /api/recipes/{id}/publish` - deprecated alias для activate.

Что реализовано в UI:

- мастер `Создать рецепт` создаёт локальный demo-черновик;
- кнопки `Далее: формула`, `Далее: процедура`, `К согласованию` переводят
  пользователя по экранному сценарию;
- в текущем public trial это не пишет новый рецепт в Alpha BPR API.

Статус: backend работает; UI-мастер создания нового рецепта в public trial -
demo/fallback.

### 2. Редактирование процедуры

Ожидаемый продуктовый смысл:

- изменить последовательность операций;
- добавить/удалить операцию;
- изменить длительность;
- добавить/удалить фазу;
- отметить критичность фазы;
- сохранить изменение с причиной для audit trail.

Что реализовано в backend/HMI-BFF:

- HMI/BFF endpoint `POST /api/demo/recipe-workbench/{recipeId}/procedure`;
- он читает рецепт через `GET /api/recipes/{id}`;
- строит `PUT /api/recipes/{id}` с `steps`;
- требует `note`, иначе возвращает ошибку `Change reason is required for recipe audit`.

Ограничения:

- mapping HMI phase -> backend step parameter упрощённый: фаза превращается в
  `RecipeStepParameter`, критичность кодируется через `unit=critical`;
- existing `tagBindings` и `equipmentPhases` сохраняются только из старого шага;
- текущие curated рецепты public trial не имеют `apiId`, поэтому live save не
  вызывается.

Статус: частично работает; серверная возможность есть, текущая публичная
поверхность показывает demo-редактирование.

### 3. Редактирование формулы

Ожидаемый продуктовый смысл:

- изменить компоненты;
- изменить уставки;
- изменить допуски;
- добавить/удалить строку;
- сохранить изменение с причиной.

Что реализовано в backend/HMI-BFF:

- HMI/BFF endpoint `POST /api/demo/recipe-workbench/{recipeId}/formula`;
- он читает рецепт через `GET /api/recipes/{id}`;
- строит `PUT /api/recipes/{id}` с `components` и `parameters`;
- UI валидирует числовые поля перед сохранением.

Ограничения:

- строка типа `mat` превращается в component;
- строка типа `par` превращается в recipe parameter;
- parsing уставок/допусков ориентирован на демонстрационные форматы;
- текущий public trial без `apiId` сохраняет изменения только в браузерной
  модели.

Статус: частично работает.

### 4. Согласование рецепта

Ожидаемый продуктовый смысл:

- reviewer видит очередь;
- открывает diff;
- проверяет технологию, QA, validation, audit;
- утверждает или возвращает на доработку.

Что реализовано:

- backend lifecycle endpoints `submit-review`, `approve`, `return-review`,
  `make-effective`;
- HMI/BFF endpoints `/{id}/submit-review`, `/{id}/approve`, `/{id}/return-review`;
- UI отключает live approve/return, если у элемента нет `apiId`.

Текущий public trial:

- очередь строится из curated trial recipe `MR-PA66-03 v2.5`;
- `approvalStatus` показывает fallback/trial состояние;
- approve/return для curated элемента недоступны как live API action.

Статус: backend работает; текущий UI-сценарий согласования - trial/demo, live
действия возможны только для объектов с `apiId`.

### 5. Версии и аудит

Ожидаемый продуктовый смысл:

- показать версии одного recipe code;
- построить diff;
- показать audit evidence;
- утвердить версию из diff.

Что реализовано:

- backend `GET /api/recipes/{code}/versions`;
- backend `GET /api/recipes/{id}/diff`;
- backend `GET /api/audit/export`;
- HMI/BFF методы `recipe_versions`, `recipe_diff`, `recipe_audit_export`.

Текущий public trial:

- `recipe-workbench` возвращает `apiDiff.ok=false` с текстом, что diff curated;
- audit export для recipe workbench недоступен в public trial;
- UI показывает встроенный diff MR-PA66-03 v2.4 -> v2.5.

Статус: backend работает; текущая вкладка public trial - curated demo.

### 6. Партии / EBR

Ожидаемый продуктовый смысл:

- создать партию из effective recipe;
- зафиксировать immutable snapshot;
- вести материалы, лоты, дозирование, line clearance;
- показывать QA exceptions;
- скачать/открыть report dataset/PDF/XLSX.

Что реализовано в backend:

- `POST /api/batches/`;
- `POST /api/orders/{id}/batch`;
- `GET /api/batches/{id}/ebr`;
- `GET /api/batches/{id}/report-dataset`;
- `GET /api/batches/{id}/report`;
- `POST /api/batches/{id}/dose-record`;
- `POST /api/batches/{id}/line-clearance`;
- `POST /api/batches/{id}/qa-release`;
- report archive endpoints.

Что показывает current UI:

- batch cards из встроенного JS-набора (`BATCH-2607-012/013/014/015`);
- EBR screen с материалами, lot status, potency correction, line clearance,
  QA exceptions, snapshot, gates и print/PDF preview;
- `recipe-workbench` сейчас отдаёт `hmiBatches=[]`, поэтому карточки не
  перечитываются из live `/api/batches`.

Статус: backend работает; текущая integrated HMI вкладка - demo/evidence view.

### 7. Ревью QA

Ожидаемый продуктовый смысл:

- QA проверяет EBR, exceptions, dose evidence, line clearance, report artifacts;
- принимает решение release/hold/reject;
- решение попадает в audit/review records.

Что реализовано:

- backend `POST /api/batches/{id}/qa-release`;
- backend audit review endpoints `POST /api/audit/reviews`, `GET /api/audit/reviews`;
- HMI/BFF `/api/demo/reviewer` читает health/ready и audit reviews live;
- если в HMI/BFF state есть `batch_id`, он пытается читать live
  `/api/batches/{id}/ebr` и `/report-dataset`.

Текущий public trial:

- без активного `state.batch_id` QA экран использует evidence JSON для EBR и
  report dataset;
- audit reviews читаются live;
- подпись QA в integrated HMI является демо-визуализацией и не является
  validated/certified electronic signature.

Статус: частично работает.

### 8. Операторский runtime workflow

Ожидаемый продуктовый смысл:

- создать order;
- получить setpoints;
- release order;
- отправить PLC status;
- записать dose record;
- получить report.

Что реализовано в HMI/BFF:

- `POST /api/demo/create-order` реально создаёт product, recipe, order;
- `GET /api/demo/setpoints` читает order setpoints;
- `POST /api/demo/release` release order и создаёт batch;
- `POST /api/demo/plc-status` и `/dose-record` отправляют adapter/evidence
  события;
- `GET /api/demo/report` читает report dataset.

Статус: работает как live demo workflow, отдельный от integrated menu
recipe-workbench curated surface.

### 9. MVP v0.1 sandbox run

Что реализовано:

- `POST /api/demo/mvp-v0-1` выполняет сквозной live API сценарий:
  product -> recipe -> revision -> submit-review -> approve -> make-effective
  -> order -> setpoints -> release -> batch -> dose-record -> line-clearance
  -> start/complete -> QA release -> EBR/report/audit.

Статус: работает как live smoke/демо-процедура через endpoint/script, но не
разложен на полноценные пользовательские кнопки во всех integrated HMI меню.

## Основные разрывы между UI и backend

1. Создание нового рецепта в integrated UI не пишет `POST /api/recipes/`.
2. Current public `recipe-workbench` показывает curated trial-набор даже при
   доступном API.
3. Редактор процедур и формул имеют live endpoints, но текущие публичные
   рецепты не имеют `apiId`, поэтому действия остаются локальными.
4. Вкладка `Партии` показывает встроенные EBR cards, хотя backend batch/EBR API
   есть и работает отдельно.
5. `Ревью QA` смешивает live health/audit reviews с evidence EBR/report, если
   текущий BFF state не содержит batch.
6. `Версии и аудит` в public trial показывает curated diff, хотя backend diff
   endpoints существуют.
7. Часть фильтров в `Согласование` и `Ревью QA` переключает UI/toast и не
   фильтрует live API выборки.
8. PDF/печать в integrated HMI - browser print preview, не тот же путь, что
   backend report/PDF archive.

## Рекомендованный следующий backlog

| Приоритет | Работа | Зачем |
| --- | --- | --- |
| P0 | Выбрать честный режим public trial: curated showcase или live sandbox authoring. | Сейчас оба слоя существуют, но пользователь видит curated UI при reachable API. |
| P0 | Если нужен live authoring: добавить `apiId` в recipe cards или вернуть live recipe list в `recipe-workbench`. | Без этого formula/procedure/approval кнопки не вызывают live save. |
| P1 | Подключить `Создать рецепт` к `POST /api/recipes/` через HMI/BFF. | Закрывает главный вопрос пользователя: как создаётся новая процедура. |
| P1 | Подключить `Партии` к live `/api/batches` + `/api/batches/{id}/ebr` или явно маркировать как evidence. | Убирает путаницу между демо-карточками и реальными партиями. |
| P1 | Разделить в UI badges: `Live API`, `Trial curated`, `Evidence fallback`. | Пользователь сразу видит, что настоящее, а что демонстрационное. |
| P2 | Сделать фильтры `Ревью QA`/`Согласование` настоящими фильтрами данных. | Сейчас часть фильтров только визуальная. |
| P2 | Свести report/PDF кнопки к backend report/archives или явно назвать browser print preview. | Убирает риск ложного ожидания архивного PDF. |

## Не-заявления

Этот аудит не утверждает:

- production deployment/go-live;
- production identity/TLS;
- Part 11/QMS validation;
- certified electronic signatures;
- customer plant integration;
- SLA/24x7 readiness.

## Основано на

- `docs/hmi/prototype/alpha-bpr-integrated-hmi-prototype.html`;
- `scripts/demo/hmi_bff_demo_server.py`;
- `src/AlphaBpr.Api/Recipes/RecipeEndpoints.cs`;
- `src/AlphaBpr.Api/Batches/BatchEndpoints.cs`;
- `src/AlphaBpr.Api/Auditing/AuditEndpoints.cs`;
- `docs/release/alpha-bpr-mvp-v0-1-product-trial-20260716.md`;
- runtime checks against `http://127.0.0.1:5095`.
