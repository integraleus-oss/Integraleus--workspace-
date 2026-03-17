# Драйвер IEC 60870-5-104 в Alpha Platform: архитектура, настройка и подводные камни

Реализация собственного драйвера IEC 60870-5-104 с нуля — задача не для слабонервных: асинхронная state machine с sequencing, таймауты на трёх уровнях и ASDU parsing требуют серьёзной инженерной проработки. Alpha Platform решает эту проблему встроенным модулем IEC-104, но понимание внутреннего устройства протокола остается критически важным для диагностики реальных проблем на объектах.

## Протокол IEC 60870-5-104: что под капотом

IEC 60870-5-104 представляет собой TCP-оболочку для протокола 60870-5-101, где транспортный уровень реализован через APCI (Application Protocol Control Information), обёртывающий APDU (Application Protocol Data Unit).

### Структура APCI и типы фреймов

```
APCI Header (6 bytes):
+--------+--------+--------+--------+--------+--------+
|  0x68  | Length |  Send  |  Recv  |  Ctrl  |  Ctrl  |
|  (1B)  |  (1B)  |  (2B)  |  (2B)  |  (1B)  |  (1B)  |
+--------+--------+--------+--------+--------+--------+
```

Протокол оперирует тремя типами фреймов:

- **I-format** (Information) — передача данных с sequence numbering
- **S-format** (Supervisory) — подтверждения без данных  
- **U-format** (Control) — управляющие команды (STARTDT, STOPDT, TESTFR)

### Пример реального телеграмма STARTDT

```hex
68 04 07 00 00 00  // U-format: STARTDT act
68 04 0B 00 00 00  // U-format: STARTDT con
```

Sequence numbering работает через счётчики N(S) и N(R), где k-parameter определяет максимальное количество неподтверждённых I-фреймов (обычно 12), а w-parameter — когда отправлять S-frame с подтверждением (обычно 8).

### State machine и таймауты

Конечный автомат протокола:

1. **STOPPED** → STARTDT act → **STARTED** (после STARTDT con)
2. **STARTED** → передача I-frames с данными
3. **TESTFR** каждые t3 секунд для keepalive
4. **STOPDT** для graceful shutdown

Критические таймауты согласно IEC 60870-5-104:2006:
- t0: connection timeout (30s)
- t1: send timeout (15s) 
- t2: acknowledgment timeout (10s)
- t3: test timeout (20s)

### ASDU и типы информационных объектов

На прикладном уровне данные инкапсулируются в ASDU (Application Service Data Unit) с указанием:
- Type ID (тип информационного объекта)
- IOA (Information Object Address) — адрес объекта
- Quality descriptors (IV, NT, SB, BL, OV)

Основные типы объектов:
- M_SP_NA_1 (1) — single point без временной метки
- M_ME_NA_1 (9) — нормализованное измеренное значение  
- C_SC_NA_1 (45) — single command
- C_CS_NA_1 (103) — синхронизация времени

### Грабли с Quality descriptors

Quality flags часто игнорируются, что приводит к записи invalid данных в historian:

```c
// НЕПРАВИЛЬНО: игнорирование QDS
if (asdu->type == M_ME_NA_1) {
    float value = normalized_to_float(info_obj->value);
    historian_write(ioa, value, timestamp);
}

// ПРАВИЛЬНО: проверка качества
if (asdu->type == M_ME_NA_1) {
    uint8_t qds = info_obj->quality;
    if (!(qds & QDS_IV) && !(qds & QDS_BL)) {  // not invalid, not blocked
        float value = normalized_to_float(info_obj->value);
        historian_write(ioa, value, timestamp);
    } else {
        historian_write_invalid(ioa, timestamp);
    }
}
```

## Архитектура модуля IEC-104 в Alpha.Server

Модуль IEC-104 интегрирован в архитектуру Alpha.Server 6.4.28 как нативный компонент без промежуточных OPC-слоёв. Это обеспечивает прямой доступ к TCP-стеку операционной системы и минимизирует латентность.

### Двунаправленная архитектура

Alpha.Server поддерживает одновременно режимы **Master** (опрос slave-устройств) и **Slave** (публикация данных для внешних мастеров). Это позволяет реализовать сценарий protocol converter: Alpha.Server получает данные по Modbus RTU и публикует их по IEC-104 для вышестоящих систем.

