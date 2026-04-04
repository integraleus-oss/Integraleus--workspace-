# Конспект: Event Frames and Notifications

**Источник**: Event Frames and Notifications Training Material  
**Дата создания**: 1 апреля 2025  
**Количество страниц**: ~100

## 1. Основы Event Frames

### 1.1 Что такое Event Frames
- **Определение**: временные периоды, представляющие значимые события или состояния в процессе
- **Компоненты**:
  - **Start Time**: время начала события
  - **End Time**: время окончания события (может быть открытым)
  - **Attributes**: характеристики события
  - **Referenced Elements**: связанные AF элементы

### 1.2 Типы событий
**Примеры Event Frames**:
- **Production Batches**: партии продукции с начальной и конечной датами
- **Equipment Downtime**: периоды простоя оборудования
- **Maintenance Windows**: плановое техобслуживание
- **Alarm Periods**: активные состояния сигнализации
- **Process Phases**: фазы технологического процесса

### 1.3 Отличие от обычных данных PI
- **Временные периоды** vs. моментальные значения
- **Контекстная информация** vs. числовые данные
- **Событийно-ориентированные** vs. непрерывные данные
- **Структурированные метаданные** vs. простые теги

## 2. Event Frame Templates

### 2.1 Структура шаблонов
**Основные компоненты**:
- **Event Frame Template**: основной шаблон
- **Event Frame Attributes**: атрибуты события
- **Referenced Element Templates**: связанные элементы
- **Attribute Templates**: шаблоны атрибутов
- **Categories**: категории для группировки

### 2.2 Event Frame Attributes
**Типы атрибутов**:
- **Static Values**: константы (например, тип события)
- **PI Point References**: ссылки на временные ряды
- **Formulas**: расчетные значения
- **Start/End Time Calculations**: динамические границы событий

**Примеры атрибутов**:
```
Batch ID: "BATCH_2025_001"
Recipe: "Standard Recipe A"
Start Temperature: PI Point Reference
End Temperature: Formula calculation
Duration: End Time - Start Time
```

### 2.3 Referenced Elements
- **Primary Referenced Element**: основной элемент события
- **Secondary References**: дополнительные связанные элементы
- **Template Mapping**: автоматическое определение элементов при создании

## 3. Event Frame Generation

### 3.1 Event Frame Generation Analysis
**Назначение**: автоматическое создание Event Frames на основе условий

**Типы триггеров**:
- **Condition-Based**: создание по логическим условиям
- **Periodic**: периодическое создание (ежедневно, еженедельно)
- **Manual**: ручное создание пользователями

### 3.2 Condition-Based Generation
**Start Trigger**: условие начала события
```
'Reactor1.Status' = "Running"
'Production.Line1.State' = "Active"
'Tank.Level' > 90
```

**End Trigger**: условие окончания события  
```
'Reactor1.Status' <> "Running"
'Production.Line1.State' = "Stopped"
'Tank.Level' < 10
```

**Evaluation Frequency**: частота проверки условий (1 секунда - 24 часа)

### 3.3 Настройка генерации
**Time Zone**: часовой пояс для событий
**Maximum Duration**: максимальная длительность события
**Minimum Duration**: минимальная длительность (фильтр коротких событий)
**Include Weekends**: включение выходных дней

### 3.4 Backfilling Event Frames
- **Historical Analysis**: создание событий для исторических данных
- **Time Range Selection**: выбор периода для анализа
- **Performance Considerations**: ресурсоемкость процесса
- **Batch Processing**: обработка большими порциями

## 4. Output Expressions

### 4.1 Назначение Output Expressions
- **Data Summary**: агрегирование данных за период события
- **Calculations**: расчеты характеристик события
- **Quality Assessment**: оценка качества процесса

### 4.2 Примеры Output Expressions
**Statistical Functions**:
```
Average Temperature: EventStat('Temperature', 'Average')
Maximum Pressure: EventStat('Pressure', 'Maximum')  
Total Flow: EventStat('FlowRate', 'Total')
Standard Deviation: EventStat('Temperature', 'StdDev')
```

