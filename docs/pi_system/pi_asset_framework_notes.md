# Конспект: Building PI System Assets and Analytics with AF

**Источник**: Building PI System Assets and Analytics with AF (PI Server 2018 SP3 Patch 3)  
**Дата создания**: 1 апреля 2025  
**Количество страниц**: 294

## 1. Введение в Asset Framework

### 1.1 Что такое PI Asset Framework (AF)
- **Назначение**: организация данных PI System по активам и процессам предприятия
- **Принцип**: asset-centric подход вместо tag-centric
- **Основа**: Microsoft SQL Server для хранения метаданных
- **Масштабируемость**: до 100+ миллионов атрибутов элементов

### 1.2 Основные компоненты
- **PI AF Server**: сервер базы данных активов
- **AF Database**: база данных с метаданными активов
- **PI System Explorer (PSE)**: основной клиент для работы с AF
- **PI Builder**: Excel add-in для массовых операций
- **AF SDK**: программный интерфейс для разработчиков

### 1.3 Архитектурные возможности
- **Единая база данных AF**: рекомендуется для всего предприятия
- **Множественные базы**: для разных подразделений или тестирования
- **Кросс-сервер элементы**: ссылки на данные из разных PI серверов
- **Безопасность на уровне объектов**: гранулярный доступ

## 2. Основные строительные блоки

### 2.1 Elements (Элементы)
- **Определение**: представление физических или логических активов
- **Примеры**: насосы, компрессоры, цеха, заводы, сети
- **Иерархия**: древовидная структура parent-child
- **Гибкость**: можно перестраивать без потери данных

### 2.2 Attributes (Атрибуты)
- **Типы данных**:
  - **PI Point**: ссылка на временной ряд в PI Data Archive
  - **Static**: статические значения (числа, строки, даты)
  - **Formula**: формулы для расчетов
  - **Table Lookup**: ссылки на внешние таблицы
  - **String Builder**: составные строки

### 2.3 Data References
- **PI Point Data Reference**: прямая ссылка на PI Point
- **Formula Data Reference**: математические и логические выражения
- **Table Lookup**: поиск в таблицах
- **Analysis**: результаты расчетов PI Analysis Service

### 2.4 Element Templates
- **Назначение**: шаблоны для массового создания элементов
- **Компоненты**: атрибуты, категории, связи
- **Наследование**: автоматическое обновление при изменении шаблона
- **Substitution Parameters**: подстановочные параметры для настройки

## 3. Стратегии проектирования иерархий

### 3.1 Подходы к организации
**Географический подход**:
```
Компания → Регион → Завод → Цех → Линия → Оборудование
```

**Функциональный подход**:
```
Компания → Процесс → Система → Подсистема → Оборудование
```

**Гибридный подход**: комбинация географического и функционального

### 3.2 Рекомендации по дизайну
- **Глубина**: не более 7-8 уровней
- **Ширина**: не более 1000 дочерних элементов
- **Согласованность**: единые принципы именования
- **Расширяемость**: учет будущего роста

### 3.3 Категории элементов
- **Группировка**: логическое объединение элементов
- **Security**: применение безопасности по категориям
- **Поиск**: фильтрация по категориям
- **Создание**: автоматическое назначение при создании

## 4. Аналитика и расчеты

### 4.1 Formula Data Reference
**Синтаксис**: `TagName(Expression, TimeRange, Frequency)`

**Примеры**:
- `'SINUSOID'` — текущее значение
- `'SINUSOID' + 'CDT158'` — сумма двух тегов
- `TagAvg('SINUSOID', '*-1d', 'h')` — средние часовые значения за сутки

**Функции**:
- `TagAvg()`, `TagMax()`, `TagMin()` — статистика
- `TagTot()` — сумма (интеграл)
- `TagVal()` — значение в момент времени
- `NoOutput()` — отсутствие выхода

### 4.2 Value Retrieval Modes
- **Auto**: автоматический выбор метода
- **Automatic**: для инженерных расчетов
- **At Time**: точное значение в момент
- **Interpolated**: интерполированное значение
- **Previous**: предыдущее значение
- **Exact Time**: только exact timestamp

### 4.3 PI Analysis Service
- **Назначение**: расчетная подсистема AF
- **Типы анализов**:
  - **Expression**: математические выражения
  - **Rollup**: агрегирование данных дочерних элементов
  - **Performance Equation**: сложные расчеты
  - **Event Frame Generation**: создание событийных кадров

### 4.4 Expression Analysis
**Конфигурация**:
- **Expression**: формула расчета
- **Trigger**: условие запуска (periodic, periodic and data change)
- **Frequency**: частота расчетов
- **Output**: PI Point для сохранения результата

**Пример**: `'Reactor1.Temperature' * 1.8 + 32` — Celsius to Fahrenheit

### 4.5 Rollup Analysis
- **Принцип**: агрегирование данных от дочерних элементов
- **Функции**: Sum, Average, Minimum, Maximum, Count
- **Фильтры**: по категориям, шаблонам, атрибутам
- **Time Weight**: учет времени при расчетах

## 5. Event Frames (Событийные кадры)

### 5.1 Концепция Event Frames
- **Определение**: временные периоды значимых событий
- **Компоненты**: Start Time, End Time, Attributes, Referenced Elements
- **Примеры**: партии продукции, аварии, техобслуживание

### 5.2 Event Frame Templates
- **Структура шаблона**:
  - Event Frame Attributes
  - Referenced Element Templates  
  - Attribute Templates
  - Categories