```
Modbus RTU ──→ Alpha.Server ──→ IEC-104
(Slave mode)     (Native)      (Master mode)
     ↓              ↓              ↓
[Устройства]   [Буферизация]  [SCADA верхнего]
               [и обработка]     [уровня]
```

### Интеграция с компонентной архитектурой

Модуль работает как часть распределённой архитектуры Alpha.Server с up to 2,000,000 тегов на инстанс. Данные передаются между компонентами через внутреннюю шину с буферизацией — это гарантирует отсутствие потерь при кратковременных разрывах IEC-104 соединений.

### Нативная поддержка Linux

В отличие от решений на Wine, модуль скомпилирован нативно для x86_64/ARM64 Linux (Astra Linux SE, РЕД ОС, ALT Linux, Ubuntu). Это обеспечивает:
- Доступ к native TCP socket options (TCP_NODELAY, SO_KEEPALIVE)
- Интеграцию с systemd для автозапуска
- Использование epoll для эффективного I/O multiplexing

## Настройка в Alpha.DevStudio: пошаговый разбор

Конфигурирование IEC-104 в Alpha.DevStudio построено на концепции адресных карт и элементов станций.

### Шаг 1: Создание адресной карты

**Карта адресов МЭК 60870-5** определяет mapping между внутренними тегами Alpha.Server и IOA-адресами протокола:

```
Внутренний тег    | IOA  | Type ID | Описание
------------------|------|---------|------------------
TEMP_REACTOR_1    | 1001 | M_ME_NA_1 | Температура реактора
PUMP_STATUS_1     | 2001 | M_SP_NA_1 | Состояние насоса
CMD_VALVE_CLOSE   | 3001 | C_SC_NA_1 | Команда закрытия
```

Alpha.DevStudio поддерживает импорт адресных карт из Excel (.xlsx), что упрощает миграцию существующих конфигураций.

### Шаг 2: Конфигурация элемента станции

**Станция МЭК 60870-5-104** — логический элемент с свойством **Номер станции** (Common Address of ASDU). Этот номер используется в ASDU header для идентификации источника данных.

```xml
<!-- Фрагмент конфигурации -->
<Station104 Name="RTU_Station_1" CommonAddress="15">
    <AddressMap>MAPS\RTU_AddressMap.xml</AddressMap>
    <Parameters>
        <t0>30000</t0>  <!-- Connection timeout, ms -->
        <t1>15000</t1>  <!-- Send timeout, ms -->
        <t2>10000</t2>  <!-- Ack timeout, ms -->
        <t3>20000</t3>  <!-- Test timeout, ms -->
        <k>12</k>       <!-- Max unconfirmed I-frames -->
        <w>8</w>        <!-- Ack after w I-frames -->
    </Parameters>
</Station104>
```

### Шаг 3: Добавление опросчика

**Опросчик МЭК 60870-5-104** — компонент Alpha.Server application, который обеспечивает TCP-соединение и выполнение протокольной state machine.

### Шаг 4: Build и deploy

После build решения Alpha.DevStudio генерирует конфигурационные файлы для Linux Alpha.Server. Deploy выполняется через встроенные средства — конфигурация копируется на target машину и Alpha.Server перезапускается с новой конфигурацией.

## Буферизация и отказоустойчивость

### Внутренняя буферизация данных

Alpha.Server реализует многоуровневую буферизацию между компонентами:

1. **Acquisition buffer** — кольцевой буфер для данных от источников
2. **Protocol buffer** — буфер для исходящих IEC-104 сообщений
3. **Archive buffer** — буфер для historian при недоступности БД

При разрыве IEC-104 соединения данные накапливаются в protocol buffer. После восстановления соединения выполняется GI (General Interrogation) для синхронизации состояний.

### Hot standby архитектура

Для критически важных применений Alpha.Server поддерживает hot standby с автоматическим failover:

```
Primary Alpha.Server ──┐
                       ├── Heartbeat ──→ IEC-104 Clients
Secondary Alpha.Server ─┘
```

Переключение выполняется на основе heartbeat через shared memory или TCP keepalive. Время переключения составляет менее 5 секунд.

### DMZ и connection inversion

Для промышленных сетей с жёсткими firewall правилами Alpha.Server поддерживает connection inversion: 

```
DMZ Zone          Internal Network
┌─────────────┐   ┌──────────────┐
│ Alpha.Server │←──│ Alpha.Server │
│ (Converter)  │   │ (Main SCADA) │
└─────────────┘   └──────────────┘
      ↑                  ↑
  IEC-104 out      Internal data bus
```

