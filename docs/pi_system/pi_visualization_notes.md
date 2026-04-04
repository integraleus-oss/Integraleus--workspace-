# PI System Visualization - Конспект по визуализации данных

**Источники**: Visualizing PI System Data, PI DataLink Lab, Data Exploration to Notification  
**Дата создания**: 1 апреля 2025  
**Статус**: Complete

## Обзор

Данный конспект охватывает визуализацию данных в PI System через основные инструменты: PI Vision, PI DataLink, PI ProcessBook. Включает практические примеры работы с трендами, дисплеями, отчетами и интеграцию с Excel.

## 1. PI Vision - Современная веб-визуализация

### 1.1 Основы PI Vision

**PI Vision** - современный веб-инструмент визуализации данных PI System, заменяющий PI ProcessBook для веб-интерфейсов.

#### Ключевые особенности:
- Веб-браузерная архитектура (HTML5)
- Asset-centric подход к построению дисплеев
- Responsive design для различных устройств
- Интеграция с PI Asset Framework
- Поддержка коллекций и относительных дисплеев

### 1.2 Типы символов в PI Vision

#### Базовые символы:
- **Value** - отображение текущего значения
- **Trend** - временные графики
- **Table** - табличное представление
- **Symbol** - графические элементы
- **Gauge** - стрелочные индикаторы
- **Bar Chart** - гистограммы

#### Расширенные визуализации:
- **XY Plot** - корреляционные графики
- **Pareto Chart** - диаграммы Парето
- **Multi-state** - индикаторы состояния
- **Asset Navigation** - навигация по активам

### 1.3 Asset-centric дисплеи

#### Принципы разработки:
```
Asset-based Display Design:
1. Создание template-based дисплея
2. Использование Element Relative displays
3. Collections для группировки активов
4. Smart hyperlinks между дисплеями
```

#### Конфигурация относительных дисплеев:
- Выбор базового элемента AF
- Настройка фильтров по шаблонам
- Создание иерархической навигации
- Использование substitution parameters

### 1.4 Работа с трендами

#### Настройки временных осей:
- Absolute time ranges (фиксированные периоды)
- Relative time ranges (динамические периоды)  
- Time scroll для навигации
- Multiple time scales на одном тренде

#### Параметры отображения:
```
Trend Configuration:
- Y-axis scaling (auto, manual, log)
- Line styles и colors
- Markers и annotations
- Cursors для точных значений
- Zoom и pan функции
```

### 1.5 Фильтрация и поиск

#### Asset tree navigation:
- Иерархическое представление активов
- Фильтрация по категориям
- Поиск по именам и атрибутам
- Favorites для быстрого доступа

## 2. PI DataLink - Интеграция с Excel

### 2.1 Основы PI DataLink

**PI DataLink** - надстройка Excel для извлечения данных PI System в электронные таблицы.

#### Типы функций:
- **Single-value functions** - одно значение на точку
- **Multiple-value functions** - временные ряды
- **Calculation functions** - вычислительные функции
- **Events functions** - работа с Event Frames
- **Search functions** - поиск данных
- **Properties function** - свойства точек

### 2.2 Группы функций PI DataLink

#### Одиночные значения (Single-value):
```excel
Current Value:    =PICurrentVal("tag")
Archive Value:    =PIArcVal("tag", "*-1h")  
Sampled Data:     =PISampDat("tag", "*-8h", "*", "1h")
Compressed Data:  =PICompDat("tag", "*-8h", "*")
```

#### Вычислительные функции (Calculation):
```excel
Total:            =PICalcDat("tag", "*-1d", "*", "total")
Average:          =PICalcDat("tag", "*-1d", "*", "average")
Maximum:          =PICalcDat("tag", "*-1d", "*", "maximum") 
Count:            =PICalcDat("tag", "*-1d", "*", "count")
```

### 2.3 Работа с Event Frames в DataLink

#### Compare Events function:
```excel
=PICompareEvents(database, search_start, search_end, 
                element_name, event_template, 
                "Event Name|Start Time|End Time|Duration")
```

