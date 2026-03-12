# HP-HMI SVG Symbol Library v2.0

**105 символов** для промышленных мнемосхем SCADA / HMI
Стандарт: ISA-101 / ASM Consortium / HP-HMI

## Цветовые состояния

| Состояние | HEX | Применение |
|---|---|---|
| Стоп | `#3d5a7a` | Оборудование остановлено |
| Работа | `#22d3a0` | Нормальная работа |
| Отключено | `#2a3a5e` | Выведено из эксплуатации |
| Авария | `#ff4454` | Аварийное состояние |
| Предупреждение | `#fbbf24` | Предупредительная сигнализация |

## Структура

```
auxiliary/          # Вспомогательное оборудование (8 шт.)
compressors/          # compressors (3 шт.)
electrical/          # Электрооборудование (8 шт.)
fans/          # fans (6 шт.)
fittings/          # Арматура и фитинги (7 шт.)
hx/          # hx (5 шт.)
motors/          # motors (8 шт.)
piping/          # Трубопроводы (11 шт.)
pumps/          # Насосы и компрессоры (4 шт.)
sensors/          # Датчики КИПиА (16 шт.)
sis/          # SIS / ESD (8 шт.)
valves/          # Запорная арматура (7 шт.)
vessels/          # Ёмкости и аппараты (6 шт.)
widgets/          # HMI-виджеты (8 шт.)
```

## Каталог символов

### Вспомогательное оборудование (`auxiliary/`)

| Файл | Название | EN |
|---|---|---|
| `flare-stack.svg` | Факельная установка | Flare Stack |
| `ejector.svg` | Эжектор | Ejector |
| `static-mixer.svg` | Статический смеситель | Static Mixer |
| `cyclone.svg` | Циклон | Cyclone Separator |
| `scrubber.svg` | Скруббер | Scrubber |
| `dryer.svg` | Осушитель | Dryer / Dehydrator |
| `silo.svg` | Силос / Бункер | Silo / Hopper |
| `pig-launcher.svg` | Камера пуска/приёма СОД | Pig Launcher/Receiver |

### compressors (`compressors/`)

| Файл | Название | EN |
|---|---|---|
| `centrifugal-compressor.svg` | Центробежный компрессор | Centrifugal Compressor |
| `reciprocating-compressor.svg` | Поршневой компрессор | Reciprocating Compressor |
| `screw-compressor.svg` | Винтовой компрессор | Screw Compressor |

### Электрооборудование (`electrical/`)

| Файл | Название | EN |
|---|---|---|
| `transformer.svg` | Трансформатор | Transformer |
| `circuit-breaker.svg` | Автоматический выключатель | Circuit Breaker |
| `disconnect-switch.svg` | Разъединитель | Disconnect Switch |
| `busbar.svg` | Шина (сборка) | Busbar |
| `ups.svg` | ИБП | UPS |
| `mcc-panel.svg` | Щит управления MCC | MCC Panel |
| `fuse.svg` | Предохранитель | Fuse |
| `ground.svg` | Заземление | Ground |

### fans (`fans/`)

| Файл | Название | EN |
|---|---|---|
| `centrifugal-fan.svg` | Центробежный вентилятор | Centrifugal Fan |
| `axial-fan.svg` | Осевой вентилятор | Axial Fan |
| `exhaust-fan.svg` | Вытяжной вентилятор | Exhaust Fan |
| `damper.svg` | Шибер / Заслонка | Damper |
| `air-handling-unit.svg` | Приточная установка (AHU) | Air Handling Unit |
| `blower.svg` | Воздуходувка | Blower |

### Арматура и фитинги (`fittings/`)

| Файл | Название | EN |
|---|---|---|
| `steam-trap.svg` | Конденсатоотводчик | Steam Trap |
| `strainer-y.svg` | Фильтр Y-типа | Y-Strainer |
| `flame-arrestor.svg` | Пламегаситель | Flame Arrestor |
| `orifice-plate.svg` | Диафрагма (сужающее) | Orifice Plate |
| `rupture-disc.svg` | Разрывная мембрана | Rupture Disc |
| `expansion-joint.svg` | Компенсатор | Expansion Joint |
| `sight-glass.svg` | Смотровое стекло | Sight Glass |

### hx (`hx/`)

| Файл | Название | EN |
|---|---|---|
| `shell-tube-hx.svg` | Кожухотрубный теплообменник | Shell & Tube HX |
| `plate-hx.svg` | Пластинчатый теплообменник | Plate HX |
| `air-cooler.svg` | Аппарат воздушного охлаждения | Air Cooler (Fin Fan) |
| `fired-heater.svg` | Печь / Огневой нагреватель | Fired Heater |
| `boiler.svg` | Котёл | Boiler |

### motors (`motors/`)

| Файл | Название | EN |
|---|---|---|
| `electric-motor.svg` | Электродвигатель | Electric Motor |
| `motor-with-vfd.svg` | Двигатель с ЧРП | Motor with VFD |
| `motor-starter.svg` | Пускатель двигателя | Motor Starter (DOL) |
| `soft-starter.svg` | Устройство плавного пуска | Soft Starter |
| `generator.svg` | Генератор | Generator |
| `turbine.svg` | Турбина | Turbine |
| `gearbox.svg` | Редуктор | Gearbox |
| `coupling.svg` | Муфта | Coupling |

### Трубопроводы (`piping/`)

