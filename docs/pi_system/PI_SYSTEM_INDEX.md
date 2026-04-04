# PI System Knowledge Base Index

**Создано**: 1 апреля 2025  
**Версия**: 1.0  
**Статус**: Complete

## Обзор базы знаний

Данная база знаний содержит комплексную информацию по AVEVA PI System, основанную на официальных учебных материалах. Материалы охватывают все ключевые аспекты проектирования, развертывания и администрирования промышленной системы сбора и анализа данных.

### Структура базы знаний

```
pi_system/
├── PI_SYSTEM_INDEX.md           (этот файл)
├── raw/                         (исходные материалы)
│   ├── pi_arch.txt             (9450 строк) - Архитектура
│   ├── pi_assets.txt           (9111 строк) - Asset Framework  
│   ├── pi_admin.txt            (6330 строк) - Администрирование
│   ├── pi_events.txt           (1976 строк) - Event Frames
│   ├── pi_visualizing.txt      (7878 строк) - Визуализация данных
│   ├── pi_analyzing.txt        (5031 строк) - Анализ данных
│   ├── pi_datalink_lab.txt     (1118 строк) - PI DataLink Lab
│   ├── pi_af_easy_wins.txt     (2035 строк) - AF Easy Wins
│   └── pi_data_exploration.txt (1652 строк) - Data Exploration
└── [конспекты]                 (структурированные заметки)
    ├── pi_architecture_notes.md
    ├── pi_asset_framework_notes.md
    ├── pi_administration_notes.md
    ├── pi_events_notifications_notes.md
    ├── pi_visualization_notes.md      ← НОВЫЙ
    ├── pi_analyzing_notes.md          ← НОВЫЙ  
    └── pi_web_api_notes.md            ← НОВЫЙ
```

## Подробное содержание конспектов

### 1. [PI System Architecture](pi_architecture_notes.md)
**Источник**: PI System Architecture, Planning and Implementation Course Version 2025  
**Объем**: 248 страниц → 8KB конспект

#### Ключевые разделы:
- **Основы PI System** - компоненты, архитектура, временной синтаксис
- **Планирование** - высокая доступность, безопасность, gMSA, OIDC
- **Установка и настройка** - требования к оборудованию, sizing guidelines
- **PI Interfaces** - функции, параметры, архитектурные паттерны
- **PI Points** - типы данных, атрибуты, Future Data
- **Data Flow** - exception reporting, compression, архивы
- **PI Buffer Subsystem** - буферизация, N-way buffering
- **PI Connectors** - типы коннекторов, отличия от интерфейсов
- **Высокая доступность** - PI Collective, failover
- **Сетевые порты** - стандартные порты для всех компонентов

#### Практическая ценность:
- Таблицы sizing по количеству точек
- Конфигурационные параметры интерфейсов
- Рекомендации по архитектуре
- Диагностические инструменты

### 2. [Asset Framework](pi_asset_framework_notes.md)  
**Источник**: Building PI System Assets and Analytics with AF  
**Объем**: 294 страницы → 10KB конспект

#### Ключевые разделы:
- **Введение в AF** - asset-centric подход, компоненты, масштабируемость
- **Основные блоки** - Elements, Attributes, Data References, Templates
- **Стратегии проектирования** - географический, функциональный, гибридный подходы
- **Аналитика и расчеты** - Formula Data Reference, Value Retrieval Modes, PI Analysis Service
- **Event Frames** - концепция, шаблоны, генерация, потребление
- **Notifications** - архитектура, delivery channels, триггеры
- **Безопасность AF** - уровни безопасности, права доступа
- **Substitution Parameters** - параметризация шаблонов
- **Advanced Features** - Table Lookups, String Builder, UOM
- **PI Vision интеграция** - asset-based displays

#### Практическая ценность:
- Примеры формул и выражений
- Стратегии дизайна иерархий
- Конфигурация анализов
- Best practices по производительности

