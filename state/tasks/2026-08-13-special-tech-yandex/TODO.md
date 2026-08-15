# special-tech.ru — Yandex recommendations

- [x] Проверить четыре варианта домена и основной canonical
- [x] Проверить robots.txt, sitemap.xml и sitemap-index.xml
- [x] Проверить наличие кода Яндекс Метрики
- [x] Настроить 301 на `https://www.special-tech.ru`
- [x] Проверить production после изменения
- [ ] Привязать существующий счётчик к сайту в Яндекс Вебмастере
- [ ] Проверить/добавить организацию в Яндекс Бизнес

## Исходное состояние, 2026-08-13

- `http://special-tech.ru/` — 200 (нужен 301)
- `http://www.special-tech.ru/` — 200 (нужен 301)
- `https://special-tech.ru/` — 200 (нужен 301)
- `https://www.special-tech.ru/` — 200, canonical корректный
- `/sitemap.xml` — 301 на `/sitemap-index.xml`
- `robots.txt` — sitemap указывает на canonical www/https
- Яндекс Метрика присутствует в production HTML

## Результат

- Production `.htaccess` сохранён перед изменением в
  `/home/stanislav/projects/spectech-sites/backups/special-tech-before-canonical-redirect-20260813T0949/.htaccess`.
- Три неканонических варианта теперь отдают `301` на canonical с сохранением
  пути и query string; canonical отдаёт `200`.
- Счётчик `110922935` активен, адрес `www.special-tech.ru`, API permission `own`.
- В Вебмастере подтверждены и `https://special-tech.ru/`, и главное зеркало
  `https://www.special-tech.ru/`.
- Привязка Метрики выполняется двухстадийно только в интерфейсе Яндекса:
  запрос из Метрики, подтверждение и включение обхода в Вебмастере. Сохранённая
  Chromium-сессия истекла и перенаправляет на вход в Yandex ID.
- Яндекс Бизнес требует выбора/создания карточки и подтверждения владельца кодом
  на телефон организации; без интерактивного входа и кода завершать нельзя.
