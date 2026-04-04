# AVEVA Operations Products — Глубокий конспект

> **Источники:** Официальные PDF (datasheets, Getting Started Guides, Installation Guide, презентации Product Manager), product pages aveva.com
> **Уровень достоверности:** 8-9/10 — всё подтверждено из первоисточников AVEVA
> **Дата изучения:** 2026-04-01

---

## 1. AVEVA System Platform

**Бывшее название:** Wonderware System Platform
**Текущая версия:** 2023 R2 P01 (June 2024)
**Документы-источники:**
- Product Datasheet (gulf.avevaselect.com, © 2022)
- Get Started Guide 2023 R2 (docs-be.aveva.com, 61 стр., © 2024)
- Installation Guide 2023 R2 P01 (docs-be.aveva.com, 421K символов)

### 1.1 Что это

Промышленная software-платформа, использующая технологию System Platform для:
- HMI (Human Machine Interface)
- Operations Management
- SCADA (Supervisory Control And Data Acquisition)
- Production and Performance Management

Содержит интегрированный набор сервисов и расширяемую модель данных. Поддерживает как supervisory control layer, так и MES layer, представляя их как единый источник информации.

### 1.2 Архитектура — функциональные компоненты

#### Galaxy — центральное понятие
- **Galaxy** = вся система целиком. Единое логическое пространство имён (Galaxy Namespace)
- **Galaxy Database** = реляционная БД (на SQL Server), содержит все persistent configuration: шаблоны, инстансы, security и т.д.
- **Galaxy Repository (GR)** = может содержать одну или несколько Galaxy Database. Создаётся при инсталляции на ноде с Bootstrap software

#### AVEVA Application Server
- Объектно-ориентированный framework-репозиторий для построения иерархии активов (asset hierarchy)
- Galaxy построена поверх SQL Server, управляет deployment и operation runtime-элементов

#### AVEVA Development Studio (IDE)
- ArchestrA IDE — единая среда разработки для supervisory SCADA и HMI
- Shared development environment — стандарты и best practices на уровне компании
- Multi-user: несколько инженеров одновременно (check-in/check-out механизм)
- Создание Galaxy, подключение к Galaxy, конфигурирование объектов

#### Visualization and Analysis Clients
- **InTouch HMI** — tag-based визуализация, native symbols + Industrial Graphics
- **AVEVA OMI (Operations Management Interface)** — responsive визуализация, context-aware, адаптивный контент по устройству пользователя, использует asset model hierarchy для навигации
- **AVEVA Insight** — AI-infused SaaS, self-service analytics

#### AVEVA Historian
- Process database, интегрированная с operations control
- Хранит process data от Communication Drivers и других источников
- Тесно связана с Microsoft SQL Server
- Block technology — в сотни раз быстрее обычных БД, занимает долю дискового пространства
- Поддерживает late-coming data, mismatched system clocks
- 1 год данных обрабатывается < 1 секунды
- Порт по умолчанию: **32565** (gRPC, с 2023 R2), legacy порт **32568** (WCF)
- Ad-hoc expressions в SQL запросах и Historian Client Web
- Репликация на AVEVA PI и AVEVA Data Hub
- HTTPS-based communications

#### Device Integration Tools
- Communication protocols: DDE, FastDDE, OPC, OPC UA, SuiteLink
- Gateway Communication Driver — инкапсулирует функциональность I/O Server
- Иерархия Communication Drivers соответствует иерархии реальных устройств
- **OPC UA Reverse Connect** — сервер инициирует подключение к клиенту (для firewall-friendly среды)
- **MQTT Publisher** — Sparkplug формат, dedicated publishing hierarchy
- **Buffered Data** — до 10K values/tag
- **SuiteLink Fallback** — по умолчанию secure (V3), unsecure (V2) отключен

#### AVEVA System Monitor
- Мониторинг критических показателей производительности AVEVA ПО и hardware

### 1.3 Разработка (Workflow)

