# Альфа платформа vs AVEVA PI System — Детальное сравнение (v3)

> Дата: 2026-04-01
> Источники:
> - Альфа платформа: документация 6500+ стр., конспекты 50 модулей
> - AVEVA PI System: 10 учебных курсов (~45 000 строк), docs.aveva.com, GitHub AVEVA samples
> - Информация от специалистов Атомик Софт (уточнения по возможностям Альфы)

---

## 1. Позиционирование

| | Альфа платформа | AVEVA PI System |
|---|---|---|
| **Разработчик** | АО «Атомик Софт» (Россия, бренд Automiq) | AVEVA / Schneider Electric (Великобритания) |
| **Что это** | Полноценная SCADA-платформа: сбор + управление + визуализация + архив | Платформа данных: сбор + архив + контекстуализация + аналитика. НЕ SCADA |
| **Оператор может** | Управлять процессом (команды на ПЛК, квитирование, ввод уставок) | Только наблюдать (мониторинг, тренды, анализ) |
| **Реестр Минцифры** | ✅ №13866 | ❌ |
| **Санкционные риски** | Нет | Иностранное ПО, ограничения поставок |

> **Ключевое:** Это продукты разных классов. Альфа — SCADA, из которой оператор управляет процессом. PI System — инфраструктура данных, которая подключается к SCADA/DCS и делает данные доступными для аналитики. В крупных проектах PI System работает РЯДОМ со SCADA, а не вместо неё.

---

## 2. Архитектура

### Альфа платформа — монолит
```
ПЛК/Датчики → Alpha.Server (сбор + логика + команды)
                  ↓
              Alpha.Historian (архив)
              Alpha.HMI (мнемосхемы, управление)
              Alpha.HMI.Alarms (тревоги)
              Alpha.Reports (отчёты)
              Alpha.Security (безопасность)
```
Единый конфиг через Alpha.DevStudio, один инсталлятор, SVN/Git версионирование.

### AVEVA PI System — экосистема компонентов
```
SCADA/DCS/PLC → PI Interface / PI Connector / AVEVA Adapter
                     ↓
                PI Data Archive (хранение, порт 5450)
                     ↓
                PI Asset Framework (модель активов, SQL Server, порт 5457)
                     ↓
                PI Analysis Service (расчёты, порт 5459)
                PI Vision (веб-визуализация, порт 443)
                PI DataLink (Excel)
                PI Web API (REST, порт 443)
                PI Integrator (BI)
```
PI Server = PI Data Archive + PI Asset Framework. Каждый компонент — отдельный сервис.

| | Альфа | PI System |
|---|---|---|
| **Установка** | Один инсталлятор | 10+ компонентов, каждый отдельно |
| **Администрирование** | Alpha.DevStudio + CLI | PI SMT, PSE, PI Builder, PI ICU, Collective Manager — разные утилиты |
| **Кривая обучения** | Один продукт | Экосистема, каждый компонент со своей логикой |
| **Гибкость** | Монолит | Можно взять только нужные компоненты |
| **Версионирование** | ✅ SVN/Git в DevStudio | ❌ Нет встроенного |

---

## 3. Сбор данных

| Протокол | Альфа | PI System |
|---|---|---|
| **OPC DA** | ✅ клиент + сервер | ✅ PI Interface |
| **OPC UA** | ✅ клиент + сервер | ✅ PI Connector / AVEVA Adapter |
| **OPC HDA** | ✅ клиент + сервер | ✅ PI Interface |
| **OPC AE** | ✅ сервер | ✅ PI Interface |
| **Modbus TCP/RTU** | ✅ встроенный master+slave | ✅ PI Interface / AVEVA Adapter |
| **IEC 60870-5-104** | ✅ клиент + сервер | ✅ PI Interface |
| **IEC 60870-5-101** | ✅ клиент + сервер | ✅ PI Interface |
| **IEC 61850** | ✅ клиент | ⚠️ Через OPC-шлюз |
| **S7 (Siemens)** | ✅ встроенный | ✅ PI Interface |
| **EtherNet/IP** | ✅ встроенный (ControlLogix) | ✅ PI Interface |
| **FINS (Omron)** | ✅ встроенный | ✅ PI Interface |
| **SNMP** | ✅ встроенный | ⚠️ Через сторонние |
| **MQTT** | ✅ встроенный | ✅ AVEVA Adapter |
| **BACnet** | ✅ клиент | ⚠️ Через PI Interface |
| **UNET (TREI)** | ✅ встроенный | ❌ |
| **DTS (ППД)** | ✅ (Linux only) | ❌ |
| **TCP Server** | ✅ встроенный | ⚠️ Через PI Interface |
| **Общее кол-во** | 20+ встроенных в ядро | 450+ отдельных интерфейсов |
| **Подход** | Драйверы в ядре Alpha.Server | Каждый интерфейс — отдельный компонент |

