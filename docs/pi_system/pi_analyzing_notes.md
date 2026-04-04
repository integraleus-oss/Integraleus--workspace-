# PI System Data Analysis - Конспект по анализу данных

**Источники**: Analyzing PI System Data Version 2018, AF Easy Wins, Data Exploration to Notification  
**Дата создания**: 1 апреля 2025  
**Статус**: Complete

## Обзор

Данный конспект охватывает комплексный анализ данных PI System: от Asset Analytics и Event Frame Generation до интеграции с Business Intelligence инструментами. Включает практические примеры, best practices и методологию аналитических проектов.

## 1. Основы анализа данных в PI System

### 1.1 Архитектура для анализа данных

**Компоненты системы анализа:**
- **PI Data Archive** - хранение временных рядов
- **PI Asset Framework** - контекст и метаданные  
- **PI Analysis Service** - серверные вычисления
- **PI Integrator for BA** - подготовка данных для BI
- **Business Intelligence Tools** - Power BI, Excel, Spotfire

### 1.2 Типы анализа данных

#### Real-time анализ:
- Stream analytics через PI Analysis Service
- Event-driven calculations
- Continuous KPI monitoring
- Alarm и notification generation

#### Historical анализ:
- Batch processing через PI Integrator for BA
- Time-series analytics в Excel/Power BI
- Statistical analysis и trending
- Root cause analysis

#### Predictive анализ:
- Machine learning integration
- Forecasting models
- Anomaly detection
- Predictive maintenance

## 2. PI Analysis Service - Серверная аналитика

### 2.1 Типы анализов

#### Expression Analysis:
```javascript
// Пример расчета OEE
vAvailability = TagAvg('Machine_Status', '*-1h', '*')
vPerformance = TagAvg('Actual_Rate', '*-1h', '*') / 'Target_Rate' * 100
vQuality = (1 - TagAvg('Defect_Rate', '*-1h', '*')) * 100
OEE = vAvailability * vPerformance * vQuality / 10000
```

#### Rollup Analysis:
```javascript
// Агрегация по дочерним элементам
Sum of Production = SUM of child elements' Production attributes
Average Efficiency = AVERAGE of child elements' Efficiency attributes
Maximum Temperature = MAX of child elements' Temperature attributes
```

#### Event Frame Generation:
```javascript
// Trigger для событий downtime
StartTrigger: 'Machine_Status' = "Stopped"
EndTrigger: 'Machine_Status' <> "Stopped"
```

### 2.2 Expression Variables - Оптимизация вычислений

#### Best Practice - использование переменных:
```javascript
// Плохо - повторные вычисления
if TagAvg('Temperature','*-1h','*') > 100 then "High"
else if TagAvg('Temperature','*-1h','*') > 50 then "Normal"  
else "Low"

// Хорошо - использование переменной
vTempAvg = TagAvg('Temperature','*-1h','*')
if vTempAvg > 100 then "High"
else if vTempAvg > 50 then "Normal"
else "Low"
```

#### Преимущества variables:
- Снижение нагрузки на PI Analysis Service
- Улучшение читаемости кода
- Упрощение maintenance
- Повышение производительности на 60%+

### 2.3 Scheduling стратегии

#### Типы расписаний:
```
Periodic:
- Fixed frequency (каждые X секунд/минут/часов)
- Daily at specific time  
- Weekly/Monthly schedules

Event-Triggered:
- На изменение input данных
- При получении новых archive events
- Conditional triggering
```

#### Рекомендации по scheduling:
- Не запускать analysis чаще чем необходимо
- Использовать Event-Triggered для real-time responses
- Periodic для batch calculations
- Offset времени для избежания simultaneous execution

### 2.4 Performance Best Practices

#### Analysis организация:
```javascript
// Consolidation vs Splitting
Критерии решения:
1. Dependency - зависимые расчеты в одном analysis
2. Scheduling - одинаковая частота выполнения  
3. Manageability - легкость troubleshooting
```

#### Управление analysis в Error состоянии:
- Disable до устранения проблем
- Regular monitoring через Management interface
- Automated alerts на failed analyses

## 3. Event Frame Generation и Analysis

### 3.1 Концепция Event Frames

**Event Frames** - структурированные записи о значимых периодах времени в процессе.