**Workflow 1: Design Standards**
- Graphic standards: Industrial Graphics + Situational Awareness Library
- Object standards: Templates → Derived Templates → Instances
- Object Wizards: один шаблон + wizard заменяет множество derived templates
- Screen Profile standards: определяют физические характеристики мониторов
- Layout standards: определяют организацию panes на экране

**Workflow 2: Build a ViewApp**
- ViewApp = набор screen profiles + layouts + content
- ViewApp Editor — интеграционный инструмент
- Content: graphics, layouts, controls, app instances, external content
- Drag & drop размещение контента

**Workflow 3: Deploy a ViewApp**
- Deployment instantiates Galaxy objects в runtime
- Cascade deploy — иерархический порядок (host → child)
- Bootstrap software на каждом компьютере
- Объекты должны быть checked in и без ошибок
- Deployment view: Galaxy → WinPlatforms → AppEngines → Areas → DI Objects → Application Objects → Communication Drivers

**Workflow 4: Run a ViewApp**
- AVEVA OMI Application Manager на целевом компьютере
- Read/Write или Read-Only режим
- Множество ViewApps одновременно
- Preview mode для быстрого тестирования без redeploy

### 1.4 Ключевые возможности (из Datasheet)

- **Responsive visualization** — адаптируется под любой форм-фактор
- **До 80% снижение инженерных трудозатрат** (шаблоны, объекты, готовый контент)
- **До 40% повышение эффективности оператора**
- **Auto-build** — чтение структуры ПЛК → автоматическое создание шаблонов
- **Collaborative cloud development**
- **Historical playback** — воспроизведение исторических данных без скриптов
- **Unlimited IO, unlimited clients**
- **Node-to-node TLS encryption**
- **Hardware agnostic**

### 1.5 Коммуникации

- Протоколы: OPC-UA, MQTT, DNP3, Modbus, IEC 60870
- ПЛК: Schneider Electric, Allen-Bradley, GE, Siemens, Automation Direct, Bosch, Eaton, WAGO, Beckhoff, BACnet, Texas Instruments, Mitsubishi, Omron, Opto 22
- OPC UA scripting из Application Server и Industrial Graphics
- OPC UA Reverse Connect
- Security policies: Aes128_Sha256_RsaOaep, Aes256_Sha256_RsaPss
- OpenSSL 1.1.1n для MQTT, SuiteLink, OPC UA

### 1.6 Алармы (2023 R2)

- State-based alarming, suppression, shelving, grouping, aggregation
- **Alarm Latching** — acknowledged alarm, вернувшийся в норму, продолжает отображаться в LATCHED состоянии
- **Alarm Dismiss** — удаление LATCHED алармов из текущего режима
- Nuisance / "bad actor" фильтрация по severity

### 1.7 OMI Apps

| App | Назначение |
|---|---|
| Map OMI App | Географический контекст + навигация |
| AVEVA Insight OMI App | AI в контексте real-time решений |
| PLC Viewer OMI App | Troubleshooting PLC логики в реальном времени |
| 3D Viewer OMI App | 3D модели активов с алармами |
| Vision AI Assistant OMI App | Мониторинг видеопотоков + anomaly alerts |
| Graphic Repeater OMI App | Повтор символов для однотипных данных |

### 1.8 Новое в 2023 R2

- **OMI Web Client** — полностью новый, лучшая производительность, look & feel как desktop, WebViewEngine объект
- **SVG Import** — импорт SVG как Industrial Graphics
- **OPC UA Scripting** — вызов OPC UA серверов из скриптов
- **Alarm Latching / Dismiss**
- **Unified Identity** — SSO через AVEVA Connect, federated identity management
- **User Defined Types (UDTs)** — вложенность до 6 уровней, JSON import/export, intellisense
- **Credential Manager** — безопасное хранение учётных данных
- **AVEVA Operations Control** — подписочная модель (Edge, Supervisory, Enterprise)

### 1.9 Документация