### Три поколения сборщиков PI System
1. **PI Interface** — 450+ протоколов, exception reporting, ручное создание точек, failover через UniInt
2. **PI Connector (1st/2nd Gen)** — автоматическое создание точек и AF-структуры. 2nd Gen НЕ поддерживает failover
3. **AVEVA Adapter** — кроссплатформенный (Windows/Linux/Docker), OMF-протокол, отправка в PI Web API или CONNECT

### Буферизация
| | Альфа | PI System |
|---|---|---|
| **При потере связи** | ✅ Буферизация в Alpha.Server | ✅ PI Buffer Subsystem (PIBufSS, порт 5451) |
| **N-Way Buffering** | ❌ | ✅ На все серверы коллектива |
| **Disconnected Startup** | ✅ Автономная работа | ✅ Интерфейс стартует без DA |

---

## 4. Хранение данных (Historian)

| | Alpha.Historian 4.0 | PI Data Archive |
|---|---|---|
| **Масштаб** | Миллионы тегов (в редакции Platform) | Миллионы тегов |
| **Фильтрация данных** | ✅ Уровень 1: по отклонению значения/времени. Swinging door (уровень 2) пока нет | ✅ Двухуровневая: Exception (фильтрация шума) + Swinging Door (фильтрация избыточных точек) |
| **Сжатие хранения** | LZMA (формат 3x, коэфф. 0.2–0.5), журнал транзакций (формат 4x) | Проприетарный формат .arc |
| **Скорость записи** | Высокая | Сотни тысяч значений/сек |
| **Скорость чтения** | Высокая | Миллионы значений/сек |
| **Future data** | Не описано | ✅ Отдельные future-архивы (1 мес.) |
| **ОС** | ✅ Windows + Linux | ❌ Только Windows Server |
| **SQL-доступ** | ✅ Alpha.RMap | ✅ PI SQL Framework (OLEDB/ODBC/JDBC) |

### Sizing PI Data Archive
- 11 МБ на 1000 точек (DA) + 10 МБ на 1000 точек (архивы) + 5 МБ на 1000 точек (Event Queue)
- Архив для 100k точек ≈ 1 ГБ
- Рекомендация: SSD, RAID 10, отдельные диски для архивов и Event Queue

---

## 5. Модель активов

| | Альфа | PI System |
|---|---|---|
| **Модель** | Дерево сигналов + пользовательские типы (ООП) в Alpha.HMI | PI Asset Framework — семантическая модель предприятия |
| **Масштаб** | Зависит от проекта | До 100+ миллионов атрибутов |
| **Шаблоны** | ✅ Типы объектов в HMI (аналог классов ООП): тип → экземпляры, наследование, параметры инициализации, визуальные + невизуальные типы | ✅ AF Templates: шаблоны активов с наследованием, Substitution Parameters, автообновление всех экземпляров |
| **Область шаблонизации** | На уровне HMI (визуализация + поведение) | На уровне данных (модель активов + расчёты + события) |
| **Множественные иерархии** | Одно дерево | ✅ Несколько иерархий (по географии, процессу, оборудованию) |
| **Rollup** | ❌ | ✅ Sum/Avg/Min/Max/Count по дочерним элементам |
| **Кросс-сервер** | ❌ | ✅ Один AF-элемент ссылается на данные из разных PI Data Archive |
| **Внешние данные** | ✅ SQLConnector (в сигналы) + подключение DLL/SO | ✅ Table Lookup (из SQL прямо в атрибуты AF) |
| **Единицы измерения** | ✅ | ✅ UOM с автоматической конвертацией |
| **Хранилище модели** | Конфигурация проекта (DevStudio) | Microsoft SQL Server |

---

## 6. Аналитика и вычисления