**Time-based Calculations**:
```
Duration: EventInfo('Duration')
Start Value: EventStat('Temperature', 'Start')
End Value: EventStat('Temperature', 'End')
Rate of Change: (EventStat('Level', 'End') - EventStat('Level', 'Start')) / EventInfo('Duration')
```

### 4.3 EventStat Function
**Синтаксис**: `EventStat(AttributeName, StatisticType, [SampleType], [TimestampFormat])`

**Статистические функции**:
- **Average**: среднее значение
- **Maximum/Minimum**: максимум/минимум
- **Total**: сумма (интеграл)
- **Count**: количество значений
- **Range**: диапазон (max - min)
- **StdDev**: стандартное отклонение

### 4.4 EventInfo Function
**Информация о событии**:
- **Duration**: длительность в секундах
- **StartTime**: время начала
- **EndTime**: время окончания
- **Name**: имя события
- **Template**: имя шаблона

## 5. Consuming Event Frames

### 5.1 PI System Explorer (PSE)
**Event Frames View**:
- **Timeline Navigation**: навигация по временной шкале
- **Search Functionality**: поиск по датам, элементам, атрибутам
- **Filtering**: фильтрация по шаблонам, категориям
- **Export**: экспорт в CSV, Excel

**Search Criteria**:
- **Time Range**: период поиска
- **Referenced Elements**: поиск по элементам AF
- **Template Names**: фильтр по шаблонам
- **Attribute Values**: поиск по значениям атрибутов

### 5.2 Event Frame Acknowledgment
**Workflow управления**:
- **Acknowledgment**: подтверждение события
- **Annotation**: добавление комментариев
- **Status Tracking**: отслеживание статуса обработки

**Use Cases**:
- Подтверждение обработки аварий
- Документирование действий оператора
- Audit trail для compliance

### 5.3 Advanced Searches
**Complex Queries**:
```
StartTime >= '*-7d' AND 
ReferencedElements.Name = 'Reactor1' AND
Template.Name = 'Batch Production'
```

**Attribute-based Search**:
```
Attributes.BatchID LIKE 'BATCH_2025%'
Attributes.Quality = 'Grade A'
```

## 6. Event Frames в PI DataLink

### 6.1 Event Frame Reports
**Excel Integration**: создание отчетов в Microsoft Excel
**Data Functions**:
- **PIEFData**: получение данных Event Frames
- **PIEFSearch**: поиск Event Frames
- **PIEFStats**: статистика по событиям

### 6.2 Reporting Functions
**PIEFData Syntax**:
```
=PIEFData(EventFrames, AttributeNames, [Options])
```

**Examples**:
```
=PIEFData("Reactor1_Batches", "BatchID;StartTime;EndTime;Duration")
=PIEFData("*", "Temperature.Maximum;Pressure.Average", "Template=Production")
```

### 6.3 Pivot Tables и Charts
**Data Aggregation**:
- Группировка по периодам времени
- Суммирование по типам событий
- Сравнительный анализ партий

**Visualization**:
- Trend charts для длительности событий
- Bar charts для количества событий
- Scatter plots для корреляций

## 7. Event Frames в PI Vision

### 7.1 Find Events Tool
**Search Interface**: графический поиск событий в PI Vision
**Features**:
- **Timeline visualization**: визуальное отображение событий
- **Interactive filtering**: интерактивная фильтрация
- **Multi-element search**: поиск по множественным элементам

### 7.2 Event Details Panel
**Event Information Display**:
- **Basic Properties**: имя, время начала/окончания, длительность
- **Attributes Table**: все атрибуты события
- **Referenced Elements**: связанные элементы AF
- **Annotations**: комментарии и acknowledgments

### 7.3 Compare Events Feature
**Comparative Analysis**:
- **Side-by-side comparison**: параллельное сравнение
- **Attribute comparison**: сравнение атрибутов
- **Trend comparison**: сравнение временных трендов

**Use Cases**:
- Сравнение партий продукции
- Анализ причин различий в качестве
- Benchmark analysis

### 7.4 Pinning Events
**Event Context Management**:
- **Pin Multiple Events**: закрепление нескольких событий
- **Context Navigation**: переключение между событиями
- **Persistent Context**: сохранение контекста при навигации