| Документ | Описание |
|---|---|
| IDE.pdf | Конфигурирование и деплой Application Server и OMI приложений |
| IndustrialGraphics.pdf | Создание и управление Industrial Graphics |
| Scripting.pdf | Справочник по скриптовому языку Application Server |
| AlarmClientControl.pdf | Конфигурация alarm control |
| TrendClient.pdf | Конфигурация трендов |
| PlatformManager.pdf | Запуск/остановка системных компонентов |
| galaxymanagement.pdf | Backup и restore Galaxy database |
| HistorianConcepts.pdf | Обзор всей системы Historian |
| HistorianAdmin.pdf | Администрирование Historian |
| HistorianDatabase.pdf | Таблицы, views, stored procedures Historian |

---

## 2. AVEVA InTouch HMI

**Бывшее название:** Wonderware InTouch
**Текущая версия:** 2023 R2 P01 (Version 23.1.000)
**Документы-источники:**
- Datasheet (gulf.avevaselect.com, 16 стр., © 2021)
- Getting Started Guide (cdn.logic-control.com, 49K символов, © 2023)

### 2.1 Что это

HMI #1 в мире. Более 100 000 заводов и фабрик. 30+ лет истории без потери обратной совместимости.

### 2.2 Типы приложений

| Характеристика | Standalone | Managed |
|---|---|---|
| Основа | Tag-based, native symbols + Industrial Graphics | Object-based, Industrial Graphics |
| Создание | Application Manager | IDE |
| Редактирование | WindowMaker из Application Manager | WindowMaker из IDE |
| Application Objects | Нет | Да |
| Публикация | Да, из WindowMaker | Да, из IDE |

### 2.3 Архитектура Standalone

- **InTouch Application Manager** — создание и управление приложениями
- **WindowMaker** — среда разработки (design time)
- **WindowViewer** — среда исполнения (runtime)
- SQL Server больше НЕ требуется для Industrial Graphics (с 2020 R2)
- Копирование папки приложения между машинами для распространения

### 2.4 Архитектура Managed

- Интеграция с System Platform IDE
- **$InTouchViewApp** — базовый шаблон для managed приложений
- Galaxy Repository (GR) — центральный репозиторий
- Деплой с одной ноды на множество целевых нод с WindowViewer
- Публикация: published app отсоединяется от шаблона, но сохраняет связь с Galaxy через Industrial Graphics

### 2.5 InTouch Unlimited (с 2020 R2)

Новая коммерческая модель:
- **Безлимитные read-write клиенты** (web, mobile, RDS)
- **AVEVA Reports** для enterprise-wide reporting
- **Industrial strength Historian** с web reporting
- **Development tools**
- **IO communication drivers** включая OPC UA Server
- **Redundancy**
- **Native cloud support**
- **Built-in technical support & version updates**

### 2.6 Визуализация

**Situational Awareness Library:**
- Dashboard Symbols, Alarm Symbols, Trend Symbols, Equipment Symbols
- Input Symbols, Instrumentation Symbols, Status Symbols
- **Polar Star** — процессные значения на "спицах", изменение формы полигона при отклонении от уставок
- **Trend Pen** — Single/Multi-Pen тренды с фиксированным или скользящим окном
- **Triple-coded Alarm Annunciations** — Цвет + Форма + Текст для однозначной интерпретации

**Symbol Wizards:**
- Выбор конфигурационных опций (графика, скрипты, свойства) → автоматическая сборка composite symbol
- Один wizard заменяет множество отдельных символов

**Element Styles:**
- Стандартизированные цвета, индикаторы, текстовые форматы
- Element Styles Editor — централизованное управление
- One-click global update через centralized management

**Resolution Independence:**
- Дизайн в любом целевом разрешении
- Масштабирование без потери качества

### 2.7 Веб-доступ

- **InTouch Web Client** — HTML5, read/write, Industrial Graphics в браузере
- **InTouch Access Anywhere** — полный доступ к InTouch через HTML5, high fidelity, включая скрипты/.NET/ActiveX
- **Reverse Proxy** для безопасного доступа за пределами control network
- **Secure Gateway** для доступа за DMZ
- **Mobile App** (Android/iOS) — multi-touch, pan/zoom, writeback, alarm acknowledgement, language switching

### 2.8 Connectivity