| | Альфа | PI System |
|---|---|---|
| **Язык** | Alpha.Om 1.4 (формулы + процедуры) | Expression Editor + встроенные функции |
| **Потоковые вычисления** | ✅ Формулы на сигналах | ✅ PI Analysis Service (streaming) |
| **Шаблонизация расчётов** | ❌ | ✅ Один расчёт в шаблоне → ко всем экземплярам |
| **Backfill** | ❌ | ✅ Пересчёт по историческим данным |
| **Rollup** | ❌ | ✅ Агрегация по дочерним элементам |
| **Expression Variables** | ✅ Переменные в Om | ✅ Переменные для оптимизации (vTempAvg = TagAvg(...)) |
| **Event Frame Generation** | ❌ | ✅ Автосоздание событий по условиям |
| **Скриптинг в HMI** | ✅ Alpha.Om + JavaScript + вызов DLL/SO | ❌ В PI Vision нет скриптинга |
| **OEE и KPI** | На прикладном уровне | ✅ Встроенные паттерны (Availability × Performance × Quality) |

### Ключевые функции PI Analysis
```
TagAvg(), TagMax(), TagMin(), TagTot() — статистика за период
TagVal() — значение в момент времени
FindEq(), FindGT() — поиск значений
NoOutput() — подавление вывода
If/Then/Else — условия
Substitution: '|Element|.Temperature' — относительные ссылки
```

---

## 7. Event Frames — уникальная фича PI System

| | Альфа | PI System |
|---|---|---|
| **Фиксация событий** | Журнал тревог (Alarms) | ✅ Event Frames — именованные периоды |
| **Шаблоны событий** | ❌ | ✅ EF Templates с атрибутами |
| **Вложенность** | ❌ | ✅ Смена → Партия → Фаза |
| **Сравнение** | ❌ | ✅ Compare Events (best batch vs worst) |
| **Output Expressions** | ❌ | ✅ Расчёты внутри EF |
| **Генерация по условию** | Тревоги по уставкам | ✅ Condition-based + Periodic |
| **Просмотр в Excel** | ❌ | ✅ PICompareEvents, PIExploreEvents в DataLink |

---

## 8. Визуализация

| | Альфа | PI System |
|---|---|---|
| **Desktop HMI** | ✅ Alpha.HMI (Дизайнер + Визуализатор) — мнемосхемы с управлением | ⚠️ PI ProcessBook (legacy, deprecated) |
| **Веб** | ✅ Alpha.HMI.WebViewer | ✅ PI Vision (HTML5, responsive) |
| **Управление процессом** | ✅ Кнопки, ввод, команды на ПЛК | ❌ Только мониторинг |
| **Скриптинг** | ✅ Alpha.Om + JavaScript | ❌ |
| **Виджеты PI Vision** | — | Value, Trend, Table, Gauge, Bar Chart, XY Plot, Pareto, Multi-state, Asset Navigation |
| **Asset-centric дисплеи** | По дереву сигналов | ✅ Element Relative Displays — один дисплей для всех однотипных активов |
| **Collections** | ❌ | ✅ Группировка активов с фильтрацией по шаблону/категории |
| **Графики** | ✅ alpha.hmi.charts (оперативные + исторические) | ✅ Trends с zoom/pan, cursors, multiple scales, annotations |
| **Анимация** | ✅ Мигание, цвет, видимость | ✅ Multi-state symbols (цвет, мигание по условию) |
| **Мобильный** | ⚠️ Через WebViewer | ✅ PI Vision адаптирован для мобильных |
| **Excel** | ⚠️ Экспорт XLSX из Alarms/Reports | ✅ PI DataLink — 6 групп функций: Single-value, Multiple-value, Calculation, Events, Search, Properties |

### Функции PI DataLink в Excel
```excel
=PICurrentVal("tag")                              — текущее значение
=PIArcVal("tag", "*-1h")                          — архивное значение
=PISampDat("tag", "*-8h", "*", "1h")              — выборка с интервалом
=PICompDat("tag", "*-8h", "*")                    — сжатые данные
=PICalcDat("tag", "*-1d", "*", "average")         — среднее за период
=PICompareEvents(db, start, end, elem, template)  — сравнение событий
```
Поддержка Dynamic Arrays (Office 365): SORT, FILTER, UNIQUE, XLOOKUP.

---

## 9. Тревоги и уведомления

