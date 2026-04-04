# Конспект: PI System Administration for IT Professionals

**Источник**: PI System Administration for IT Professionals Version 2017 R2  
**Дата создания**: 1 апреля 2025  
**Количество страниц**: ~250

## 1. Основы администрирования PI System

### 1.1 Роль IT администратора
- **Инфраструктурные задачи**: серверы, сети, безопасность, резервное копирование
- **Отличие от PI администратора**: фокус на IT инфраструктуру vs. конфигурацию PI данных
- **Совместная работа**: с PI админами, инженерами процесса, пользователями

### 1.2 Архитектура для IT
```
Операционная сеть (OT) ↔ DMZ ↔ Корпоративная сеть (IT)
       ↓                    ↓              ↓
   Источники данных    PI Interfaces    Пользователи
   (PLC, DCS, SCADA)   PI Connectors    (Инженеры, Менеджеры)
```

### 1.3 Основные IT компоненты
- **PI Data Archive**: временные ряды, архивы, точки
- **PI Asset Framework**: метаданные, SQL Server, анализы
- **Интерфейсы сбора данных**: PI Interface, PI Connector
- **Клиентские инструменты**: PI Vision, PI DataLink, PI ProcessBook

## 2. Планирование инфраструктуры

### 2.1 Sizing Guidelines
**Небольшая система** (до 5,000 точек):
- **Сервер**: 1 машина для всех компонентов
- **Processor**: 4 cores, 2+ GHz
- **Memory**: 8+ GB
- **Disk**: SSD рекомендуется, 500+ GB

**Средняя система** (5,000-50,000 точек):
- **PI Data Archive**: отдельный сервер
- **PI AF + SQL Server**: отдельный сервер  
- **Processor**: 8+ cores
- **Memory**: 16+ GB
- **Disk**: Отдельные диски для archives/queue

**Большая система** (50,000+ точек):
- **Collective**: множественные PI Data Archive серверы
- **HA SQL Server**: кластер или миррорирование
- **Load balancer**: для PI AF серверов
- **Dedicated networks**: отдельные сети для данных

### 2.2 Дисковая подсистема
**Рекомендации по дискам**:
- **Archives**: быстрые диски (SSD), RAID 10
- **Event Queue**: отдельный диск от archives
- **SQL Database**: SSD, отдельные файлы log/data
- **OS**: отдельный диск

**Размеры**:
- **Archives**: 2-3 KB на точку для sizing
- **SQL AF Database**: 1-10 GB в зависимости от модели
- **Event Queue**: 5 MB на 1000 точек

### 2.3 Виртуализация
**Поддержка**: полная поддержка VMware, Hyper-V
**Рекомендации**:
- **Resource allocation**: dedicated CPU/memory
- **Disk I/O**: высокоскоростные диски для VM
- **Network**: достаточная пропускная способность
- **Time sync**: синхронизация времени critical

## 3. Сетевая архитектура и безопасность

### 3.1 Сетевые зоны
**OT Network (Operational Technology)**:
- Источники данных: PLC, DCS, SCADA
- Интерфейсы сбора данных
- Ограниченный доступ, высокая безопасность

**DMZ (Demilitarized Zone)**:
- PI Data Archive серверы
- PI Interface серверы  
- Контролируемый доступ между OT и IT

**IT Network**:
- PI AF серверы
- SQL Server
- Клиентские приложения
- Пользователи и приложения

### 3.2 Firewall конфигурация
**PI Data Archive порты**:
- **5450**: PI API (TCP)
- **5451**: PI Buffer Subsystem (TCP)
- **5452**: PI Update Manager (TCP)

**PI AF порты**:
- **5457**: PI AF Server (TCP)
- **5458**: PI Notifications (TCP)  
- **5459**: PI Analysis Service (TCP)

**SQL Server**:
- **1433**: SQL Server (TCP)
- **1434**: SQL Browser Service (UDP)

**Web серверы**:
- **80**: HTTP (TCP)
- **443**: HTTPS (TCP)

### 3.3 Authentication & Authorization
**Windows Integration**:
- **Active Directory**: рекомендуемый подход
- **Kerberos**: для PI Vision delegation
- **Service accounts**: dedicated accounts для сервисов

**PI Security Model**:
- **PI Identities**: роли в PI System
- **PI Mappings**: Windows User → PI Identity
- **Database Security**: доступ к таблицам PI
- **AF Security**: object-level в Asset Framework

### 3.4 Group Managed Service Accounts (gMSA)
**Преимущества**:
- Автоматическое управление паролями
- Централизованное хранение
- Отсутствие локального хранения паролей

**Требования**:
- Windows Server 2012+
- KDS Root Key в домене
- PowerShell для настройки

**Создание gMSA**:
```powershell
New-ADServiceAccount -Name SVC-PIDA -DNSHostName SVC-PIDA.domain.com
Set-ADServiceAccount -Identity SVC-PIDA -PrincipalsAllowedToRetrieveManagedPassword "PI-Servers"
```

