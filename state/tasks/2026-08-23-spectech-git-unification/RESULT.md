# Результат унификации Git

## Выполнено

- 48 записей исходного `git status` `specialtechnology.ru` сверены с production.
- 48/48 подтверждены как уже опубликованное состояние.
- Старый репозиторий очищен фиксацией baseline:
  - commit `08ca6cc Reconcile source with live production state`;
  - рабочее дерево после коммита чистое.
- Создан канонический monorepo:
  - path: `/home/stanislav/projects/spectech-sites`;
  - branch: `main`;
  - commit: `9f2f4e6 Create canonical monorepo for Spectech sites`.
- Импортированы:
  - `sites/specialtechnology/`;
  - `sites/special-tech/`;
  - `packages/cms-adapters/` placeholder;
  - проектные документы и release policy.
- Не импортированы: secrets, `/lk/**`, БД, uploads, backups, `node_modules`, `dist`, `.astro`.
- Старый `deploy.php` с встроенным ключом исключён из monorepo и добавлен в `.gitignore`.

## Проверки

- Astro: `npm ci --ignore-scripts --no-audit --no-fund` — успешно.
- Astro: `npm run build` — успешно, 17 страниц, sitemap создан.
- Staged forbidden-path scan — чисто.
- Staged secret scan — чисто.
- Git status обоих репозиториев после коммитов — чисто.
- Initial baseline `git diff --check` обнаружил исторические trailing spaces в импортированном production-коде. Они не нормализовались, чтобы baseline оставался побайтно сопоставимым с production. Последующие изменения должны проходить `git diff --check` относительно baseline.

## Не выполнено намеренно

- Production, Reg.ru, DNS и Synology не изменялись.
- Deprecated Alpha-терминология не исправлялась в рамках baseline; она вынесена в отдельный будущий пакет.
- Remote на Synology не создавался: для root-level изменений NAS требуется отдельное явное разрешение.