| | Alpha.HMI.Alarms 3.3 | PI System |
|---|---|---|
| **Тревоги реального времени** | ✅ Промышленный класс (ISA 18.2) | ⚠️ Multi-state символы (визуальные) |
| **Квитирование** | ✅ | ✅ Acknowledgement с эскалацией |
| **Подавление (shelving)** | ✅ | ❌ |
| **Группы важности** | ✅ (1-1000, три категории) | ⚠️ Через приоритеты |
| **Журнал** | ✅ Оперативный + исторический | ✅ Event Frames |
| **Эскалация** | ❌ | ✅ Автоэскалация при отсутствии подтверждения |
| **Каналы доставки** | ✅ Email (SMTP/SSL), Syslog (UDP/TCP), OPC — через Alpha.Diagnostics + модуль рассылки событий | ✅ Email (SMTP), Web Service (HTTP POST) |
| **Экспорт** | ✅ CSV, PDF, XLSX | ⚠️ Через DataLink/API |
| **Кроссплатформенность** | ✅ Windows, Linux, веб | ❌ Notification Service только Windows |

---

## 10. Высокая доступность (HA)

| | Альфа | PI System |
|---|---|---|
| **Резервирование серверов** | ✅ **Дублирование** (оба работают одновременно, клиент выбирает сам) + **Горячее резервирование** (основной + резервный в ожидании, автопереключение). Единый конфиг на оба | ✅ PI Collective (репликация Data Archive) |
| **Резервирование АРМов** | ✅ Дублирование: несколько АРМов с одинаковыми данными | ✅ Несколько PI Vision серверов |
| **Резервирование истории** | ✅ Несколько БД Historian | ✅ Репликация Data Archive в Collective |
| **N-Way Buffering** | ❌ | ✅ Буферизация на все серверы коллектива |
| **Failover интерфейсов** | ✅ | ✅ UniInt-based автоматический failover |
| **Disconnected Startup** | ✅ | ✅ |
| **HA для AF/SQL** | — | ✅ SQL Server Always On / Mirroring |
| **Управление кластером** | ✅ Через Alpha.DevStudio (встроено в IDE) | ✅ PI Collective Manager (отдельная GUI-утилита) |
| **Редакции с HA** | SCADA, Platform (в One+ нет) | Все |

---

## 11. API и интеграция

| | Альфа | PI System |
|---|---|---|
| **REST API** | ❌ | ✅ PI Web API (RESTful, JSON, Swagger, Batch Operations) |
| **SDK (C/C++)** | ✅ Нативный API | ❌ (PI API — legacy) |
| **SDK (Python)** | ✅ | ⚠️ Через PI Web API |
| **SDK (.NET)** | ✅ | ✅ PI AF SDK |
| **SQL-доступ** | ✅ Alpha.RMap | ✅ PI SQL Framework (OLEDB/ODBC/JDBC) |
| **OPC UA сервер** | ✅ Встроенный | ✅ |
| **Excel add-in** | ❌ | ✅ PI Builder (массовые операции с точками/AF) + PI DataLink (данные) |
| **BI-интеграция** | ❌ | ✅ PI Integrator (Power BI, Tableau, Qlik, Spotfire) |
| **OMF** | ❌ | ✅ Open Message Format |
| **GitHub Samples** | ❌ | ✅ Примеры на Angular, jQuery, Python, R, C# |

### PI Web API — ключевые возможности
```
GET  /points/{webId}/value           — получение значения
POST /points/{webId}/value           — запись значения
GET  /points/{webId}/interpolated    — интерполированные данные
GET  /assetdatabases                 — список баз AF
GET  /elements/{webId}/attributes    — атрибуты элемента
POST /batch                          — пакетные операции (6+ вызовов в 1 запросе)
```
Аутентификация: Anonymous, Basic, Windows, Kerberos, Certificate.

---

## 12. Отчётность и BI

| | Альфа | PI System |
|---|---|---|
| **Встроенные отчёты** | ✅ Alpha.Reports 1.1 (конструктор + сервер + планировщик) | ❌ |
| **Excel** | ⚠️ Экспорт XLSX | ✅ PI DataLink (6 групп функций, Dynamic Arrays, PivotTables) |
| **BI** | ❌ | ✅ PI Integrator for BA → Power BI, Tableau, Qlik, Spotfire |
| **Predictive Analytics** | ❌ | ✅ Интеграция с ML-платформами через PI Integrator / PI Web API |
| **Массовое управление** | ✅ Alpha.DevStudio | ✅ PI Builder (Excel add-in для массовых операций) |