| Файл | Название | EN |
|---|---|---|
| `process-line-liquid.svg` | Линия — жидкость | Process Line — Liquid |
| `process-line-gas.svg` | Линия — газ | Process Line — Gas |
| `process-line-steam.svg` | Линия — пар | Process Line — Steam |
| `process-line-condensate.svg` | Линия — конденсат | Process Line — Condensate |
| `flow-arrow.svg` | Стрелка потока | Flow Direction Arrow |
| `tee-junction.svg` | Тройник | Tee Junction |
| `reducer.svg` | Переход (редуктор) | Reducer |
| `blind-flange.svg` | Заглушка | Blind Flange |
| `flange-pair.svg` | Фланцевое соединение | Flanged Connection |
| `drain-point.svg` | Дренаж | Drain Point |
| `vent-point.svg` | Воздушник | Vent / Air Release |

### Насосы и компрессоры (`pumps/`)

| Файл | Название | EN |
|---|---|---|
| `centrifugal-pump.svg` | Центробежный насос | Centrifugal Pump |
| `positive-displacement-pump.svg` | Поршневой насос | Positive Displacement Pump |
| `submersible-pump.svg` | Погружной насос | Submersible Pump |
| `vacuum-pump.svg` | Вакуумный насос | Vacuum Pump |

### Датчики КИПиА (`sensors/`)

| Файл | Название | EN |
|---|---|---|
| `pressure-transmitter.svg` | Датчик давления | Pressure Transmitter (PT) |
| `temperature-transmitter.svg` | Датчик температуры | Temperature Transmitter (TT) |
| `flow-transmitter.svg` | Датчик расхода | Flow Transmitter (FT) |
| `level-transmitter.svg` | Датчик уровня | Level Transmitter (LT) |
| `analyzer-transmitter.svg` | Анализатор | Analyzer Transmitter (AT) |
| `pressure-indicator.svg` | Манометр (местный) | Pressure Indicator (PI) |
| `temperature-indicator.svg` | Термометр (местный) | Temperature Indicator (TI) |
| `pressure-switch.svg` | Реле давления | Pressure Switch (PSH) |
| `level-switch.svg` | Реле уровня | Level Switch (LSH) |
| `flow-indicator-controller.svg` | Регулятор расхода | Flow Indicator Controller (FIC) |
| `temperature-element.svg` | Термопара / ТС | Temperature Element (TE) |
| `valve-positioner.svg` | Позиционер клапана | Valve Positioner (ZT) |
| `speed-transmitter.svg` | Датчик скорости | Speed Transmitter (ST) |
| `vibration-transmitter.svg` | Датчик вибрации | Vibration Transmitter (VT) |
| `alarm-indicator.svg` | Индикатор аварии | Alarm Indicator |
| `dcs-block.svg` | Блок DCS / ПЛК | DCS / PLC Function Block |

### SIS / ESD (`sis/`)

| Файл | Название | EN |
|---|---|---|
| `esd-button.svg` | Кнопка аварийного останова | ESD Push Button |
| `sis-block.svg` | Блок SIS | SIS Logic Block |
| `esd-valve.svg` | Отсечной клапан ESD | ESD Shutdown Valve |
| `gas-detector.svg` | Датчик загазованности | Gas Detector (LEL) |
| `fire-detector.svg` | Датчик пламени | Fire / Flame Detector |
| `smoke-detector.svg` | Дымовой извещатель | Smoke Detector |
| `deluge-valve.svg` | Клапан дренчерный | Deluge Valve |
| `sis-transmitter.svg` | SIS-датчик (SIL) | SIS Transmitter (SIL-rated) |

### Запорная арматура (`valves/`)

| Файл | Название | EN |
|---|---|---|
| `gate-valve.svg` | Задвижка | Gate Valve |
| `control-valve.svg` | Регулирующий клапан | Control Valve |
| `check-valve.svg` | Обратный клапан | Check Valve |
| `ball-valve.svg` | Шаровой кран | Ball Valve |
| `butterfly-valve.svg` | Дисковый затвор | Butterfly Valve |
| `safety-relief-valve.svg` | Предохранительный клапан | Safety Relief Valve |
| `three-way-valve.svg` | Трёхходовой клапан | Three-Way Valve |

### Ёмкости и аппараты (`vessels/`)

| Файл | Название | EN |
|---|---|---|
| `vertical-tank.svg` | Вертикальная ёмкость | Vertical Tank |
| `horizontal-tank.svg` | Горизонтальная ёмкость | Horizontal Tank |
| `distillation-column.svg` | Ректификационная колонна | Distillation Column |
| `separator.svg` | Сепаратор | Separator |
| `reactor.svg` | Реактор | Reactor |
| `open-top-tank.svg` | Открытый резервуар | Open-Top Tank |

### HMI-виджеты (`widgets/`)

| Файл | Название | EN |
|---|---|---|
| `bargraph-vertical.svg` | Баргаф вертикальный | Vertical Bargraph |
| `bargraph-horizontal.svg` | Баргаф горизонтальный | Horizontal Bargraph |
| `sparkline.svg` | Спарклайн (мини-тренд) | Sparkline |
| `digital-display.svg` | Цифровой дисплей | Digital Value Display |
| `faceplate.svg` | Фейсплейт управления | Control Faceplate |
| `nav-button.svg` | Кнопка навигации | Navigation Button |
| `analog-gauge.svg` | Аналоговая шкала | Analog Gauge |
| `status-indicator.svg` | Статусная панель | Status Indicator Banner |

## Использование

Каждый SVG содержит цвет `#3d5a7a` (стоп). Для смены состояния:

```javascript
// Переключение на «работа»
svgEl.innerHTML = svgString.replaceAll('#3d5a7a', '#22d3a0');
```