#### Ключевые характеристики:
- **Name** - уникальное имя события
- **Start/End Time** - временные границы
- **Referenced Elements** - связанные активы
- **Attributes** - дополнительные данные
- **Duration** - автоматически рассчитываемая длительность

### 3.2 Event Frame Templates

#### Структура template:
```
Event Frame Template:
├── General (Naming Pattern, Referenced Elements)
├── Attribute Templates
│   ├── PI Point Data Reference attributes
│   ├── Formula-based attributes  
│   └── String Builder attributes
└── Categories (для организации)
```

#### Naming Patterns:
```javascript
// Примеры naming patterns
%ELEMENT% %TEMPLATE% %STARTTIME:yyyy-MM-dd HH:mm:ss%
%..%\%ELEMENT% Batch_%STARTTIME:yyyyMMdd_HHmm%
Production Run - %ATTRIBUTE:ProductType% - %DURATION% hrs
```

### 3.3 Event Frame Generation Analysis

#### Trigger configuration:
```javascript
// Простой trigger
StartTrigger: 'Production_Status' = "Running"

// Сложный trigger с условиями
StartTrigger: 'Production_Status' = "Running" AND 'Temperature' > 80

// Trigger с временными условиями
StartTrigger: TagAvg('Flow_Rate', '*-5m', '*') > 100
```

#### Output at Close expressions:
```javascript
// Variables для поиска timestamp
vPrevBatchEnd = FindEq('Batch_Status', '*', '-1d', "Complete")

// Расчет batch statistics  
TotalProduction = TagTot('Production_Rate', EventFrame("StartTime"), EventFrame("EndTime"))
AverageTemp = TagAvg('Temperature', EventFrame("StartTime"), EventFrame("EndTime"))
QualityIssues = TagCount('Quality_Flag', EventFrame("StartTime"), EventFrame("EndTime"), "Bad")
```

### 3.4 Event Frame Consumption

#### PI System Explorer:
- Event Frame Search interface
- Filter по templates, elements, time ranges
- Attribute display и export
- Manual event frame creation

#### PI DataLink для Event Frames:
```excel
// Compare Events - flat format
=PICompareEvents("\\Server\Database", "t-30d", "*", 
                 "*", "Production_Batch",
                 "Event Name|Start Time|Duration|Total Production")

// Explore Events - hierarchical format  
=PIExploreEvents("\\Server\Database", "t-7d", "*",
                 "Production Area", "Downtime_Event")
```

#### PI Vision Event Frame displays:
- Event Timeline symbols
- Event table displays
- Integration с asset navigation

## 4. Business Intelligence Integration

### 4.1 PI Integrator for Business Analytics

#### Архитектура:
```
PI AF Server -> PI Integrator for BA -> Target System
                    ↓
            SQL Server, CSV Files, 
            Power BI, Spotfire, etc.
```

#### Типы Views:
- **Asset Views** - based на Elements и Element Templates
- **Event Views** - based на Event Frames и Event Frame Templates  
- **Streaming Views** - real-time data streaming

### 4.2 Asset View Configuration

#### Shape Builder process:
```
1. Select AF Database
2. Navigate to target element
3. Drag elements to Shape Builder
4. Configure filters (by template)
5. Add attributes of interest
6. Set time range и value mode
7. Choose target (SQL Server, CSV)
8. Publish view
```

#### Time Value Modes:
- **Interpolated** - регулярная выборка
- **Compressed** - только изменения значений
- **Plot** - оптимизировано для графиков

### 4.3 Power BI Integration

#### Data preparation workflow:
```
PI System Data -> PI Integrator for BA -> SQL Server
                                       -> Power BI Dataset
                                       -> Power BI Reports
```

#### Пример: Transformer Loading Analysis
```dax
// DAX measures в Power BI
Service Hours = CALCULATE(COUNT('Transformer Loading'[Loading]))
Average Loading = AVERAGE('Transformer Loading'[Loading])
Monthly Trend = CALCULATE([Average Loading], 
                         DATESBETWEEN('Date'[Date], 
                                     STARTOFMONTH('Date'[Date]),
                                     ENDOFMONTH('Date'[Date])))
```

