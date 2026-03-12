# Alpha.Historian 4.0 — Конспект

**Продукт:** Сервер истории значений сигналов и событий
**Разработчик:** АО «Атомик Софт» (Automiq)
**ОС:** Windows 10/11, Server 2012-2022, Linux (Astra, РЕД ОС, Альт, Ubuntu)

## Назначение
Долговременное хранение исторических данных: значения сигналов + события.

## Архитектура
- Сервер истории (служба/сервис) + базы данных
- Получение данных от Alpha.Server через модуль истории
- Предоставление данных клиентам через Alpha.Server/AccessPoint (HMI, Trends, Alarms, OPC UA/HDA, PostgreSQL)

## Форматы БД
### 4x (новый)
- Журнал транзакций, фрагменты, слияние данных
- Запись с любой меткой времени
- Компактное хранение, быстрый запуск
- Конфиг: db.jsonc + local.jsonc (кэш, I/O, запись, лимиты, очистка, журнал)

### 3x (старый)
- Активная/архивная области
- Фрагменты по суткам
- Сжатие LZMA (коэффициент 0.2-0.5)

## Установка
- Windows: MSI, служба Alpha.Historian.Server
- Linux: deb/rpm, сервис alpha.historian.server через systemctl
- Путь Linux: /opt/Automiq/Alpha.Historian
- Домашняя папка: C:/Alpha.Historian/server_home (Win) или /var/lib/Alpha.Historian/server_home (Linux)

## Оценка объёма
- 4x: DatabaseSize = StorageDepth × ΣSource.VolumePerDay
- Формулы расчёта по типам: bool, int, float, double, string
- 3x: ArchiveSize + ActiveSize с учётом сжатия

## Конфигурация
- server.jsonc — API, мониторинг, DCOM, Alpha.Net
- local.jsonc — потоки, async-запросы, JSON API
- db.jsonc — формат, location
- Горячее применение настроек

## CLI
- `alpha.historian.cli stat` — статистика
- `alpha.historian.cli config_status` — статус конфигурации
- `alpha.historian.cli config_reload` — горячая перезагрузка
- Поддержка удалённых целей: --target

## Мониторинг
- Через Alpha.Link: дерево сигналов (Instance, Db, Config, Policy, Api, AsyncQuery, JsonApi, Engine, License)
- Метрики: объём памяти пула, нагрузка на диск, состояние БД, скорость записи/чтения

---
*Источник: Alpha.Historian 4.0 Руководство администратора*
*Обработано: 2026-03-11*