- **Gateway Communication Driver** — OPC DA/UA setup, включён в InTouch
- **OPC UA Server** — InTouch может работать как OPC UA сервер
- **External providers** — drag & drop из OPC UA server list в Model-Tagname pane
- **OPC UA, OPC DA, SQL, SOAP, HTTP/S, .NET** — open connectivity
- **Encrypted communications** (если включено)

### 2.9 Cloud Integration

- **AVEVA Insight** — historian в облаке, Insight Publisher из Application Manager и WindowMaker
- **AVEVA Integration Studio** — cloud storage для Industrial Graphics, drag & drop в облако
- **AVEVA Connect** — federated identity management

### 2.10 Безопасность

- Microsoft Windows Authentication (domain controller / local)
- AVEVA Identity Manager (для non-Windows ОС)
- SSL & HTTPS для web communications
- Access-Level Password Security
- FDA 21CFR11 — Secured and Verified Writes
- Возможность запуска InTouch как Windows Service (Faceless)
- **Unified Identity** (2023 R2) — SSO через AVEVA Connect

### 2.11 Скриптинг

- **QuickScript** — встроенный скриптовый язык, сотни in-built функций
- **.NET scripting** + import custom script DLLs
- Auto-complete, line numbering, multi-level undo-redo, syntax checking, color coding
- InTouch Tag Server Client license — WindowViewer подключается к remote Tag Server

### 2.12 Прочее

- **HTML5 Web Widgets** — carousel widget (slideshow для Smart TV / wall monitors)
- **XML Import/Export** — CAD drawings в HMI
- **Application Templates** — стартовые шаблоны для новых проектов
- **Window Templates** — наследование свойств, контента, скриптов
- **Pan and Zoom** — multi-touch + keyboard/mouse
- **UDTs** (2023 R2) — User Defined Types, вложенность до 6 уровней
- **Мультиязычность** — EN, DE, FR, JA, ZH-CN + Language Assistant (Excel Add-in)

### 2.13 Технические требования (InTouch 2020 R2)

**Client OS (64-bit):**
- Windows 8.1 Pro/Enterprise
- Windows 10 (1803-1909) Pro/Enterprise/IoT Enterprise
- Windows 10 Enterprise LTSB 2016, LTSC 2019

**Server OS (64-bit):**
- Windows Server 2012 Data Center
- Windows Server 2012 R2 Standard/Data Center
- Windows Server 2016/2019 LTSC Standard/Datacenter

---

## 3. AVEVA Plant SCADA

**Бывшее название:** Citect SCADA (Schneider Electric), Vijeo Citect
**Текущая версия:** 2023 R2
**Документы-источники:**
- Datasheet (klinkmann.com, 7 стр., © 2022)
- Product page (aveva.com)

### 3.1 Что это

Высокопроизводительная промышленная SCADA для управления и мониторинга процессов в производстве, добывающей промышленности, коммунальных услугах и управлении зданиями.

### 3.2 Архитектура — 5 фундаментальных задач

Plant SCADA имеет **5 независимых задач**, каждая работает как отдельный client/server модуль:

1. **I/O (Communications)** — связь с I/O устройствами
2. **Alarm** — мониторинг условий тревог
3. **Report** — вывод отчётных данных
4. **Trend** — трендирование
5. **Display** — визуальное отображение

Каждая задача независима и выполняет собственную обработку. Пользователь контролирует, какие ноды выполняют какие задачи.

**Пример:** Одна нода выполняет display + trending, вторая — alarming + communications + reporting.

**Преимущества:** Redundancy (отказоустойчивость при сбое любой части системы без потери функциональности) + Performance (распределение нагрузки).

### 3.3 Развёртывание

- Client-Server с рождения
- **Clustering** — группировка серверов, автоматический failover, load balancing
- **Redundancy:** Primary & Secondary servers, client redundancy
- **Secure centralized deployment** — controlled transfer, delta-only deployment
- **Online changes** без остановки

### 3.4 Клиенты

1. **Desktop Client** — полнофункциональное desktop-приложение для panel/control room
2. **Web Client** — Industrial Graphics в браузере, read/write, для мобильных/casual пользователей
3. **Access Anywhere** — remote read/write через HTML5 браузер, полный доступ