Alpha.Server в DMZ выступает как protocol converter, принимая исходящие соединения от внешних систем, но получая данные от внутренней сети через Alpha.AccessPoint.

## Типичные грабли при работе с IEC 104

### Проблема: k/w parameter mismatch

**Симптомы**: Периодические disconnection каждые 2-3 минуты

**Причина**: Мастер настроен на k=12, slave — на k=8. При достижении k=8 неподтверждённых фреймов slave перестаёт отвечать, мастер ждёт до k=12, затем разрывает соединение.

**Решение**: Синхронизация параметров k и w между мастером и slave-устройством.

### Проблема: Некорректная синхронизация времени

**Симптомы**: События в SCADA отображаются с неправильными timestamp

**Причина**: C_CS_NA_1 команды синхронизации времени не учитывают часовые пояса.

```c
// НЕПРАВИЛЬНО: локальное время без timezone
time_t local_time = time(NULL);
send_time_sync(local_time);

// ПРАВИЛЬНО: UTC с учётом DST
struct tm utc_tm;
gmtime_r(&local_time, &utc_tm);
send_time_sync_utc(&utc_tm, get_dst_offset());
```

### Проблема: Дублирование IOA адресов

**Симптомы**: Часть тегов не обновляется в SCADA

**Причина**: Два different tag имеют одинаковый IOA. SCADA принимает только последний пришедший.

**Решение**: Валидация уникальности IOA на этапе конфигурирования.

### Проблема: Firewall dropping idle connections

**Симптомы**: Соединение разрывается ровно через 30 минут простоя

**Причина**: Firewall/NAT timeout меньше, чем t3 parameter.

**Решение**: Снижение t3 до 10-15 секунд или настройка TCP keepalive:

```c
int keepalive = 1;
setsockopt(sock, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive));

int keepidle = 10;   // Start keepalive after 10s idle
int keepintvl = 3;   // Send keepalive every 3s
int keepcnt = 3;     // Drop after 3 failed keepalives
setsockopt(sock, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(keepidle));
setsockopt(sock, IPPROTO_TCP, TCP_KEEPINTVL, &keepintvl, sizeof(keepintvl));
setsockopt(sock, IPPROTO_TCP, TCP_KEEPCNT, &keepcnt, sizeof(keepcnt));
```

### Проблема: GI flooding при reconnect

**Симптомы**: После каждого переподключения SCADA получает лавину данных

**Причина**: Неправильная реализация General Interrogation — отправка всех тегов вместо только изменившихся.

**Решение**: Отправка GI response только для тегов с актуальными данными:

```c
// НЕПРАВИЛЬНО: дамп всех тегов
void send_general_interrogation_response(int cot) {
    for (int ioa = 1; ioa <= MAX_IOA; ioa++) {
        send_measurement(ioa, get_tag_value(ioa), cot);
    }
}

// ПРАВИЛЬНО: только валидные теги
void send_general_interrogation_response(int cot) {
    for (int ioa = 1; ioa <= MAX_IOA; ioa++) {
        if (is_tag_valid(ioa)) {
            send_measurement(ioa, get_tag_value(ioa), cot);
        }
    }
}
```

## Заключение

IEC 60870-5-104 остаётся базовым протоколом для телемеханики в энергетике и водоканале благодаря простоте реализации и широкой поддержке в legacy оборудовании. Alpha Platform предоставляет готовый модуль с нативной Linux поддержкой и integration в промышленную архитектуру с буферизацией и отказоустойчивостью.

Выбор протокола зависит от архитектурных требований:
- **Modbus RTU/TCP** — для простых применений с ограниченным числом тегов (до 1000)
- **IEC 60870-5-104** — для телемеханики среднего масштаба с requirement по time synchronization и event handling (1000-50000 тегов)
- **OPC UA** — для современных индустриальных применений с security требованиями и semantic interoperability (50000+ тегов)

Понимание внутреннего устройства IEC-104 критично для диагностики проблем на объектах: неправильная настройка параметров протокола может приводить к потере данных или нестабильной работе телемеханики. Детальная документация API модуля IEC-104 в Alpha Platform не является публично доступной; фокус данной статьи — на конфигурационном уровне интеграции и решении типичных проблем.

---

*Автор: Разработчик specialtechnology.ru*
*Дата публикации: Март 2026*