#### Визуализации в Power BI:
- **Matrix** - loading по transformers и months
- **Clustered Column Charts** - consumption по locations
- **Line Charts** - trends по time periods
- **Tables** - top performers/issues с PI Vision links

### 4.4 Excel Advanced Analytics

#### PivotTable analysis:
```excel
Data Source: Event Frame data от PI DataLink
Rows: Equipment ID, Reason Code
Columns: Month  
Values: Sum of Downtime Duration, Count of Events
```

#### Statistical analysis:
```excel
// Excel formulas для PI data
Correlation: =CORREL(temperature_range, production_range)
Regression: =SLOPE(), =INTERCEPT(), =RSQ()
Standard Deviation: =STDEV.S(pi_data_range)
Percentiles: =PERCENTILE.INC(pi_data_range, 0.95)
```

#### Dynamic Array Functions (Office 365):
```excel
// Filtering PI data
=FILTER(pi_data, production_column > 1000)
=SORT(UNIQUE(equipment_list))
=XLOOKUP(equipment_id, lookup_table, specifications)
```

## 5. Predictive Analytics

### 5.1 Simple Predictive Models в Excel

#### Linear regression example (из Dryer lab):
```excel
// Regeneration time prediction
y = mx + b
где:
y = Predicted Regeneration Duration  
x = Drying Cycle Barrels
m = slope от SLOPE() function
b = intercept от INTERCEPT() function
```

#### Model deployment в AF:
```javascript
// Asset Analytics prediction
vDryingBarrels = 'Drying Cycle Barrels'
vPredictedRegen = 0.0234 * vDryingBarrels + 2.5
// Coefficients из Excel regression analysis
```

### 5.2 Advanced Analytics Integration

#### External ML platforms:
```
PI System -> Data Export -> ML Platform (Python, R, Azure ML)
                        -> Model Training  
                        -> Model Deployment
                        -> Predictions -> PI System
```

#### Real-time scoring:
- PI Analysis Service для simple models
- PI Web API для external model calls
- Edge computing для latency-sensitive applications

## 6. Практические сценарии

### 6.1 Production Optimization Analysis

#### Fleet Generation example:
```javascript
// Asset Analytics для generation efficiency
Utilization = TagTot('Gross Generation','*-1h','*') * 24 / 'Hourly Capacity' * 100
Efficiency = 'Net Generation' / 'Gross Generation' * 100

// Rollup на station level
Average Station Efficiency = AVERAGE of child units' Efficiency
Total Station Output = SUM of child units' Net Generation
```

#### Power BI dashboard components:
- Generation trends по units
- Efficiency comparison charts
- Capacity utilization heatmaps
- Maintenance scheduling optimization

### 6.2 Asset Condition Monitoring

#### Temperature anomaly detection:
```javascript
// Event Frame Generation для temperature excursions
StartTrigger: TagAvg('Temperature','*-1h','*') > 'High_Temp_Limit'
Duration: Until temperature returns to normal range
Attributes: Max Temp, Duration, Equipment State, Operator
```

#### Condition-based maintenance:
- Vibration trend analysis
- Oil analysis correlation
- Performance degradation tracking
- Predictive failure models

### 6.3 Quality Analysis

#### Process capability studies:
```excel
// Statistical Process Control в Excel
Cp = (USL - LSL) / (6 * σ)
Cpk = MIN((USL - μ)/(3σ), (μ - LSL)/(3σ))
где USL/LSL - specification limits, μ - process mean, σ - standard deviation
```

#### Root cause analysis workflow:
```
1. Event Frame capture аномальных периодов
2. Multi-variate analysis в Power BI/Excel
3. Correlation analysis между process variables  
4. Statistical significance testing
5. Process improvement recommendations
```

## 7. Best Practices для Data Analysis

### 7.1 Data Quality Management

#### Validation strategies:
- **Range checking** - значения в expected пределах
- **Rate of change limits** - избежание spurious spikes
- **Consistency checks** - cross-validation между related points
- **Completeness monitoring** - tracking missing data

#### Bad data handling:
```javascript
// В Analysis expressions
if BadVal('Temperature') then NoOutput()
else if 'Temperature' > 1000 then NoOutput() // Range check
else 'Temperature' * 1.8 + 32 // Convert C to F
```