### 7.5 Event Tables
**Tabular Event Display**:
- **Custom Columns**: настраиваемые столбцы
- **Sorting**: сортировка по любому атрибуту
- **Filtering**: встроенная фильтрация
- **Export**: экспорт табличных данных

## 8. Notifications System

### 8.1 Архитектура Notifications
**Компоненты системы**:
- **PI Notifications Service**: основной сервис уведомлений
- **Notification Rules**: правила для отправки уведомлений
- **Delivery Channels**: каналы доставки (Email, Web Service)
- **Contact Database**: база контактов
- **Subscription Management**: управление подписками

### 8.2 Notification Components
**Rule Components**:
- **Trigger**: условие активации уведомления
- **Content Template**: шаблон сообщения
- **Delivery Channel**: способ доставки
- **Recipients**: получатели уведомления
- **Schedule**: расписание отправки

### 8.3 Trigger Conditions
**Event Frame Triggers**:
```
EventFrame.Template.Name = "Production Downtime"
EventFrame.Duration > TimeSpan('01:00:00')
EventFrame.Attributes.Severity = "Critical"
```

**Condition-Based Triggers**:
```
'Reactor.Temperature' > 150
'Tank.Level' < 10
'Pump.Status' = "Failed"
```

## 9. Delivery Channels

### 9.1 Email Delivery
**SMTP Configuration**:
- **Server Settings**: SMTP server, port, authentication
- **Security**: TLS/SSL encryption
- **Credentials**: service account для отправки

**Email Format Options**:
- **HTML Format**: rich formatting, embedded images
- **Plain Text**: простой текст
- **Attachments**: прикрепление файлов, отчетов

### 9.2 Web Service Delivery
**HTTP POST Integration**:
- **Endpoint Configuration**: URL назначения
- **Authentication**: API keys, basic auth
- **Payload Format**: JSON, XML customization
- **Error Handling**: retry logic, error notifications

**Custom Integrations**:
- ITSM systems (ServiceNow, Remedy)
- Messaging platforms (Teams, Slack)
- Mobile applications
- Custom business applications

### 9.3 Delivery Channel Testing
**Validation Process**:
- **Connection Testing**: проверка доступности
- **Authentication Verification**: проверка учетных данных
- **Sample Message**: отправка тестового сообщения
- **Error Diagnostics**: диагностика проблем

## 10. Message Content и Formatting

### 10.1 Content Templates
**Template Variables**:
- **{EventFrame.Name}**: имя события
- **{EventFrame.StartTime}**: время начала
- **{EventFrame.Duration}**: длительность
- **{EventFrame.Attributes.AttributeName}**: значения атрибутов

**Example Template**:
```
Subject: Production Alert - {EventFrame.ReferencedElements.Name}

Production downtime detected:
Equipment: {EventFrame.ReferencedElements.Name}
Start Time: {EventFrame.StartTime}
Duration: {EventFrame.Duration}
Reason: {EventFrame.Attributes.Reason}

Please investigate immediately.
```

### 10.2 Conditional Content
**Dynamic Content Generation**:
```
{IF EventFrame.Attributes.Severity = "Critical"}
URGENT: Immediate attention required
{ELSEIF EventFrame.Attributes.Severity = "High"}
WARNING: Investigation needed
{ELSE}
INFO: Monitoring situation
{ENDIF}
```

### 10.3 Formatting Options
**Rich Text Formatting**:
- **HTML Tables**: табличное представление данных
- **Charts и Graphs**: встроенные изображения трендов
- **Color Coding**: цветовое кодирование по severity
- **Hyperlinks**: ссылки на PI Vision displays

## 11. Contact Management

### 11.1 Contact Types
**Individual Contacts**:
- **Name**: имя контакта
- **Email**: email адрес
- **Phone**: номер телефона (для SMS)
- **Active Directory**: интеграция с AD

**Contact Groups**:
- **Distribution Lists**: группы для массовых уведомлений
- **Role-based Groups**: по ролям (операторы, инженеры)
- **Location-based**: по географическому расположению