## 4. Backup и Disaster Recovery

### 4.1 Компоненты для backup
**PI Data Archive**:
- **Database files**: PIPoint, PIArchive databases  
- **Configuration files**: PI\dat\piconfig.xml
- **Archives**: все .dat файлы архивов
- **License file**: лицензионный файл

**PI AF**:
- **SQL Database**: полный backup базы AF
- **Configuration**: AF Server конфигурация

### 4.2 Backup стратегии
**Ежедневные backup**:
- SQL Database (full/differential)
- PI Database files (cold backup)
- Configuration files

**Archive backup**:
- Старые архивы на tape/cloud storage
- Compressed archives для экономии места

**Testing**:
- Регулярные restore tests
- Disaster recovery procedures
- Documentation procedures

### 4.3 High Availability опции
**PI Data Archive HA**:
- **PI Collective**: multiple members
- **Automatic failover**: между членами коллектива
- **N-way buffering**: буферизация на все узлы

**SQL Server HA**:
- **Always On Availability Groups**
- **Database Mirroring**
- **Failover Clustering**

## 5. Monitoring и Performance

### 5.1 Performance Counters
**PI Data Archive**:
- **Archive writes/sec**: интенсивность записи
- **Queue size**: размер очереди событий
- **Connection count**: количество подключений
- **Memory usage**: использование памяти

**SQL Server**:
- **Batch requests/sec**: загрузка SQL
- **Page life expectancy**: efficiency кеширования
- **Lock waits**: конфликты блокировок

### 5.2 Monitoring Tools
**Built-in Tools**:
- **PI SMT**: System Management Tools
- **Windows Performance Monitor**
- **SQL Server Management Studio**
- **Windows Event Logs**

**Third-party Tools**:
- **SCOM**: System Center Operations Manager
- **Nagios**: Open source monitoring
- **Custom scripts**: PowerShell monitoring

### 5.3 Log Files
**PI Message Logs**:
- **Location**: PI\log\pipc.log
- **Content**: PI events, errors, warnings
- **Rotation**: автоматическое по размеру

**Windows Event Logs**:
- **Application Log**: PI service events
- **System Log**: OS level events
- **Security Log**: authentication events

**SQL Server Logs**:
- **Error Log**: SQL Server events
- **Agent Log**: SQL Agent jobs

## 6. Troubleshooting

### 6.1 Общие проблемы
**Подключения**:
- **Network connectivity**: ping, telnet port tests
- **Authentication**: PI Mappings, Windows auth
- **Firewall**: port accessibility
- **Time synchronization**: NTP sync

**Performance**:
- **Disk I/O**: slow archive writes
- **Memory**: insufficient RAM
- **Network bandwidth**: data collection bottlenecks
- **CPU**: высокая загрузка процессора

### 6.2 Diagnostic Tools
**Network**:
- **telnet hostname port**: проверка доступности портов
- **netstat -an**: активные соединения
- **wireshark**: анализ сетевого трафика

**PI System**:
- **apisnap**: тест PI API connectivity
- **PI SDK Utility**: connection manager
- **PI SMT**: system status, logs

**SQL Server**:
- **SSMS**: connection tests, query performance
- **SQL Profiler**: trace SQL activity
- **DMVs**: dynamic management views

### 6.3 Common Error Codes
**PI Errors**:
- **-10722**: Point not found
- **-10006**: No connection to server  
- **-10003**: Server not found
- **-10016**: Access denied

**Windows Errors**:
- **1326**: Logon failure - bad username/password
- **5**: Access denied
- **53**: Network path not found

## 7. Security Hardening

### 7.1 OS Level Security
**Windows Hardening**:
- **Windows Updates**: регулярные обновления
- **Antivirus**: exclusions для PI folders
- **User Account Control**: настройка UAC
- **Local Security Policy**: audit settings

**Service Accounts**:
- **Principle of least privilege**: минимальные права
- **Service account isolation**: отдельные accounts
- **Password policies**: complex passwords для обычных accounts
- **Account lockout**: защита от brute force

### 7.2 Network Security
**Firewall Rules**:
- **Restrictive by default**: deny all, allow specific
- **Port restrictions**: только необходимые порты
- **IP restrictions**: ограничение по источникам
- **Regular review**: периодический audit правил

**Encryption**:
- **TLS**: для web interfaces
- **IPSec**: для network communication
- **Certificate management**: proper cert lifecycle

### 7.3 PI System Security
**Database Security**:
- **Identity management**: proper PI Identity assignment
- **Regular audits**: review user access
- **Mapping cleanup**: remove unused mappings
- **Trust limitations**: avoid over-privileged trusts

## 8. Maintenance Tasks

### 8.1 Регулярные задачи
**Ежедневно**:
- Проверка event logs на ошибки
- Мониторинг disk space
- Backup verification
- Performance counters review

