# Alpha.Alarms 3.30 — Конспект

**Продукт:** Программный комплекс «Альфа платформа», модуль Alpha.Alarms
**Разработчик:** АО «Атомик Софт» (Automiq)
**Версия:** 3.30.0
**Назначение:** Управление тревогами и событиями в системах промышленной автоматизации (SCADA)

## Системные требования
- ОС: Windows 7 / 2008 Server+, x32/x64
- CPU: Intel Celeron 1.6 ГГц+
- RAM: ≥1 ГБ
- Диск: ≥500 МБ
- Сеть: Ethernet 10/100/1000
- Лицензия: HASP USB-ключ (Sentinel)

## Установка
- Путь: `C:\Program Files\Automiq\Alpha.Alarms` (или x86)
- Конфиг: `C:\ProgramData\AlphaPlatform\Alarms\config.xml`
- Debug-режим: `<Debug>true</Debug>` в config.xml
- Диагностика: журнал приложений Windows или Alpha.Tools EventLogViewer

## Варианты запуска
1. **Стандартный** — через меню Пуск или Alpha.Alarms.App.exe
2. **С параметрами командной строки:**
   - `mode operative/historical` — режим работы
   - `ActiveViewMode ActiveConditions/Journal` — вид отображения
   - `Begin/End` — интервал для исторического режима (DD.MM.YYYY-hh:mm:ss)
   - `SetAdvancedFilter "условие"` — расширенный фильтр отображения
   - `SetAdvancedRequestFilter "условие"` — расширенный фильтр запроса
   - `LoadConfiguration "путь"` — альтернативная конфигурация
   - `FileParam "путь"` — параметры из файла (UTF-8)
   - `IsFullAccessAllowed true/false` — полный доступ
   - `EditSettingsNotAllowed` — запрет настроек
   - `windowpos X,Y windowsize W,H` — размер/положение окна
3. **Встраиваемый компонент** — в Alpha.HMI

## Группы важности событий (1-1000)
- **Прочие** — метод исключения
- **Значительные** — 334-666 (по умолчанию)
- **Особой важности** — 667-1000 (по умолчанию)
- **Важные** — диапазон не задан по умолчанию
- Пользователь может переопределить диапазоны
- Можно создавать пользовательские группы важности

## Оперативные события
- Режим реального времени — поступление событий онлайн
- Два режима отображения: журнал / список активных условий
- Лимит строк: 50-100 000 (неквитированные особо важные не подчиняются лимиту)
- **Квитирование** — подтверждение оператором
- **Подавление** — временное скрытие событий от источника/объекта
- **Блокирование** — полное блокирование событий
- Звуковая сигнализация
- Слежение за последним событием

## Аналитика (гл. 7)
- Настройка столбцов таблицы: время генерации, срабатывания, деактивации, сообщение, источник, важность, квитирование, пользователь, комментарий, значение/качество сигнала
- Цветовая сигнализация по группам важности + мигание
- Сортировка: по клику на заголовок + пользовательские правила с приоритетами
- Подсветка неквитированных в дереве сигналов

### Фильтрация
- **Предустановленные фильтры** — создание/редактирование/импорт/экспорт (XML)
- **Фильтр пользователя** — на текущий сеанс, логические связки И/ИЛИ/НЕ
- **Расширенные фильтры** — через параметры запуска или API
- **Серверная фильтрация** — по зонам, тегам, маскам
- **По объекту** — из дерева сигналов
- **По событию** — по конкретному сигналу-источнику

## Дополнительные возможности (гл. 8)
- Экспорт: .xlsx, .xml, .csv
- Интеграция с Alpha.Trends (графики сигналов)
- Просмотр экранных форм (интеграция с ПК «Лоцман»)
- Печать: таблица событий, реал-тайм (матричный принтер), настройка
- Откат настроек к значениям по умолчанию
- Буфер обмена — копирование тегов

## Встраиваемый компонент + Alarms-API (гл. 9)
Для использования в Alpha.HMI проектах.

### Свойства API (30+):
- ActiveMode — оперативный/исторический
- ShowMilliseconds, RowHeight, OperativeVisibleRowCount
- GUIModificationAvailable, ButtonPanelVisible
- Mute — беззвучный режим
- FilterActive, IsAdvancedFilterActive
- EventDisplayOrder — порядок сообщений
- IsFullAccessAllowed — полный доступ
- CurrentEventsAvailable, EventHistoryAvailable
- FilterAvailable, SnapshotAvailable
- ClearingCurrentEventsAvailable
- SoundPlaybackManagmentAvailable
- WindowsFixed, EditingSettingsAvailable
- AcknowledgmentAvailable
- EventHistoryPagedViewingAvailable, PrintingAvailable
- FollowLatestEvent, EnableSortingOnGridHeader
- EventTableSortAvailability, ExportDataAvailability
- FileSystemSafeMode
- ActiveViewMode — журнал/активные условия
- AreaTreeVisible, LookLatestEvent

### Функции API:
- AckAll, AckSelected — квитирование
- CancelHistoryQuery — отмена запроса истории
- ClearAcknowledgedEvents, ClearOperativeEventList — очистка
- ClearSoundQueue — очистка звуковой очереди
- DisplayCurrentEvents, DisplayCurrentEventsSnapshot — отображение
- GetUnacknowledgedEventsCount — счётчик неквитированных
- LoadConfiguration — загрузка конфигурации
- LogOff — выход

## Смежные модули (упоминаются)
- Alpha.Trends — графики/тренды
- Alpha.HMI — дизайнер экранных форм
- Alpha.Security — подсистема безопасности
- Alpha.Tools — утилиты (EventLogViewer)
- ПК «Лоцман» — экранные формы

---
*Источник: Alpha.Alarms 3.30 Руководство пользователя, АО «Атомик Софт», 2015-2022*
*Обработано: 2026-03-11*