### 11.2 Active Directory Integration
**AD Synchronization**:
- **User Import**: автоматический импорт пользователей
- **Group Mapping**: сопоставление AD групп
- **Attribute Mapping**: email, phone, department
- **Sync Schedule**: периодическая синхронизация

### 11.3 Subscription Management
**Subscription Options**:
- **Individual Subscriptions**: личные подписки
- **Group Subscriptions**: подписки групп
- **Role-based**: автоматические подписки по ролям
- **Time-based**: подписки с ограничением по времени

## 12. Acknowledgment Workflow

### 12.1 Acknowledgment Process
**Workflow Steps**:
1. **Event Detection**: обнаружение события
2. **Notification Sent**: отправка уведомления
3. **Acknowledgment Required**: требование подтверждения
4. **Response Actions**: действия получателя
5. **Closure**: закрытие события

### 12.2 Acknowledgment Methods
**Acknowledgment Channels**:
- **Email Reply**: ответ на email уведомление
- **PI Vision**: через web interface
- **Mobile App**: мобильное приложение
- **API**: программные интерфейсы

### 12.3 Escalation Rules
**Automatic Escalation**:
- **Time-based**: эскалация по времени
- **Role-based**: эскалация по иерархии
- **Severity-based**: эскалация по критичности
- **Business Rules**: кастомная логика эскалации

## 13. Best Practices

### 13.1 Event Frame Design
**Template Strategy**:
- **Standardization**: единые шаблоны для схожих процессов
- **Hierarchical Design**: иерархические шаблоны
- **Attribute Naming**: согласованные соглашения по именованию
- **Version Control**: управление версиями шаблонов

### 13.2 Performance Optimization
**Analysis Configuration**:
- **Appropriate Frequency**: разумная частота evaluation
- **Selective Processing**: обработка только необходимых элементов
- **Efficient Conditions**: оптимизированные условия триггеров
- **Resource Management**: управление нагрузкой на сервер

### 13.3 Notification Strategy
**Message Design**:
- **Clear и Actionable**: четкие и действенные сообщения
- **Appropriate Urgency**: соответствующий уровень срочности
- **Noise Reduction**: минимизация ложных уведомлений
- **Context Information**: достаточная контекстная информация

### 13.4 Maintenance
**Regular Tasks**:
- **Event Frame Cleanup**: очистка старых событий
- **Notification Rule Review**: пересмотр правил уведомлений
- **Contact List Updates**: обновление контактов
- **Performance Monitoring**: мониторинг производительности

## 14. Troubleshooting

### 14.1 Event Frame Issues
**Common Problems**:
- **Missing Events**: события не создаются
- **Incomplete Events**: события без End Time
- **Performance Issues**: медленная генерация
- **Incorrect Attributes**: неправильные значения атрибутов

**Diagnostic Tools**:
- **PI System Explorer**: просмотр статуса анализов
- **Message Logs**: анализ ошибок в логах
- **Performance Counters**: мониторинг производительности

### 14.2 Notification Problems
**Delivery Issues**:
- **Email not delivered**: проблемы SMTP
- **Web service failures**: API недоступен
- **Contact synchronization**: проблемы AD integration
- **Template errors**: ошибки в шаблонах сообщений

**Resolution Steps**:
- **Channel Testing**: проверка delivery channels
- **Log Analysis**: анализ notification logs
- **Contact Verification**: проверка контактной информации
- **Template Validation**: валидация шаблонов

## 15. Интеграция с другими системами

### 15.1 ITSM Integration
**ServiceNow Integration**:
- **Incident Creation**: автоматическое создание incidents
- **Status Updates**: синхронизация статусов
- **Work Notes**: добавление комментариев

### 15.2 Business Intelligence
**Reporting Systems**:
- **Power BI**: интеграция через PI Web API
- **Tableau**: подключение к AF данным
- **Custom Reports**: специализированная отчетность

### 15.3 Mobile Applications
**Mobile Notifications**:
- **Push Notifications**: мгновенные уведомления
- **Mobile Acknowledgment**: подтверждение с мобильных устройств
- **Field Worker Support**: поддержка полевых работников