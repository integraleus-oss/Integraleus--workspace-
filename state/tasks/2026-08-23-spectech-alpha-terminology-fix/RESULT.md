# Результат

Исправлены все найденные устаревшие названия в каноническом monorepo:

- `Alpha.Trends` → `alpha.hmi.charts` с пояснением, что графики встроены в Alpha.HMI;
- `Alpha.Alarms 3.30` → `Alpha.HMI.Alarms 3.3`.

Обновлены:

- публичная страница `dpp-dobycha.html`;
- Markdown и Mermaid статьи миграции;
- DOCX-версия статьи;
- обе PNG-диаграммы.

Проверки:

- repo-wide text scan — устаревших названий нет;
- DOCX XML scan — устаревших названий нет;
- OCR двух диаграмм — показано `Alpha.HMI.Alarms 3.3`;
- визуальная проверка Mermaid PNG — пройдена;
- `git diff --check` — пройден.

Commit monorepo: `e40722b Replace deprecated Alpha alarms and trends names`.

Production не изменялся. Для публикации требуется отдельное подтверждение release.
