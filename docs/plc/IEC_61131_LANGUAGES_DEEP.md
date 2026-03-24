# Языки программирования IEC 61131-3 — углублённое руководство

> Дата составления: 2026-03-20
> Источники указаны в разделе [Источники](#источники)

---

## Оглавление

1. [Общие сведения о стандарте](#1-общие-сведения-о-стандарте)
2. [Типы данных IEC 61131-3](#2-типы-данных-iec-61131-3)
3. [LD — Ladder Diagram](#3-ld--ladder-diagram)
4. [FBD — Function Block Diagram](#4-fbd--function-block-diagram)
5. [ST — Structured Text](#5-st--structured-text)
6. [IL — Instruction List](#6-il--instruction-list)
7. [SFC — Sequential Function Chart](#7-sfc--sequential-function-chart)
8. [CFC — Continuous Function Chart](#8-cfc--continuous-function-chart)
9. [Стандартная библиотека функций и ФБ](#9-стандартная-библиотека-функций-и-фб)
10. [Типовые паттерны программирования](#10-типовые-паттерны-программирования)
11. [Примеры реальных задач](#11-примеры-реальных-задач)

---

## 1. Общие сведения о стандарте

МЭК 61131-3 (ГОСТ Р МЭК 61131-3-2016) — международный стандарт, определяющий 5 языков программирования ПЛК:

- **Текстовые:** ST (Structured Text), IL (Instruction List)
- **Графические:** LD (Ladder Diagram), FBD (Function Block Diagram), SFC (Sequential Function Chart)
- **Расширение (не в стандарте):** CFC (Continuous Function Chart) — расширение FBD в CoDeSys

Принципы стандарта:
- Программа разбивается на программные модули — POU (Program Organization Unit)
- Типы POU: PROGRAM, FUNCTION, FUNCTION_BLOCK
- Единая система типов данных
- Переносимость между ПЛК разных производителей

## 2. Типы данных IEC 61131-3

### Элементарные типы

| Тип | Размер | Диапазон | Пример |
|-----|--------|----------|--------|
| BOOL | 1 бит | TRUE / FALSE | `bStart := TRUE;` |
| BYTE | 8 бит | 0..255 | `byVal := 16#FF;` |
| WORD | 16 бит | 0..65535 | `wReg := 16#ABCD;` |
| DWORD | 32 бит | 0..4294967295 | `dwVal := 16#12345678;` |
| SINT | 8 бит | -128..127 | `siTemp := -10;` |
| INT | 16 бит | -32768..32767 | `iCount := 1000;` |
| DINT | 32 бит | -2^31..2^31-1 | `diTotal := 100000;` |
| UINT | 16 бит | 0..65535 | `uiAddr := 40001;` |
| REAL | 32 бит | ±3.4E38 | `rTemp := 25.5;` |
| LREAL | 64 бит | ±1.7E308 | `lrPrecise := 3.14159265;` |
| TIME | 32 бит | T#0ms..T#49d | `tDelay := T#5s;` |
| DATE | 32 бит | D#1970-01-01.. | `dToday := D#2026-03-20;` |
| STRING | перем. | до 255 символов | `sName := 'Pump1';` |

### Пользовательские типы

```iec-st
(* Перечисление *)
TYPE E_PumpState : (STOPPED, STARTING, RUNNING, STOPPING, FAULT);
END_TYPE

(* Структура *)
TYPE ST_PumpData :
STRUCT
    bRunning    : BOOL;
    rPressure   : REAL;
    tRunTime    : TIME;
    eState      : E_PumpState;
END_STRUCT
END_TYPE

(* Массив *)
VAR
    arTemps     : ARRAY[1..10] OF REAL;
    arPumps     : ARRAY[0..3] OF ST_PumpData;
END_VAR
```

## 3. LD — Ladder Diagram

### Описание
Язык релейных (лестничных) диаграмм. Графически представлен двумя вертикальными шинами питания с горизонтальными цепями между ними. Идеален для дискретной логики.

### Основные элементы
- **Нормально открытый контакт** `—| |—` — замкнут при TRUE
- **Нормально закрытый контакт** `—|/|—` — замкнут при FALSE
- **Катушка** `—( )—` — присваивает результат цепи переменной
- **SET-катушка** `—(S)—` — устанавливает в TRUE
- **RESET-катушка** `—(R)—` — сбрасывает в FALSE
- **Детектор переднего фронта** `—|P|—`
- **Детектор заднего фронта** `—|N|—`

### Пример: Пуск/Стоп двигателя с самоподхватом

```
     bStart        bStop         bFault       bMotorRun
  ─┤ ├──────────┤/├──────────┤/├──────────( )
  │                                            │
  │  bMotorRun                                 │
  ├──┤ ├───────────────────────────────────────┘
```

Логика: Кнопка «Пуск» запускает, «Стоп» или «Авария» останавливает. Контакт bMotorRun обеспечивает самоподхват (запоминание).

### Пример: Реверс двигателя

```
     bForward     bReverse      bStop        KM1_Forward
  ─┤ ├──────────┤/├──────────┤/├──────────(S)
  
     bReverse     bForward      bStop        KM2_Reverse
  ─┤ ├──────────┤/├──────────┤/├──────────(S)
  
     bStop                                   KM1_Forward
  ─┤ ├────────────────────────────────────(R)
     bStop                                   KM2_Reverse
  ─┤ ├────────────────────────────────────(R)
```

Блокировка одновременного включения реализована перекрёстными нормально-закрытыми контактами.

## 4. FBD — Function Block Diagram

### Описание
Графический язык, напоминающий функциональные схемы на цифровых микросхемах. Блоки соединяются «проводниками», которые могут передавать сигналы любого типа (BOOL, INT, REAL, TIME и др.).

### Стандартные блоки
- **Логические:** AND, OR, XOR, NOT
- **Арифметические:** ADD, SUB, MUL, DIV
- **Сравнение:** GT, GE, EQ, LE, LT, NE
- **Таймеры:** TON, TOF, TP
- **Счётчики:** CTU, CTD, CTUD
- **Триггеры:** RS, SR
- **Регуляторы:** PID (библиотечный)

### Пример: Сигнализация давления (FBD-логика в текстовой нотации)

```
  rPressure ──┐
              ├─[GT]──┬──[AND]──> bAlarmHigh
  rSetpoint ──┘       │
                      │
  bEnable ────────────┘
```

Если давление > уставки И разрешение включено → тревога высокого давления.

## 5. ST — Structured Text

### Описание
Текстовый язык высокого уровня, похожий на Pascal. Наиболее гибкий из языков МЭК, удобен для математических вычислений, сложной логики, обработки строк.

### Синтаксис

```iec-st
(* Операция присваивания *)
iVar := 100 * 50;

(* Условие IF *)
IF rTemperature > 80.0 THEN
    bOverheat := TRUE;
    iAlarmCode := 101;
ELSIF rTemperature > 60.0 THEN
    bWarning := TRUE;
ELSE
    bOverheat := FALSE;
    bWarning := FALSE;
END_IF

(* Цикл FOR *)
FOR i := 1 TO 10 BY 1 DO
    arValues[i] := arValues[i] * 1.05;
END_FOR

(* Цикл WHILE *)
WHILE bCondition DO
    iCounter := iCounter + 1;
    IF iCounter > 100 THEN
        bCondition := FALSE;
    END_IF
END_WHILE

(* Конструкция CASE *)
CASE eState OF
    E_PumpState.STOPPED:
        bValveOpen := FALSE;
    E_PumpState.STARTING:
        bValveOpen := TRUE;
        tStartTimer(IN := TRUE, PT := T#5s);
    E_PumpState.RUNNING:
        bValveOpen := TRUE;
    E_PumpState.FAULT:
        bValveOpen := FALSE;
        bAlarm := TRUE;
END_CASE
```

### Объявление переменных

```iec-st
VAR
    iCounter    : INT := 0;          (* локальная *)
    rSetpoint   : REAL := 50.0;
END_VAR

VAR_INPUT
    bEnable     : BOOL;             (* вход ФБ *)
    rPV         : REAL;             (* процессная переменная *)
END_VAR

VAR_OUTPUT
    bDone       : BOOL;             (* выход ФБ *)
    rOut        : REAL;
END_VAR

VAR_GLOBAL
    gLastError  : INT;              (* глобальная *)
END_VAR

VAR RETAIN
    diTotalCycles : DINT;           (* энергонезависимая *)
END_VAR
```

### Пример: Таймер задержки включения (TON) в ST

```iec-st
VAR
    fbTON       : TON;
    bInput      : BOOL;
    bDelayed    : BOOL;
END_VAR

fbTON(IN := bInput, PT := T#3s);
bDelayed := fbTON.Q;
(* bDelayed станет TRUE через 3 секунды после bInput = TRUE *)
```

### Пример: Счётчик вверх (CTU) в ST

```iec-st
VAR
    fbCTU       : CTU;
    bPulse      : BOOL;
    bReset      : BOOL;
    iCount      : INT;
END_VAR

fbCTU(CU := bPulse, RESET := bReset, PV := 100);
iCount := fbCTU.CV;
IF fbCTU.Q THEN
    (* Достигнуто 100 импульсов *)
END_IF
```

## 6. IL — Instruction List

### Описание
Низкоуровневый текстовый язык, похож на ассемблер. Работает через аккумулятор. **Устаревший** — исключён из 3-й редакции IEC 61131-3 (2013), но поддерживается в старых системах.

### Основные операторы

| Оператор | Описание |
|----------|----------|
| LD | Загрузить значение в аккумулятор |
| LDN | Загрузить инвертированное значение |
| ST | Сохранить из аккумулятора |
| STN | Сохранить инвертированное |
| AND | Логическое И |
| OR | Логическое ИЛИ |
| XOR | Исключающее ИЛИ |
| NOT | Инверсия |
| ADD | Сложение |
| SUB | Вычитание |
| MUL | Умножение |
| DIV | Деление |
| S | Установить (set) |
| R | Сбросить (reset) |
| JMP | Безусловный переход |
| JMPC | Переход по условию (аккумулятор = TRUE) |
| CAL | Вызов ФБ |

### Пример: Пуск/Стоп на IL

```il
    LD      bStart
    OR      bMotorRun
    ANDN    bStop
    ANDN    bFault
    ST      bMotorRun
```

## 7. SFC — Sequential Function Chart

### Описание
Графический язык для описания последовательных процессов. Основан на сети Петри. Программа представляется как набор **шагов** (Steps) и **переходов** (Transitions).

### Элементы SFC
- **Шаг (Step)** — состояние процесса, содержит действия
- **Начальный шаг** — двойная рамка, активен при запуске
- **Переход (Transition)** — условие перехода между шагами
- **Действие (Action)** — программа, привязанная к шагу
- **Квалификаторы действий:** N (non-stored), S (set), R (reset), L (time limited), D (time delayed), P (pulse)
- **Ветвление:** параллельное (двойная горизонтальная линия) и альтернативное (одинарная)

### Пример: Процесс дозирования

```
    [Init]              ← начальный шаг
       │
    ── T1: bStartBatch ── переход: кнопка "Старт"
       │
    [Fill]              ← шаг: открыть клапан, заполнение
       │ Действие N: bValveFill := TRUE
       │
    ── T2: rLevel >= rSetLevel ── переход: уровень достигнут
       │
    [Mix]               ← шаг: перемешивание
       │ Действие N: bMixer := TRUE
       │ Действие L(T#60s): (* ограничено 60 сек *)
       │
    ── T3: tMixTimer.Q ── переход: время вышло
       │
    [Drain]             ← шаг: слив
       │ Действие N: bValveDrain := TRUE
       │
    ── T4: rLevel <= 0.5 ── переход: ёмкость пуста
       │
    [Complete]          ← шаг: цикл завершён
       │
    ── T5: TRUE ── безусловный переход обратно
       │
    [Init]
```

### Параллельное ветвление

```
    [Step1]
       │
    ═══╤═══         ← параллельное разветвление
    │       │
  [Branch1] [Branch2]  ← оба выполняются одновременно
    │       │
    ═══╧═══         ← параллельное слияние (ждёт оба)
       │
    [Step2]
```

## 8. CFC — Continuous Function Chart

### Описание
Расширение FBD, реализованное в CoDeSys. Отличие от FBD:
- Блоки размещаются свободно на «холсте» (не привязаны к цепям)
- Соединения могут идти в любом направлении, включая обратные связи
- Порядок выполнения задаётся нумерацией блоков
- Удобен для схем регулирования с обратными связями

## 9. Стандартная библиотека функций и ФБ

### Таймеры

| ФБ | Описание |
|----|----------|
| TON | Задержка включения (delay ON) |
| TOF | Задержка выключения (delay OFF) |
| TP | Импульс заданной длительности |

### Счётчики

| ФБ | Описание |
|----|----------|
| CTU | Счётчик вверх |
| CTD | Счётчик вниз |
| CTUD | Реверсивный счётчик |

### Триггеры

| ФБ | Описание |
|----|----------|
| SR | Приоритет установки |
| RS | Приоритет сброса |
| R_TRIG | Детектор переднего фронта |
| F_TRIG | Детектор заднего фронта |

### Математические функции

ABS, SQRT, LN, LOG, EXP, SIN, COS, TAN, ASIN, ACOS, ATAN, EXPT (возведение в степень)

### Преобразования типов

INT_TO_REAL, REAL_TO_INT, BOOL_TO_INT, TIME_TO_DINT и др.

### Строковые функции

LEN, LEFT, RIGHT, MID, CONCAT, INSERT, DELETE, REPLACE, FIND

## 10. Типовые паттерны программирования

### Паттерн: Пуск/Стоп с задержкой и блокировками (ST)

```iec-st
FUNCTION_BLOCK FB_MotorControl
VAR_INPUT
    bStart, bStop, bEmergency  : BOOL;
    bProtection                : BOOL;   (* тепловая защита *)
END_VAR
VAR_OUTPUT
    bRunning                   : BOOL;
    bFault                     : BOOL;
    eState                     : E_PumpState;
END_VAR
VAR
    fbStartDelay : TON;
    fbRunTimer   : TON;
END_VAR

CASE eState OF
    E_PumpState.STOPPED:
        bRunning := FALSE;
        IF bStart AND NOT bProtection AND NOT bEmergency THEN
            eState := E_PumpState.STARTING;
        END_IF

    E_PumpState.STARTING:
        fbStartDelay(IN := TRUE, PT := T#3s);
        IF fbStartDelay.Q THEN
            eState := E_PumpState.RUNNING;
            bRunning := TRUE;
            fbStartDelay(IN := FALSE);
        END_IF
        IF bStop OR bProtection OR bEmergency THEN
            eState := E_PumpState.STOPPED;
            fbStartDelay(IN := FALSE);
        END_IF

    E_PumpState.RUNNING:
        bRunning := TRUE;
        IF bStop THEN
            eState := E_PumpState.STOPPING;
        END_IF
        IF bProtection OR bEmergency THEN
            eState := E_PumpState.FAULT;
        END_IF

    E_PumpState.STOPPING:
        bRunning := FALSE;
        eState := E_PumpState.STOPPED;

    E_PumpState.FAULT:
        bRunning := FALSE;
        bFault := TRUE;
END_CASE
```

### Паттерн: Простой ПИД-регулятор (ST)

```iec-st
FUNCTION_BLOCK FB_SimplePID
VAR_INPUT
    rPV          : REAL;    (* процессная переменная *)
    rSP          : REAL;    (* уставка *)
    rKp          : REAL;    (* пропорц. коэффициент *)
    rKi          : REAL;    (* интегральный коэфф. *)
    rKd          : REAL;    (* дифференц. коэфф. *)
    rOutMin      : REAL := 0.0;
    rOutMax      : REAL := 100.0;
    tCycleTime   : TIME := T#100ms;
END_VAR
VAR_OUTPUT
    rOutput      : REAL;
END_VAR
VAR
    rError       : REAL;
    rErrorPrev   : REAL;
    rIntegral    : REAL;
    rDerivative  : REAL;
    rDt          : REAL;
END_VAR

rDt := TIME_TO_REAL(tCycleTime) / 1000.0;
rError := rSP - rPV;
rIntegral := rIntegral + rError * rDt;
rDerivative := (rError - rErrorPrev) / rDt;

rOutput := rKp * rError + rKi * rIntegral + rKd * rDerivative;

(* Ограничение выхода *)
IF rOutput > rOutMax THEN
    rOutput := rOutMax;
    rIntegral := rIntegral - rError * rDt;  (* Anti-windup *)
ELSIF rOutput < rOutMin THEN
    rOutput := rOutMin;
    rIntegral := rIntegral - rError * rDt;
END_IF

rErrorPrev := rError;
```

## 11. Примеры реальных задач

### Управление насосной станцией (ST)

```iec-st
(* Автоматическое управление по давлению *)
IF rPressure < rLowSetpoint AND NOT bPump1Running THEN
    fbPump1.bStart := TRUE;      (* включить насос 1 *)
END_IF

IF rPressure < rCriticalLow AND bPump1Running AND NOT bPump2Running THEN
    fbPump2.bStart := TRUE;      (* подключить насос 2 *)
END_IF

IF rPressure > rHighSetpoint AND bPump2Running THEN
    fbPump2.bStop := TRUE;       (* отключить резервный *)
END_IF

IF rPressure > rHighSetpoint AND NOT bPump2Running AND bPump1Running THEN
    fbPump1.bStop := TRUE;
END_IF
```

### Регулирование температуры с каскадом (концепция)

```iec-st
(* Внешний контур: температура продукта → уставка расхода теплоносителя *)
fbPID_Outer(rPV := rTempProduct, rSP := rTempSetpoint);
rFlowSetpoint := fbPID_Outer.rOutput;

(* Внутренний контур: расход теплоносителя → положение клапана *)
fbPID_Inner(rPV := rFlowActual, rSP := rFlowSetpoint);
rValvePosition := fbPID_Inner.rOutput;
```

### Система блокировок (LD-логика описана в ST)

```iec-st
(* Разрешение пуска компрессора *)
bPermitStart := bOilPressOK           (* давление масла в норме *)
    AND bCoolantTempOK                (* температура охлаждения *)
    AND NOT bVibrationHigh            (* нет вибрации *)
    AND bSuctionValveOpen             (* всасывающий клапан открыт *)
    AND NOT bEmergencyStop            (* нет аварийного останова *)
    AND tAfterStopDelay.Q;            (* выдержка после останова *)
```

---

## Источники

1. **asu-app.ru** — Язык LD: https://asu-app.ru/development/plc/yazyk-programmirovaniya-ld.php
2. **asu-app.ru** — Язык ST: https://asu-app.ru/development/plc/yazyk-programmirovaniya-st.php
3. **asu-app.ru** — Язык FBD: https://asu-app.ru/development/plc/yazyk-programmirovaniya-fbd.php
4. **Beremiz docs** — МЭК 61131-3: https://bric-beremiz.readthedocs.io/ru/latest/mek61131_3.html
5. **finestart.school** — Языки МЭК: https://finestart.school/media/programming_languages
6. **ГОСТ Р МЭК 61131-3-2016**: http://docs.cntd.ru/document/1200135008
7. **kip-world.ru** — Примеры CoDeSyS: https://kip-world.ru/primery-prostejshih-programm-dlya-codesys.html
8. **kvalifik.ru** — ST vs LD в CODESYS: https://www.kvalifik.ru/about/articles/st-vs-ld-v-codesys-iec-61131-3-kak-vybrat-yazyk-programmirovaniya-plk-v-asu-tp/
9. **plchmis.com** — Примеры таймеров: https://www.plchmis.com/ru-articles.html/
10. **electrik.info** — Схемы пуска на LD: https://electrik.info/plc/1635-shemy-puska-dvigatelya-na-ld-dlya-plk.html
11. **sm1820.github.io** — Beremiz SFC guide: https://sm1820.github.io/beremiz/iec_guide/sfc_guide.html
12. **codesys.ru** — ST для C-программиста: http://www.codesys.ru/docs/st_c.pdf