### 3. [PI System Administration](pi_administration_notes.md)
**Источник**: PI System Administration for IT Professionals Version 2017 R2  
**Объем**: ~250 страниц → 14KB конспект

#### Ключевые разделы:
- **Основы администрирования** - роль IT админа, архитектура для IT
- **Планирование инфраструктуры** - sizing guidelines, виртуализация
- **Сетевая архитектура** - зоны безопасности, firewall, аутентификация
- **Backup и DR** - стратегии резервного копирования, HA опции
- **Monitoring и Performance** - performance counters, инструменты мониторинга
- **Troubleshooting** - общие проблемы, диагностические инструменты
- **Security Hardening** - защита на уровне ОС, сети, PI System
- **Maintenance Tasks** - регулярные задачи, archive management
- **Integration** - AD интеграция, SIEM, change management
- **Automation** - PowerShell для PI System, скрипты автоматизации
- **Compliance** - требования регуляторов, подготовка к аудиту

#### Практическая ценность:
- Конкретные порты и firewall правила
- PowerShell скрипты для автоматизации
- Чек-листы для maintenance
- Процедуры troubleshooting

### 4. [Event Frames & Notifications](pi_events_notifications_notes.md)
**Источник**: Event Frames and Notifications Training Material  
**Объем**: ~100 страниц → 15KB конспект

#### Ключевые разделы:
- **Основы Event Frames** - концепция, типы событий, отличие от обычных данных
- **Event Frame Templates** - структура, атрибуты, referenced elements
- **Event Frame Generation** - автоматическое создание, триггеры, backfilling
- **Output Expressions** - функции EventStat и EventInfo
- **Consuming Event Frames** - PSE, PI DataLink, PI Vision
- **Notifications System** - архитектура, компоненты, триггеры
- **Delivery Channels** - Email, Web Service, тестирование
- **Message Content** - шаблоны, переменные, условный контент
- **Contact Management** - типы контактов, AD интеграция
- **Acknowledgment Workflow** - процесс подтверждения, эскалация
- **Best Practices** - дизайн, производительность, стратегия уведомлений

#### Практическая ценность:
- Примеры триггеров и выражений
- Шаблоны сообщений для notifications
- Workflow настройки Event Frames
- Интеграция с внешними системами

### 5. [PI Visualization](pi_visualization_notes.md) ⬅ НОВЫЙ
**Источники**: Visualizing PI System Data, PI DataLink Lab, Data Exploration  
**Объем**: ~200 страниц → 11KB конспект

#### Ключевые разделы:
- **PI Vision** - современная веб-визуализация, asset-centric displays
- **PI DataLink** - интеграция с Excel, функции PI DataLink
- **PI ProcessBook** - классические Windows HMI дисплеи
- **Advanced Excel** - PivotTables, dynamic arrays, Power BI integration
- **Performance optimization** - batch operations, caching strategies
- **Best practices** - дизайн, security, migration strategies

#### Практическая ценность:
- Примеры создания asset-based дисплеев
- Excel формулы для PI DataLink
- Оптимизация производительности визуализации
- Миграция ProcessBook → PI Vision

### 6. [PI Data Analysis](pi_analyzing_notes.md) ⬅ НОВЫЙ
**Источники**: Analyzing PI System Data, AF Easy Wins, Data Exploration  
**Объем**: ~300 страниц → 16KB конспект

#### Ключевые разделы:
- **PI Analysis Service** - серверная аналитика, Expression/Rollup analysis
- **Event Frame Analysis** - generation, templates, consumption
- **Business Intelligence** - PI Integrator for BA, Power BI integration
- **Predictive Analytics** - simple models, ML integration
- **Performance optimization** - expression variables, scheduling
- **Practical scenarios** - production optimization, condition monitoring

#### Практическая ценность:
- Asset Analytics best practices
- Event Frame configuration examples
- BI integration workflows
- Real-world analysis scenarios