### 3.5 Connectivity

- **150+ native protocol drivers**
- OPC UA, BACNET, IEC 61850, MODBUS, DNP3, IEC 60870
- **Нативная интеграция с Schneider Electric** — PLC (Modicon M340/M580, Quantum), PAC, power/energy meters, EcoStruxure Control Expert (Unity Pro)

### 3.6 Алармы

- **ISM (Instant visual alarm summary)** — фокус на abnormal situations
- Alarm indicators с severity
- До **8 причин, ответов и последствий** для каждого аларма
- Acknowledgment, cause, responses, filter/sorting, reason statements, alarm shelving
- Shapes + Colors + Numbers для conveying alarm status

### 3.7 Инжиниринг

- **Object-based overlay** на tag-based database
- **Equipment Editor** — объектно-ориентированная конфигурация
- **Cicode** — >1 000 built-in функций, специально для промышленных сред
- **Context-aware template** — layout template с emphasis on context
- **Broad graphics library** — vector-based symbols + animations, SA-graphics
- **Multi-language:** ZH, EN, FR, DE, IT, JA, KO, PT, RU, ES

### 3.8 Лицензирование (из форума Schneider Electric)

Шаги лицензирования:
- 75, 150, 500 → **1K**
- 1500 → **2.5K**
- 5K → **10K**
- 15K, 50K → **100K**
- **Unlimited**

USB-ключи обновляются через AVEVA License Website (при активной поддержке Customer FIRST).

### 3.9 Интеграция с портфолио AVEVA

- **AVEVA Historian** — process, alarm, event history data
- **AVEVA Insight** — AI-infused process analytics в облаке
- **AVEVA Teamwork** — skills development, knowledge sharing

---

## 4. AVEVA MES (Manufacturing Execution System)

**Бывшее название:** Wonderware MES
**Текущая версия:** MES 2023
**Документы-источники:**
- Product page (aveva.com)
- Презентация "What's new MES 2023" (Jeff Barkehanai, Product Manager, california.avevaselect.com, 20+ слайдов, © 2022)

### 4.1 Что это

Market-leading MES software для batch-oriented и flexible make-to-order production. Composable model-driven deployment. Hybrid cloud architecture.

### 4.2 Заявленные KPI

- **+15-20%** improvement to OEE
- **100%** first-time quality
- **+10-25%** plant capacity utilization

### 4.3 Архитектура (MESA Model)

AVEVA MES покрывает из MESA Functional Model:
- **Operations Management**
- **Performance Management**
- **Product Tracking & Genealogy**
- **Quality Management**
- **Process Management** (через AVEVA System Platform)
- **Data Collection / Acquisition** (через System Platform)

Связанные продукты:
- **Planet Together** — Operations/Detailed Scheduling
- **EQMS / Plant QMS** — Quality Management (расширенное)
- **AVEVA Enterprise Integration** — ERP integration (SAP, Amazon, Web)

### 4.4 Data Center Deployments (Multi-site)

Архитектура enterprise MES:
```
Corporate/BU/Regional Data Center(s)
├── AVEVA Enterprise Integration
├── AVEVA Manufacturing Execution System
├── AVEVA Work Tasks
│
Distributed Production Facilities (Site 1..N)
├── AVEVA Enterprise Integration
├── AVEVA Manufacturing Execution System
├── AVEVA Work Tasks
├── AVEVA System Platform
```

**Преимущества Data Center:**
- Экономия на оборудовании, IT-труде, деплое, обновлениях
- Лучшее использование IT-активов и доступность
- Снижение attack surface (security)
- Централизация данных → обмен best practices
- Упрощение enterprise integration
- Стандартизация отчётности и KPI benchmarking

**Ограничения:**
- Зависимость от WAN connectivity
- Рекомендуется валидация архитектуры командой AVEVA MES practice

### 4.5 Новое в MES 2023

**Multi Time Zone:** улучшенная обработка локального времени на мультисайтовых инсталляциях, shift change по timezone сайта