#### Explore Events function:
```excel
=PIExploreEvents(database, search_start, search_end,
                element_path, event_template)
```

### 2.4 Advanced функции Excel с PI DataLink

#### Dynamic Array Functions (Office 365):
```excel
SORT:     =SORT(PICompDat("tag","y","t"))
FILTER:   =FILTER(data_range, criteria)
UNIQUE:   =UNIQUE(PICompDat("tag","y","t")) 
XLOOKUP:  =XLOOKUP(lookup_value, lookup_array, return_array)
```

#### PivotTables с PI Data:
- Import Event Frame data
- Create PivotTable from PI data
- Analyze downtime events
- Statistical analysis of process data

### 2.5 Оптимизация производительности DataLink

#### Рекомендации:
- Использование range references вместо individual calls
- Bulk data retrieval methods
- Управление volatile functions
- Manual calculation mode для больших workbooks

#### Диагностика:
```
AF SDK Tracing:
1. AFGetTrace.exe для мониторинга calls
2. Measurement времени выполнения
3. Оптимизация количества вызовов
4. Анализ bottlenecks
```

## 3. PI ProcessBook - Классическая визуализация

### 3.1 Основы ProcessBook

**PI ProcessBook** - традиционный Windows-инструмент для создания HMI дисплеев.

#### Типы дисплеев:
- **Static displays** - фиксированные дисплеи
- **Relative displays** - параметризованные дисплеи
- **Template-based displays** - на основе шаблонов

#### Symbol Library:
- Trends и Multi-trends
- Values и Multi-values  
- Bar charts и XY plots
- Animation объекты
- Custom symbols

### 3.2 Относительные дисплеи ProcessBook

#### Element Relative Displays:
```
Configuration:
1. Define Relative Element в дисплее
2. Use Element-relative tag references
3. Configure Element browsing
4. Set up navigation between displays
```

#### Template-based approach:
- Создание master template
- Parameterization с substitution parameters
- Deployment на множество активов
- Centralized maintenance

### 3.3 Анимация и интерактивность

#### Типы анимации:
- **Color animation** - изменение цвета по условиям
- **Size animation** - изменение размера
- **Position animation** - движение объектов
- **Rotation animation** - вращение
- **Visibility animation** - показ/скрытие

#### User interaction:
- Button actions
- Value input controls
- Navigation commands
- Popup displays

## 4. Практические примеры

### 4.1 Создание Production Dashboard

#### PI Vision Dashboard:
```
Components:
1. Overview trend - ключевые KPIs
2. Asset status table - состояние оборудования
3. Alarm summary - текущие аларм
4. Navigation symbols - переходы к детализации
```

#### Configuration steps:
1. Create base display with key metrics
2. Add asset tree navigation
3. Configure drill-down links
4. Set up refresh intervals
5. Apply security contexts

### 4.2 Excel-based отчетность

#### Transformer Loading Analysis (из учебного материала):
```excel
Data Sources:
- PI Integrator for BA SQL tables
- Direct PI DataLink functions
- External metadata tables

Report Components:
- Monthly Average Loading matrix
- Wh Delivered by location charts  
- Weekday consumption patterns
- Top overloaded transformers table
```

#### Power BI Integration:
1. PI Integrator for BA для подготовки данных
2. Import в Power BI dataset
3. Create interactive dashboards
4. Publish в Power BI Service

### 4.3 Event Frame Analysis

#### Downtime Analysis Example:
```excel
Event Frame Query:
Database: \\PISRV1\Plant Database
Template: Downtime Events  
Time Range: t-30d to *

Attributes Retrieved:
- Event Duration
- Reason Code  
- Equipment ID
- Production Loss
- Temperature conditions
```

#### PivotTable Analysis:
- Group by Reason Code
- Summarize total downtime
- Analyze by equipment type
- Trend analysis over time

## 5. Интеграция компонентов

### 5.1 PI Vision + AF Integration