**Еженедельно**:
- Archive file management
- User access review  
- SQL maintenance (reindex, update statistics)
- Network connectivity tests

**Ежемесячно**:
- Security audit
- Performance baseline review
- Backup restore testing
- Documentation updates

### 8.2 Archive Management
**Archive Sizing**:
- Monitor archive fill rates
- Plan для future capacity
- Archive to tape/cloud для old data
- Динамические архивы management

**Cleanup Tasks**:
- Old message logs removal
- Temporary file cleanup
- Old backup files removal
- Unused PI Point cleanup

### 8.3 Database Maintenance
**SQL Server**:
- **Index rebuilds**: weekly maintenance
- **Statistics updates**: для query performance  
- **Backup verification**: restore tests
- **DBCC checks**: database integrity

**PI Database**:
- **Database repair**: if corruption detected
- **Point database cleanup**: remove unused points
- **Archive verification**: check archive integrity

## 9. Integration с Enterprise Systems

### 9.1 Active Directory Integration
**User Management**:
- **Group memberships**: для PI access control
- **Automatic provisioning**: user lifecycle
- **Single sign-on**: seamless access

**Computer Management**:
- **Group Policy**: standardized configurations
- **Certificate deployment**: automated cert management
- **Software deployment**: PI client software

### 9.2 SIEM Integration
**Log Forwarding**:
- **Windows Event Log forwarding**
- **PI Message Log integration**
- **SQL Server audit logs**

**Correlation Rules**:
- **Failed authentication attempts**
- **Unusual access patterns**
- **System performance anomalies**

### 9.3 Change Management
**Change Control**:
- **Configuration baselines**: documented configs
- **Change approval process**: for production changes
- **Testing procedures**: dev/test environments
- **Rollback procedures**: emergency rollback plans

## 10. Automation и PowerShell

### 10.1 PowerShell для PI System
**PI PowerShell Tools**:
- **Connection management**: automated connections
- **Point creation**: bulk point operations
- **Data retrieval**: automated reporting
- **System monitoring**: health checks

**Examples**:
```powershell
# Connect to PI Server
$pisrv = Connect-PIDataArchive -PIDataArchiveMachineNAme "PISERVER"

# Create new PI Point
$attr = @{Name="TEST.TAG"; PointType="Float32"; EngUnits="degC"}
Add-PIPoint -Connection $pisrv -Attributes $attr

# Get current values
Get-PIValue -PointName "SINUSOID" -Connection $pisrv
```

### 10.2 Automation Scripts
**Monitoring Scripts**:
- Disk space monitoring
- Service status checks
- Performance counter collection
- Error log parsing

**Maintenance Scripts**:
- Automated backups
- Log file rotation
- Archive management
- User access reports

## 11. Compliance и Audit

### 11.1 Regulatory Requirements
**21 CFR Part 11** (FDA):
- **Electronic signatures**: audit trails
- **Data integrity**: tamper evidence
- **Access controls**: user authentication

**SOX Compliance**:
- **Financial data integrity**
- **Access controls**: segregation of duties
- **Audit trails**: transaction logging

### 11.2 Audit Preparation
**Documentation Requirements**:
- System architecture diagrams
- User access matrices
- Change control procedures
- Backup and recovery procedures

**Evidence Collection**:
- **Access logs**: who accessed what and when
- **Configuration changes**: audit trail of changes
- **Data integrity**: checksums, validation
- **Backup verification**: restore testing evidence

## 12. Проблемы масштабирования

### 12.1 Performance Bottlenecks
**Disk I/O**:
- **Archive writes**: SSD requirements
- **Event queue**: separate disk recommended
- **SQL Database**: tempdb на отдельном диске

**Network**:
- **Bandwidth**: adequate для data collection
- **Latency**: low latency connections
- **Redundancy**: multiple network paths

**Memory**:
- **Caching**: достаточно RAM для file system cache
- **SQL Server**: memory allocation
- **Application**: PI application memory usage

### 12.2 Scaling Strategies
**Horizontal Scaling**:
- **PI Collective**: multiple PI Data Archive servers
- **Load balancing**: для PI AF servers
- **Distributed interfaces**: multiple data collection nodes

**Vertical Scaling**:
- **CPU upgrades**: more cores/faster processors
- **Memory increases**: more RAM
- **Storage improvements**: faster disks

## 13. Best Practices Summary

### 13.1 Infrastructure
- **Dedicated servers**: avoid multi-purpose servers
- **Redundancy**: eliminate single points of failure
- **Monitoring**: comprehensive system monitoring
- **Documentation**: maintain current documentation

### 13.2 Security
- **Least privilege**: minimum required access
- **Regular audits**: periodic security reviews
- **Patch management**: timely security updates
- **Network segmentation**: proper network zoning

### 13.3 Operations
- **Change control**: structured change management
- **Backup strategy**: regular tested backups  
- **Disaster recovery**: documented DR procedures
- **Training**: keep staff skills current