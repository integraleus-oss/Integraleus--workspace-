# PS01 Full Alpha Platform Runtime Package

Цель: собрать не только Alpha.HMI, а максимально полный переносимый пакет PS01
по ТЗ v2.0 на актуальных компонентах Alpha Platform.

- [x] Создать task packet и output-папку.
- [x] Проверить локально доступные Alpha-модули, CLI, службы и примеры.
- [x] Скопировать/адаптировать проверенный Alpha.HMI кандидат.
- [x] Добавить реальные вкладки/формы: Обзор, Тренды, Архив, Аварии, Отчёты, Уставки.
- [x] Подготовить Alpha.Server/OPC UA/Modbus карту и скрипты проверки.
- [x] Подготовить Alpha.HMI.Alarms матрицу и журнал/квитирование как runtime contract или importable config, если формат найден.
- [x] Подготовить Alpha.Historian + alpha.hmi.charts конфигурацию и экран трендов.
- [x] Подготовить Alpha.Reports определения пяти отчётов.
- [x] Подготовить Alpha.Security роли и audit matrix.
- [x] Подготовить Alpha.Imitator сценарии стенда или указать блокер, если native import не найден.
- [x] Compile/export Alpha.HMI, Viewer screenshots, XML/CSV/JSON checks.
- [x] Упаковать ZIP, проверить `unzip -t`, посчитать SHA-256.
- [x] Отправить итог в Telegram с честным статусом модулей.
