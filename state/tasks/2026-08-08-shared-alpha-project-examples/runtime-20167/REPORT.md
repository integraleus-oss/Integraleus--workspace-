# Runtime-проверка проекта 20167 на Home

Дата: 2026-08-08
Контур: отдельная рабочая копия в `runtime-20167`; deploy не выполнялся.

## Итог

- Alpha.HMI `kns.hmi` успешно скомпилирован текущим Alpha.HMI 2.0.35 и экспортирован в `kns.ni.binom`.
- Главная форма `Main_GK_KNS` успешно запущена в Alpha.HMI Viewer и реально отрисована.
- DevStudio-решение `Bachat_KNS.solution` успешно скомпилировано Alpha.DevStudio 4.2.2.
- Серверные конфигурации Alpha.Server и Alpha.AccessPoint успешно построены командой `devstudio.cli build --action rebuild`.
- Deploy серверной конфигурации не выполнялся; активный Alpha-BPR-контур не менялся и не перезапускался.

## Безопасная копия

До компиляции серверной части в копии выполнено:

- все Modbus TCP/RTU master переведены в `active="false"`;
- адреса исходной сети `192.168.13.0/24` заменены на TEST-NET `192.0.2.0/24`;
- `anonimous-can-write="true"` заменено на `false` в обоих TCP Server;
- `write-values-on-activation="true"` заменено на `false`;
- транзакционный autosave `.tx-ab3bb8` сохранён в `quarantine/` и исключён из Designer-smoke.

Исходная копия до правок зафиксирована в `evidence/source-sha256.txt`; нейтрализованный OMX — в `evidence/server-neutralized-sha256.txt`.

## Результаты проверок

### Alpha.HMI

- Компиляция: успешно, ошибок нет, 592 предупреждения.
- Основные классы предупреждений:
  - устаревшие SQL-элементы отчётных форм;
  - неизвестные управляющие последовательности в строках и путях;
  - возможные циклы `ValueChanged -> Value`;
  - потерянные свойства и целевые элементы у экземпляров;
  - неиспользуемые типы;
  - коллизии ресурсов AlarmSettings между проектом и внешним модулем.
- Designer: проект открывается в чистом XDG-профиле.
- Viewer: `Main_GK_KNS` отрисована из текущего `ni.binom`.
- Runtime-журнал содержит многочисленные предупреждения `QFont::fromString: Invalid description '(empty)'`.

### Alpha.DevStudio / Alpha.Server

- Compile: успешно, ошибок нет, 50 предупреждений.
- Build: успешно, ошибок нет, 177 предупреждений.
- Существенные дефекты:
  - около 49 имён компьютерных узлов не соответствуют текущим правилам домена;
  - `DR_14_UZO2.P.Trip` имеет тот же адрес, что `DR_14_UZO1.P.Trip`;
  - множество сигналов не имеют адресов в ModbusTcpSlave и не попадут в Alpha.Server;
  - отключённые для стенда Modbus master корректно отмечены сборщиком как неактивные.

## Визуальные наблюдения

- На главной форме действительно показана крупная технологическая мнемосхема обогатительной фабрики.
- Потерянные/недоступные связи видны как `?`, нулевые значения и частично пустые подписи.
- Ярко-розовый массово используется для обычного оборудования и значений. По текущему HPHMI-чек-листу это антипример: насыщенный цвет перегружает обзор и конкурирует с аварийной индикацией.

## Тестовые данные и command/readback

Полноценный тест `команда -> запись -> изменение состояния -> readback` пока не выполнен.

Причина: безопасный отдельный сетевой namespace из пользовательского systemd на этом ядре недоступен; systemd явно сообщил, что `PrivateNetwork=yes` не применён. Разворачивать 20167 в действующие Alpha.Domain/Alpha.Server сервисы нельзя, потому что это затронет Alpha-BPR и порты 1010/4950. На Home также не найден подтверждённый пользовательский CLI/API записи значений Alpha.Imitator для этого проекта.

Для следующего шага нужен отдельный root-level network namespace/container либо отдельный экземпляр Alpha.Domain/Alpha.Server/Alpha.Imitator с согласованными альтернативными портами. До явного разрешения root-level изменения не выполнялись.

## Evidence

- `evidence/hmi-compile.json` — полный HMI compile log.
- `evidence/server-compile.jsonl` — DevStudio compile log.
- `evidence/server-build.jsonl` — DevStudio build log.
- `evidence/hmi-designer.png` — Designer после открытия проекта.
- `evidence/hmi-viewer.png` — отрисованная `Main_GK_KNS`.
- `evidence/server-neutralization.txt` — подтверждение обезвреживания связей.
- `evidence/alpha-bpr-services-before.txt` и `after.txt` — неизменные PID/start timestamps/состояния BPR-сервисов.