**High Availability:** MES Service слит с MES Middleware — устранена единая точка отказа. Любой Middleware может выполнять задачи MES Service, один назначается master

**MES Proxy:** поддержка второго MES Middleware для failover

**Web API:** расширения для Quality SPC Charts, Work Order, Job, Inventory management

**Security:** улучшенное шифрование паролей, client/server communication encryption

**Shift Patterns:** новый механизм (аналогичный Insight Performance) с effectivity dates, regular/holiday/overtime, comments

**Quality Management:** spec limits на SPC charts, новая опция Sample Plan Frequency

**UI Modernization:** обновление MES client и web portal под стандарты AVEVA UI

**Supervisor → MES Client Migration:**
- MES 2023 — последний релиз с Supervisor
- Data Log Configuration → Master Data Config
- Shift Patterns and Schedules заменяют Shift Exceptions
- Customer Configuration перенесена в MES Client
- Supply Chain Connector, Inventory, Storage Entity остаются в Supervisor

**Portfolio Compatibility:**
- Только System Platform 2023 (не ниже)
- Только Historian 2023
- BI Gateway 2021 SP1 (заменяет Intelligence 2017 U1)
- Новые лицензии для версии 7.x

### 4.6 Функциональные модули

- **Composable and modular deployment** — plug-and-play use case libraries
- **Low-code/no-code workflow** — моделирование UX и workflows
- **Real-time production control** — schedules, job execution, inventory
- **Performance management** — OEE KPIs, schedule adherence
- **Quality control** — SPC, sample plans, spec limits
- **Multi-site visualization and analytics** — cloud-based
- **Track and trace** — genealogy, traceability investigations
- **Paperless work management** — через AVEVA Work Tasks

### 4.7 Интеграция

- **AVEVA System Platform** — нативная интеграция
- **AVEVA Enterprise Integration** — ERP (SAP, Amazon, Web), автоматический data exchange, business continuity
- **AVEVA Work Tasks** — connected worker, digital transformation of work
- **AVEVA CONNECT** — multi-site cloud visualization

---

## 5. AVEVA Enterprise SCADA

**Бывшие названия:** Telvent OASyS SCADA → Schneider Electric ClearSCADA → AVEVA Geo SCADA Expert → AVEVA Enterprise SCADA
**Текущая версия:** 2023
**Документы-источники:**
- Product page (aveva.com)
- Datasheet PDF (не распарсился — защищённый)

### 5.1 Что это

Secure digital platform для регуляторного compliance, situational awareness, decision-making и visualization в масштабе enterprise. Основной фокус — pipeline operations (нефть, газ, жидкости).

### 5.2 Ключевые возможности

**Control Room Management (CRM):**
- Новое поколение performant, standards-based CRM graphic objects
- Соответствие **API 1165** и **ASM Consortium** display-building guidelines
- **PHMSA** (Pipeline and Hazardous Materials Safety Administration) compliance

**Security:**
- Built-in from the ground up
- Тяжёлое использование **Microsoft Active Directory**
- **Group Policy Objects (GPOs)** от Center for Internet Security (CIS) и Microsoft
- Принципы **least privilege** и **defense in depth**
- При deployment по reference architecture → полное соответствие **Purdue model**
- Multi-factor authentication
- Centralized log management
- Audit trail

**High Availability Redundancy:**
- Self-arbitrated measures для автоматического поддержания data и system integrity

**Enterprise Interface:**
- Secure interfaces к внешним enterprise системам
- Pipeline operators: flow nominations из внешних источников, сравнение с actual flows, alarm при расхождении

**Enterprise Integration:**
- Интеграция с pipeline operations и integrity operations software
- Нативная интеграция с **AVEVA PI System** и **CONNECT**
- Open interface для передачи данных в data stores, ERPs

**Regulatory Compliance:**
- Industry best practices для CRM programs
- Удовлетворение rigorous audits pipeline regulatory agencies

**Alarm Management:**
- Advanced alarm suppression, management, escalation
- Integrated reporting и analysis

### 5.3 Use Cases