### 7.2 Performance Optimization

#### Analysis Service tuning:
- **Expression variables** для repeated calculations
- **Appropriate scheduling** - не чаще чем необходимо
- **Disable failing analyses** до устранения проблем
- **Monitor evaluation times** через Preview Results

#### Data volume management:
```
PI Integrator for BA:
- Use filters для reduction data volume
- Appropriate time ranges
- Parametrized queries для external tables
- Compression settings для storage optimization  
```

### 7.3 Security и Governance

#### Data access control:
- AF Security на element/attribute level
- PI Vision display-level security
- Row-level security в Power BI
- Excel workbook protection

#### Change management:
- Version control для analysis templates
- Testing procedures для new analyses
- Documentation standards
- Rollback procedures

## 8. Troubleshooting

### 8.1 Analysis Service Issues

#### Common problems:
```
Performance Issues:
- Slow evaluation times
- High CPU utilization  
- Memory consumption
- Backfill taking too long

Configuration Issues:  
- Syntax errors в expressions
- Missing input attributes
- Incorrect scheduling
- Template mapping problems
```

#### Diagnostic tools:
- **Preview Results** для testing expressions
- **Management interface** для monitoring status
- **PI System Management Tools** для performance counters
- **Windows Event Logs** для error details

### 8.2 BI Integration Issues

#### PI Integrator for BA troubleshooting:
```
Common Issues:
- Connection timeouts к target databases
- Data type mismatches
- Performance problems с large datasets
- Authentication failures

Diagnostics:
- View logs в PI Integrator interface
- SQL Server Profiler для database issues
- Network connectivity testing
- Permission verification
```

#### Power BI performance:
- Dataset refresh optimization
- DAX formula performance  
- Visual rendering issues
- Gateway connectivity problems

### 8.3 Data Quality Issues

#### Identification methods:
```
Statistical Methods:
- Outlier detection (Z-score, IQR)
- Trend analysis для drift detection
- Correlation analysis для consistency
- Missing data percentage tracking
```

#### Remediation strategies:
- Automated data cleansing rules
- Manual review processes  
- Source system improvements
- Backup data source utilization

## 9. Advanced Topics

### 9.1 Real-time Analytics Architecture

#### Stream processing pattern:
```
Data Sources -> PI Interfaces -> PI Data Archive
                              -> PI Analysis Service (real-time)
                              -> External Stream Processors
                              -> Action Systems (Notifications, Control)
```

#### Edge analytics:
- Local processing на plant level
- Reduced latency для critical decisions
- Bandwidth optimization
- Offline capability

### 9.2 Machine Learning Integration

#### Model lifecycle management:
```
1. Data Preparation (PI Integrator for BA)
2. Feature Engineering (Excel/Python)
3. Model Training (Azure ML/Python)
4. Model Validation (Statistical methods)
5. Deployment (PI Analysis Service/Web API)
6. Monitoring (Performance tracking)
7. Retraining (Continuous improvement)
```

#### Common use cases:
- **Predictive maintenance** - equipment failure prediction
- **Quality prediction** - product quality forecasting
- **Anomaly detection** - unusual pattern identification
- **Optimization** - process parameter optimization

### 9.3 Big Data Analytics

#### Scalability considerations:
```
Volume: Handling millions of tags, high-frequency data
Variety: Multiple data types, external data sources  
Velocity: Real-time processing requirements
Veracity: Data quality и reliability challenges
```

#### Architecture patterns:
- Data lake integration
- Distributed processing (Spark, Hadoop)
- Cloud analytics platforms
- Hybrid on-premises/cloud solutions

---

## Заключение

Анализ данных в PI System представляет собой комплексную экосистему инструментов и методологий - от real-time серверной аналитики через PI Analysis Service до advanced Business Intelligence с Power BI и машинного обучения. 

Ключевые успешные факторы:
- **Правильная архитектура данных** с Asset Framework
- **Эффективные вычисления** с оптимизированными Analysis expressions
- **Качественная подготовка данных** через PI Integrator for BA  
- **Интеграция с современными BI инструментами**
- **Continuous improvement** процессов анализа данных

Современные тенденции направлены на интеграцию с cloud платформами, machine learning и real-time decision making системами.