### 5.3 Event Frame Generation Analysis
**Триггеры**:
- **Condition-Based**: по условию (например, Status = 'Running')
- **Periodic**: периодические (дневные, месячные отчеты)
- **Manual**: ручное создание

**Настройки**:
- **Start Trigger**: условие начала события
- **End Trigger**: условие окончания события
- **Evaluation Frequency**: частота проверки условий

### 5.4 Consuming Event Frames
**PI System Explorer**:
- Поиск событий по датам, типам, элементам
- Аннотации и acknowledgment
- Экспорт данных

**PI Vision**:
- Find Events tool
- Event Details panel
- Compare Events
- Pinning Events
- Event Tables

**PI DataLink**:
- Event Frame reports в Excel
- Сводные таблицы для анализа
- Pivot Charts для визуализации

## 6. Notifications (Уведомления)

### 6.1 Архитектура Notifications
**Компоненты**:
- **Notification Service**: основной сервис
- **Notification Rules**: правила уведомлений
- **Delivery Channels**: каналы доставки
- **Contact Database**: база контактов
- **Subscription Database**: база подписок

### 6.2 Delivery Channels
**Email**:
- SMTP конфигурация
- HTML/Text формат
- Вложения

**Web Service**:
- HTTP POST requests
- JSON payload
- Custom endpoints

### 6.3 Trigger Conditions
- **Condition-based**: по логическим условиям
- **Event Frame-based**: при создании/изменении событий
- **Analysis-based**: по результатам анализов

### 6.4 Contact Management
- **Active Directory Integration**: автоматический импорт
- **Manual Contacts**: ручное добавление
- **Contact Groups**: группы для массовых уведомлений
- **Escalation**: эскалация при отсутствии подтверждения

## 7. Безопасность AF

### 7.1 Уровни безопасности
- **AF Database Level**: доступ к базе данных
- **Element/Attribute Level**: гранулярный доступ
- **Category Level**: безопасность по категориям
- **Template Level**: доступ к шаблонам

### 7.2 Права доступа
- **Read**: чтение данных
- **ReadWrite**: чтение и запись
- **Subscribe**: подписка на события
- **ReadWriteAdmin**: полный доступ для администрирования

### 7.3 Windows Integration
- **Windows Groups**: интеграция с AD группами
- **Windows Users**: прямое назначение прав пользователям
- **Inheritance**: наследование прав по иерархии

## 8. Substitution Parameters

### 8.1 Назначение
- **Параметризация**: создание гибких шаблонов
- **Типы**: Element, Attribute, Category-based
- **Использование**: в Data References, Analysis expressions

### 8.2 Примеры использования
- `|Element|` — имя текущего элемента
- `|@Asset|` — Element-based parameter
- `|Temperature|` — Attribute-based parameter

### 8.3 Complex Expressions
```
If TagVal('|Element|.Status','*') = "Running" 
Then TagAvg('|Element|.Temperature','*-1h','1m') 
Else NoOutput()
```

## 9. Advanced AF Features

### 9.1 Table Lookups
- **External Database Integration**: подключение к SQL, Oracle, etc.
- **Configuration**: connection strings, SQL queries
- **Usage**: enrichment of real-time data with static information

### 9.2 String Builder
- **Template строки**: `"Tank {0} level is {1} at {2}"`
- **Dynamic content**: комбинирование статических и динамических данных
- **Formatting options**: числовые форматы, даты

### 9.3 Unit of Measure (UOM)
- **Unit Classes**: группы единиц измерения (Temperature, Pressure, etc.)
- **Conversion**: автоматическое преобразование единиц
- **Default Display**: настройка отображения по умолчанию

## 10. PI Vision интеграция

### 10.1 Asset-based Displays
- **Element Relative Displays**: привязка к элементам AF
- **Context**: автоматическое изменение контекста при навигации
- **Asset Navigation**: встроенный браузер активов

### 10.2 Symbol Configuration
- **Multi-state**: различные состояния символов
- **Data Binding**: привязка к атрибутам элементов
- **Relative References**: относительные ссылки на данные

## 11. Best Practices

### 11.1 Дизайн модели
- **Итеративный подход**: начинать с небольшой области и расширять
- **Стандартизация**: единые соглашения по именованию
- **Documentation**: документирование структуры и логики

### 11.2 Performance
- **Index optimization**: оптимизация SQL индексов
- **Analysis frequency**: разумная частота расчетов
- **Bulk operations**: использование PI Builder для массовых операций

### 11.3 Maintenance
- **Regular backups**: резервное копирование AF базы
- **Version control**: управление версиями шаблонов
- **Testing**: тестирование изменений в dev среде

### 11.4 Troubleshooting
- **PI Buffer Subsystem**: буферизация для анализов
- **Analysis troubleshooting**: диагностика проблем расчетов
- **Performance monitoring**: мониторинг производительности

## 12. Ограничения и рекомендации

### 12.1 Технические лимиты
- **Элементы в базе**: до 100 миллионов атрибутов
- **Глубина иерархии**: рекомендуется не более 8 уровней
- **Дочерние элементы**: до 1000 на один parent

### 12.2 Производительность
- **SQL Server sizing**: правильный размер для нагрузки
- **Network bandwidth**: учет сетевого трафика для анализов
- **Memory requirements**: достаточно RAM для кеширования

### 12.3 Интеграция с другими системами
- **PI Connectors**: автоматическое создание AF структуры
- **Manual import**: импорт из CSV, XML
- **Third-party tools**: интеграция с CMMS, ERP системами