**Leak Detection:**
- **AVEVA Pipeline Integrity Monitor** — computational pipeline monitoring (CPM)
- Компании выбирают CPM, наиболее подходящий для их конкретного pipeline

**Performance Intelligence:**
- Нативная интеграция с AVEVA PI System и AVEVA Insight
- Machine learning: от реактивных к проактивным операциям
- Historical time series data для regulatory compliance и corporate reporting

**Sustainability:**
- Digital warning system + leak detection
- Сравнение real-time data с runtime computational models
- Обнаружение и реагирование на аномалии в течение минут

### 5.4 Связанные продукты

- **AVEVA Pipeline Training Simulator** — тренажёр операторов трубопроводов
- **AVEVA Pipeline Operations for Liquids** — real-time control room operations
- **AVEVA Pipeline Operations for Gas** — setup, monitor, balance supply/demand
- **AVEVA PI System** — collect, aggregate, enrich real-time operations data
- **AVEVA Measurement Advisor** — точное измерение газовых и жидких потоков

### 5.5 Лицензирование

AVEVA Flex subscription program — credits-based system, pay-as-you-use.

---

## Сводная таблица

| Характеристика | System Platform | InTouch HMI | Plant SCADA | MES | Enterprise SCADA |
|---|---|---|---|---|---|
| **Уровень ISA-95** | 2-3 | 1-2 | 1-2 | 3 | 1-2 |
| **Масштаб** | Enterprise | Standalone/Site | Site/Multi-site | Enterprise | WAN/Regional |
| **Ядро** | ArchestrA / Galaxy | Tags + Industrial Graphics | 5 Tasks (I/O, Alarm, Report, Trend, Display) | Model-driven | CRM + Telemetry |
| **Среда разработки** | IDE (ArchestrA IDE) | WindowMaker + IDE | Plant SCADA Studio | MES Client + Web Portal | Proprietary |
| **Web-клиент** | OMI Web Client (новый) | Web Client + Access Anywhere | Web Client + Access Anywhere | Web Portal + Composable UI | HTML5 |
| **Историан** | Встроенный (Historian) | Встроенный (Historian) | Встроенный | Нет (через SP Historian) | Встроенный |
| **Скриптинг** | Application Server scripts + .NET | QuickScript + .NET | Cicode (1000+ функций) | Low-code/no-code workflows | Н/Д |
| **Протоколы** | OPC UA, MQTT, DNP3, Modbus, IEC 60870 | OPC UA/DA, SQL, SOAP, HTTP/S, .NET | 150+ drivers, OPC UA, BACNET, IEC 61850, Modbus, DNP3 | ISA-95 / B2MML, REST API | IEC 104, DNP3 (pipeline) |
| **Основная отрасль** | Любая (процессная) | Любая | Горнодобыча, металлургия, инфраструктура | CPG, фарма, химия | Нефтегаз, энергетика |
| **Облако** | Да (CONNECT, Insight) | Да (Insight, Integration Studio) | Да (Insight) | Да (Hybrid cloud) | Да (CONNECT, PI System) |
| **Безопасность** | TLS node-to-node, AD, Unified Identity | Windows Auth, AVEVA ID, FDA 21CFR11 | Role-based | Encrypted communications | AD, GPO, CIS, Purdue model |
| **Лицензирование** | Flex subscription | Unlimited / Flex | USB keys / Flex | Flex | Flex |

---

## Что НЕ удалось прочитать (пробелы)

1. **System Platform Installation Guide** — скачан (421K), но не полностью разобран (содержит детали системных требований, SQL Server конфигурации, network topology)
2. **Enterprise SCADA Datasheet PDF** — защищён, не распарсился
3. **MES Datasheet PDF** — защищён, не распарсился
4. **Plant SCADA Getting Started Guide** — не найден в открытом доступе (за логином)
5. **Enterprise SCADA administration/configuration guides** — за логином на docs.aveva.com
6. **Точные системные требования** по всем продуктам (кроме InTouch 2020 R2)

Для закрытия этих пробелов нужны:
- Доступ к docs.aveva.com (Customer FIRST аккаунт)
- Или PDF-файлы документации от пользователя