---

## 13. Безопасность

| | Альфа | PI System |
|---|---|---|
| **LDAP/AD** | ✅ Alpha.Security | ✅ Windows Integrated Security (Mappings) |
| **SSO** | ⚠️ Через LDAP | ✅ OpenID Connect (с PI Server 2024) |
| **gMSA** | ❌ | ✅ Group Managed Service Accounts |
| **Безопасность по объектам** | ✅ | ✅ По элементам AF, категориям, шаблонам (Read/ReadWrite/Admin) |
| **Сетевые паттерны** | Зависит от проекта | 5 документированных паттернов (PI в DMZ, HA в DMZ, Absolute Enforcement и др.) |
| **Аудит** | ✅ | ✅ |

---

## 14. Платформы и Edge

| | Альфа | PI System |
|---|---|---|
| **Windows** | ✅ | ✅ (основная) |
| **Linux** | ✅ (Astra, РЕД ОС, Альт, Ubuntu) | ⚠️ Только AVEVA Adapters и Edge Data Store |
| **Edge** | ✅ Alpha.Server на АБАК, Raspberry Pi — полноценный edge | ✅ Edge Data Store (лёгкий агент) |
| **Docker** | ⚠️ Тестируется | ✅ AVEVA Adapters |
| **Облако** | ⚠️ Тестируется | ✅ AVEVA CONNECT (SaaS) |
| **Виртуализация** | ✅ | ✅ VMware, Hyper-V |

---

## 15. Лицензирование

| | Альфа | PI System |
|---|---|---|
| **Модель** | Бессрочная лицензия + годовая поддержка | Подписка (AVEVA Flex Credits) |
| **Единица** | Количество тегов | Количество тегов |
| **Редакции** | One+ (до 50k, USB HASP), SCADA (USB HASP), Platform (программные ключи, самогенерация) | PI Data Infrastructure (единая подписка) |
| **Пул тегов** | ✅ В Platform — надстройка для свободного распределения | ✅ Aggregate Tag |
| **Стоимость** | Существенно ниже | Enterprise-ценник |

---

## 16. Администрирование

| | Альфа | PI System |
|---|---|---|
| **IDE** | Alpha.DevStudio 4.1 | PI SMT + PSE + PI ICU + PI Builder |
| **CLI** | ✅ alpha.historian.cli, DevStudio CLI | ✅ piconfig, piartool |
| **Версионирование** | ✅ SVN/Git в DevStudio | ❌ Нет встроенного |
| **Мониторинг** | ✅ Alpha.Diagnostics, Alpha.Link | ✅ PI SMT Network Manager, Performance Counters |
| **Горячее применение** | ✅ Historian config_reload | ⚠️ Зависит от компонента |

---

## 17. Сетевые порты PI System

| Компонент | Порт |
|---|---|
| PI Data Archive (PI API) | 5450 TCP |
| PI Buffer Subsystem | 5451 TCP |
| PI Update Manager | 5452 TCP |
| PI AF Server | 5457 TCP |
| PI Notifications | 5458 TCP |
| PI Analysis Service | 5459 TCP |
| SQL Server | 1433 TCP, 1434 UDP |
| PI Vision / PI Web API | 80/443 |

---

## 18. Итоговые плюсы и минусы

### Альфа платформа — плюсы
1. ✅ **Российский продукт** — реестр Минцифры, нет санкционных рисков
2. ✅ **Полноценная SCADA** — оператор управляет процессом
3. ✅ **Linux** — Astra, РЕД ОС, Альт, Ubuntu (критично для КИИ)
4. ✅ **Цена** — значительно дешевле PI System
5. ✅ **Бессрочная лицензия** — нет подписки
6. ✅ **Простота** — один продукт vs экосистема 10+ компонентов
7. ✅ **Встроенные драйверы** — 20+ протоколов в ядре, нет зоопарка интерфейсов
8. ✅ **Alarm-система** — промышленный класс (ISA 18.2), подавление, квитирование
9. ✅ **Встроенные отчёты** — Alpha.Reports
10. ✅ **Масштаб** — миллионы тегов в Alpha.Platform
11. ✅ **Edge** — Alpha.Server на АБАК/Raspberry Pi без отдельного продукта
12. ✅ **API** — C/C++, Python, .NET, OPC UA, SQL
13. ✅ **Версионирование** — SVN/Git в DevStudio
14. ✅ **Platform** — самогенерация ключей, свободное распределение тегов
15. ✅ **ООП-модель** — типы объектов с наследованием и параметрами инициализации в HMI
16. ✅ **HA** — дублирование + горячее резервирование серверов, АРМов, истории
17. ✅ **Оповещения** — Email (SMTP/SSL), Syslog (UDP/TCP), OPC