#### Asset Framework leveraging:
- Element-based displays
- Template reusability
- Attribute categorization
- Calculation results display

#### Navigation patterns:
```
Hierarchy Navigation:
Site Level -> Area Level -> Unit Level -> Equipment Level
Each level с appropriate KPIs и drill-down options
```

### 5.2 DataLink + Vision Integration

#### Workflow:
1. PI Vision для real-time monitoring
2. PI DataLink для detailed analysis
3. Excel для statistical calculations
4. PI Vision для results presentation

#### Data flow:
```
Process Data -> PI Data Archive -> PI AF Server
             -> PI Vision (display)
             -> PI DataLink (analysis)
             -> Excel (calculations)
             -> Power BI (advanced analytics)
```

## 6. Best Practices

### 6.1 Дизайн визуализаций

#### General principles:
- **Clarity** - четкость и понятность
- **Consistency** - единообразие стиля
- **Context** - соответствующий контекст
- **Performance** - оптимальная производительность

#### Color schemes:
- Status colors: Red (alarm), Yellow (warning), Green (normal)
- Trend colors: Distinct colors для different variables
- Background colors: Neutral для лучшей читаемости

### 6.2 Performance оптимизация

#### PI Vision:
- Limit number of trends per display
- Use appropriate time ranges
- Configure caching settings
- Optimize AF database structure

#### PI DataLink:
- Use range references instead of individual calls
- Implement manual calculation mode
- Avoid volatile functions
- Use bulk retrieval methods

### 6.3 Security considerations

#### Access control:
- AF Security на asset level
- PI Vision display security
- Excel workbook protection
- Network-level restrictions

#### Data sensitivity:
- Classification of displayed data  
- Audit trails для access
- Encryption для sensitive data
- Regular security reviews

## 7. Troubleshooting

### 7.1 Общие проблемы

#### PI Vision issues:
- Slow loading displays
- Authentication problems  
- Missing data в trends
- Symbol configuration errors

#### PI DataLink issues:
- Excel add-in не загружается
- Slow formula calculations
- "No Data" results
- Connection timeouts

### 7.2 Диагностические инструменты

#### PI Vision:
```
Browser Developer Tools:
- Network tab для connection issues
- Console для JavaScript errors
- Performance tab для load times
```

#### PI DataLink:
```
Excel Diagnostics:
- PI DataLink Settings panel
- AF SDK Trace (AFGetTrace.exe)  
- Performance counters
- Connection status indicators
```

### 7.3 Monitoring и Maintenance

#### Regular tasks:
- Clear browser caches
- Update PI DataLink add-in
- Review display performance
- Archive old workbooks
- Update security permissions

#### Proactive monitoring:
- PI Vision server logs
- AF Database health checks  
- Network connectivity tests
- User feedback collection

## 8. Миграционные стратегии

### 8.1 ProcessBook to PI Vision

#### Migration approach:
1. **Assessment** - inventory существующих дисплеев
2. **Prioritization** - критические vs nice-to-have
3. **Redesign** - adaptation к PI Vision capabilities
4. **Testing** - validation с пользователями
5. **Deployment** - поэтапное внедрение

#### Key differences:
- Web-based vs Windows application
- Asset-centric vs tag-centric approach
- Different symbol libraries
- New navigation paradigms

### 8.2 Excel to Power BI

#### Evolution path:
```
Static Excel Reports -> 
Dynamic PI DataLink Reports ->  
Power BI Dashboards ->
Advanced Analytics Platform
```

#### Considerations:
- Data source connectivity
- Refresh requirements  
- User training needs
- Licensing implications

---

## Заключение

Визуализация данных в PI System включает мощный набор инструментов от традиционных (ProcessBook) до современных (PI Vision) и аналитических (Excel + DataLink, Power BI). Правильный выбор инструмента зависит от требований пользователей, технических ограничений и стратегических целей организации.

Ключевой тренд - переход к asset-centric подходу и интеграции с современными Business Intelligence платформами, что обеспечивает более эффективную работу с данными и принятие решений на их основе.