# Reconciliation `specialtechnology.ru`

Дата проверки: 2026-08-23.

## Результат

Исходный `git status` содержал 48 записей:

- 47 изменённых tracked-файлов;
- 1 новый файл `cross-site-analytics.js`.

Сравнение выполнено с текущим публичным production `https://specialtechnology.ru/`:

- 46 файлов, доступных по своим URL, побайтно совпадают с локальными версиями;
- `index.html` побайтно совпадает с публичной главной `/` (сам `/index.html` штатно отдаёт 301);
- `.htaccess` нельзя скачать публично, но обе локальные директивы подтверждены поведением production:
  - `/index.html` → `/` (`301`);
  - `/calculator.html?check=...` → `/calculator.html` (`301`).

Вывод: все 48 записей являются уже опубликованным production-состоянием, которое не было зафиксировано в Git. Локальных неопубликованных файлов в этом наборе не обнаружено.

## Классификация

- Уже live и должны быть закоммичены: 48/48.
- Только локальные полезные изменения: 0.
- Generated/noise: 0.
- Требуют решения перед фиксацией: 0.

## Отдельные контентные долги

Проверка Alpha guardrail обнаружила устаревшие названия в существующем live-контенте:

- `dpp-dobycha.html` — `Alpha.Trends`;
- исходные Markdown/Mermaid материалы статьи миграции — `Alpha.Alarms 3.30`.

Это не причина менять reconciliation-baseline: baseline должен точно фиксировать production. Исправление терминологии оформляется отдельным локальным diff → preview → approval → deploy пакетом.

## Evidence

- `hash-classification.tsv` — SHA-256 HEAD/local/live.
- `http-status.tsv` — HTTP-статусы snapshot-загрузки.
- `production-snapshot/` — публичные копии изменённых файлов на момент проверки.

Production во время reconciliation не изменялся.