### Альфа платформа — минусы (относительно PI System)
1. ❌ **Нет модели активов** уровня PI AF — нет семантических иерархий с rollup и кросс-сервер ссылками
2. ❌ **Нет REST API** — при наличии C/C++, Python, .NET, OPC UA, SQL
3. ❌ **Нет Excel-надстройки** уровня PI DataLink (6 групп функций, Dynamic Arrays, PivotTables)
4. ❌ **Нет BI-интеграции** уровня PI Integrator (Power BI, Tableau, Qlik)
5. ❌ **Нет Event Frames** — нет сравнения событий, ретроспективного анализа партий
6. ❌ **Нет шаблонизации расчётов** — backfill, rollup, Substitution Parameters в формулах
7. ❌ **Нет Swinging Door** фильтрации (пока)
8. ❌ **Меньше протоколов** — 20+ встроенных vs 450+ у PI
9. ❌ **Меньше экосистема** — нет сообщества уровня PI Square, GitHub Samples

### AVEVA PI System — плюсы
1. ✅ **Asset Framework** — семантическая модель до 100M атрибутов, шаблоны, rollup, кросс-сервер
2. ✅ **Двухуровневая фильтрация** — Exception + Swinging Door
3. ✅ **Event Frames** — ретроспективный анализ, сравнение партий, вложенность
4. ✅ **Аналитика** — шаблонизация расчётов, backfill, rollup, OEE-паттерны
5. ✅ **PI Web API** — REST, JSON, Swagger, Batch Operations, примеры на 5 языках
6. ✅ **PI DataLink** — мощная Excel-интеграция (6 групп функций, Dynamic Arrays)
7. ✅ **450+ протоколов**
8. ✅ **Edge-to-Cloud** — от датчика до AVEVA CONNECT
9. ✅ **BI-интеграция** — PI Integrator → Power BI, Tableau, Qlik, Spotfire
10. ✅ **HA** — PI Collective, N-Way Buffering, документированные паттерны
11. ✅ **Экосистема** — PI Square, обучение, 40+ лет, GitHub Samples

### AVEVA PI System — минусы
1. ❌ **НЕ SCADA** — нет управления процессом
2. ❌ **Только Windows** — серверная часть
3. ❌ **Цена** — enterprise-ценник + подписка
4. ❌ **Санкции** — недоступен для российских предприятий
5. ❌ **Нет в реестре Минцифры**
6. ❌ **Сложность** — 10+ компонентов, каждый со своим lifecycle
7. ❌ **Нет alarm-системы** — нужна отдельная SCADA
8. ❌ **Нет версионирования** конфигурации из коробки
9. ❌ **Зависимость от SQL Server** — AF требует MS SQL
10. ❌ **Диапазон времени** — до января 2038 (Year 2038 problem)
11. ❌ **PI ProcessBook deprecated** — классический HMI больше не развивается

---

## 19. Когда что выбирать

### Выбирай Альфу, если:
- Нужна SCADA для управления процессом (оператор + мнемосхемы + команды)
- Российское предприятие, импортозамещение, КИИ
- Linux обязателен
- Бюджет ограничен
- Нужна простота (один продукт, одна IDE)
- Нужна alarm-система промышленного класса

### Выбирай PI System, если:
- Нужен enterprise-историан для аналитики (не для управления)
- Нужна модель активов и цифровые двойники
- Нужна интеграция с BI/ML
- Нужен ретроспективный анализ событий (Event Frames)
- Мультисайтовая инфраструктура с облаком
- Нет ограничений по импортозамещению

### Они работают вместе:
В крупных проектах PI System подключается к Альфе через OPC UA/DA и забирает данные для аналитики. Альфа управляет процессом, PI System делает данные доступными для инженеров, аналитиков и руководства. Это разные слои одной архитектуры.