### 7. [PI Web API](pi_web_api_notes.md) ⬅ НОВЫЙ
**Источники**: PI Web API documentation, AVEVA samples, практический опыт  
**Объем**: Комбинированный материал → 27KB конспект

#### Ключевые разделы:
- **RESTful Architecture** - HTTP методы, ресурсы, WebId система
- **Authentication & Security** - методы аутентификации, CORS, best practices
- **Core Resources** - PI Points, AF Elements/Attributes, Event Frames
- **Batch Operations** - multiple requests, performance optimization
- **Programming Examples** - JavaScript, Python, C# клиенты
- **Advanced scenarios** - streaming, caching, error handling
- **Integration patterns** - microservices, message queues
- **Troubleshooting** - common issues, performance testing

#### Практическая ценность:
- Production-ready код примеры
- Security implementation guidelines
- Performance optimization techniques
- Integration architecture patterns

## Ключевые технические параметры

### Sizing Guidelines (из архитектурного конспекта)
| Точки | Archive Size | Memory | Cores |
|-------|-------------|---------|--------|
| 0-87K | 256 MB | 8+ GB | 4 |
| 87-175K | 512 MB | 16+ GB | 8+ |
| 175-350K | 1024 MB | 24+ GB | 8+ |
| 350K+ | 2048+ MB | 32+ GB | 12+ |

### Стандартные порты (из админ. конспекта)
- **PI Data Archive**: 5450 (PI API), 5451 (Buffer)
- **PI AF Server**: 5457, 5458, 5459  
- **SQL Server**: 1433 (TCP), 1434 (UDP)
- **PI Vision**: 80 (HTTP), 443 (HTTPS)

### Рекомендуемые настройки точек
- **CompDev**: минимальное измеримое изменение прибора
- **ExcDev**: половина от CompDev  
- **CompMax**: 8 часов по умолчанию
- **ExcMax**: 10 минут по умолчанию

## Применение базы знаний

### Для системных архитекторов
1. **Планирование системы**: sizing guidelines, архитектурные паттерны
2. **Проектирование безопасности**: gMSA, сетевые зоны, аутентификация
3. **Высокая доступность**: PI Collective, failover стратегии

### Для администраторов
1. **Развертывание**: пошаговые инструкции установки и настройки
2. **Мониторинг**: performance counters, инструменты диагностики
3. **Maintenance**: регулярные задачи, backup стратегии
4. **Troubleshooting**: общие проблемы и их решение

### Для инженеров данных
1. **Моделирование активов**: стратегии дизайна AF иерархий
2. **Аналитика**: Formula Data Reference, PI Analysis Service
3. **Event Frames**: создание и потребление событийных данных
4. **Интеграция**: подключение к внешним системам

### Для разработчиков
1. **PI SDK/AF SDK**: программные интерфейсы
2. **PI Web API**: REST API для доступа к данным
3. **PowerShell Tools**: автоматизация административных задач
4. **Custom applications**: интеграционные решения

## Связанная документация

### Официальная документация AVEVA
- PI Server Installation and Upgrade Guide
- PI Data Archive System Management Guide  
- PI Asset Framework Client User Guide
- PI Vision Installation and Administration Guide

### Дополнительные ресурсы
- AVEVA Community Forums
- Knowledge Base (Tech Support)
- Training Materials (AVEVA Learning)
- Best Practices Guides

## История изменений

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.0 | 01.04.2025 | Первоначальное создание базы знаний |
| 1.1 | 01.04.2025 | Добавлены новые конспекты: Visualization, Data Analysis, PI Web API |

## Контакты и поддержка

Данная база знаний создана для внутреннего использования команды технических специалистов. 

При возникновении вопросов:
1. Проверьте соответствующий конспект
2. Обратитесь к исходным материалам в папке `raw/`
3. Консультируйтесь с официальной документацией AVEVA
4. Используйте ресурсы AVEVA Community

---

*База знаний актуальна на дату создания и требует периодического обновления при выходе новых версий PI System.*