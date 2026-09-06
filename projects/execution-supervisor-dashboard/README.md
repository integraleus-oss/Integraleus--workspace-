# Оркестратор · Control Room

Локальная read-only панель для `execution-supervisor`. Она читает только
`state/tasks/**/execution-supervisor-state.json` и соседние admission/evidence
файлы. Панель ничего не запускает, не останавливает и не изменяет.

## Запуск

```bash
cd /home/stanislav/.openclaw/workspace/agents/main/projects/execution-supervisor-dashboard
npm start
```

Открыть `http://127.0.0.1:4177`. По умолчанию сервер слушает только loopback.
Для другого порта: `DASHBOARD_PORT=4180 npm start`.

## Возможности

- автообновление каждые 5 секунд;
- сводка RUNNING / SUCCEEDED / attention / pending delivery;
- поиск и фильтр по статусам;
- фактическая проверка runner PID для RUNNING;
- Flow, Run, PID, exit code, маршрут и длительность;
- таймлайн запуска и доставка итогового уведомления;
- просмотр evidence;
- адаптивный интерфейс для телефона.

## Проверка

```bash
npm test
```
