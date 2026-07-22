# Аудит сайтов СПЕЦТЕХ - 2026-07-21

Сайты:

- `https://www.special-tech.ru/`
- `https://www.specialtechnology.ru/`

## Быстрый вывод

Оба сайта живые, быстрые и индексируемые. `specialtechnology.ru` сейчас выглядит как основной корпоративный портал и каталог продуктов. `special-tech.ru` выглядит как отдельный SEO/лидогенерационный мини-сайт под подбор SCADA и расчет лицензий.

Главная проблема не в доступности, а в позиционировании и конверсии: сайты частично конкурируют за похожие запросы, но не полностью объясняют, какой из них главный, куда отправлять разные типы заявок, и почему посетитель должен доверить расчет именно СПЕЦТЕХ.

## Факты проверки

### `www.special-tech.ru`

- Главная: `200 OK`, итоговый URL `https://www.special-tech.ru/`, около `32 KB`, быстрая загрузка по `curl` около `0.05-0.08 s`.
- TLS валиден до `2027-03-02`.
- Sitemap: `robots.txt` указывает на `https://www.special-tech.ru/sitemap-index.xml`; он доступен и ведет на `sitemap-0.xml`.
- `https://www.special-tech.ru/sitemap.xml` возвращает `404`, но это не критично, потому что правильный sitemap указан в robots.
- В sitemap около 10 URL: главная, about, contact, services, подбор SCADA, расчет лицензий, импортозамещение, новости, privacy.
- На главной есть форма `POST /send_form.php`, контакты `+7 (495) 760-09-39`, `sales@special-tech.ru`.
- Canonical, OpenGraph, Twitter card и JSON-LD Organization/WebSite/WebPage есть.
- Не найдено Yandex.Metrika/analytics-скрипта на главной по HTML-съему.

### `specialtechnology.ru`

- `www.specialtechnology.ru` редиректит на `https://specialtechnology.ru/`.
- Главная: `200 OK`, около `147 KB`, быстрая загрузка по `curl` около `0.08-0.13 s`.
- TLS для `www.specialtechnology.ru` валиден до `2026-10-11`.
- `robots.txt` и `sitemap.xml` доступны; sitemap содержит около 39 URL.
- Есть продуктовые страницы, блог, калькулятор, страницы политики и согласия.
- На главной есть форма `POST /send_form.php`; калькулятор использует отдельный endpoint `send_calc.php`, GET отвечает `405`, что нормально для POST-only.
- Есть Yandex.Metrika `107569860`.
- Canonical и OpenGraph есть.

## Что изменить срочно

1. Исправить продуктовые названия Alpha.
   - В `specialtechnology.ru/blog/scada-comparison.html` найдено `Alpha ONE+`; по текущей шпаргалке нужно `Alpha.One+`.
   - На `special-tech.ru` в hero-плашке есть `SCADA / MES / Historian`. Если MES не отдельное направление продажи, заменить на что-то вроде `SCADA / Historian / Reports` или `SCADA / архивы / отчеты`, чтобы не обещать Alpha MES.

2. Развести роли доменов.
   - `specialtechnology.ru`: официальный корпоративный портал, каталог решений, блог, калькулятор, доверие.
   - `special-tech.ru`: быстрый вход для SEO-запросов "подбор SCADA", "расчет лицензий", "импортозамещение SCADA".
   - На обоих сайтах явно написать эту роль: "Основной портал" и "Быстрая заявка инженеру". Сейчас это понятно из ссылок, но не закреплено как пользовательский сценарий.

3. Добавить измерение конверсий на `special-tech.ru`.
   - Сейчас по HTML не видно Метрики/аналитики.
   - Нужно отслеживать отправку формы, клики на калькулятор, телефон, email, переходы на `specialtechnology.ru`, `lk`.
   - Иначе SEO-лендинг будет генерировать трафик, но качество лидов будет трудно оценить.

4. Проверить `send_form.php` на обоих доменах end-to-end.
   - GET/HEAD ведут себя ожидаемо, но нужен тест реальной POST-заявки на тестовый адрес/ящик.
   - Проверить антиспам, обязательное согласие, письмо менеджеру, письмо пользователю, UTM/source в заявке.

## Что добавить для конверсии

1. Блок "Что прислать для расчета".
   - Теги: примерно сколько сигналов.
   - Клиенты: сколько рабочих мест.
   - WEB: нужен или нет.
   - Архивы: нужны ли Alpha.Historian/история.
   - Отчеты: нужны ли Alpha.Reports.
   - Резервирование: один сервер или резервная пара.
   - Протоколы: OPC UA/DA, Modbus, IEC 104/101/61850, SNMP, S7 и другие.

2. Пример результата заявки.
   - "На выходе получите: состав лицензий, вопросы к проекту, схему архитектуры, основу КП".
   - Лучше показать пример таблицы спецификации без цен или с обезличенными позициями.

3. Доверие рядом с формой.
   - Официальный дистрибьютор.
   - Сертификаты/партнерские статусы.
   - ИНН/адрес уже есть, но лучше компактно продублировать рядом с CTA.
   - Срок ответа: например "первичный ответ в течение 1 рабочего дня", если это правда операционно.

4. Кейсы или типовые сценарии.
   - Новый объект АСУ ТП.
   - Миграция с зарубежной SCADA.
   - Малый объект без резервирования.
   - Резервируемая диспетчерская.
   - Распределенная система.

5. Короткий FAQ под поисковые запросы.
   - Чем Alpha.One+ отличается от Alpha.SCADA.
   - Когда нужен Alpha.Historian.
   - Когда нужен Alpha.Reports.
   - Когда нужен выделенный WEB-сервер.
   - Какие вводные нужны для КП.

## Что добавить для SEO

1. Для `special-tech.ru` расширить sitemap контентом под коммерческие запросы:
   - `/raschet-stoimosti-scada/`
   - `/licenzii-alpha-scada/`
   - `/alpha-one-plus/`
   - `/alpha-scada/`
   - `/alpha-historian/`
   - `/alpha-reports/`
   - `/importozameshchenie-wincc/`
   - `/importozameshchenie-ignition/`

2. Добавить FAQPage schema на страницы с FAQ.
   - На главной JSON-LD уже есть, но FAQ schema даст более точную семантику для поисковиков.

3. Добавить BreadcrumbList schema на внутренние страницы.

4. На `specialtechnology.ru` проверить длинные meta description.
   - Несколько страниц имеют description 170-267 символов, это не ошибка, но сниппеты могут резаться.

5. Обновить блоговые статьи под актуальную терминологию Alpha.
   - Не использовать устаревшее `Alpha ONE+`.
   - Не упоминать устаревшие Alpha.Alarms/Alpha.Trends; в проверенных страницах таких вхождений не найдено.

## Что добавить для доверия и продаж

1. Страница "Как мы считаем лицензии".
   - Не раскрывать внутренние прайс-правила целиком, но показать методологию: вводные, проверка архитектуры, подбор редакции, проверка резервирования, проверка Historian/Reports/WEB.

2. Страница "Для интеграторов".
   - Отдельный сценарий: быстро получить спецификацию для КП/тендера.

3. Страница "Для заказчиков/эксплуатации".
   - Фокус на рисках: лишние лицензии, резерв, архивы, миграция, поддержка ОС.

4. Лид-магнит без лишней маркетинговости.
   - PDF/checklist: "Вводные для расчета лицензий Alpha".
   - Можно использовать как вложение в форму и как материал для отдела продаж.

5. Сравнительная страница "Alpha.SCADA / Alpha.Platform / Alpha.One+".
   - Аккуратно: это редакции лицензирования одной платформы, не отдельные продукты.

## Технические правки

1. Сделать `https://www.special-tech.ru/sitemap.xml` редиректом на `/sitemap-index.xml`.
   - Не обязательно, но снизит шум в проверках.

2. Проверить HSTS на `special-tech.ru`.
   - У `specialtechnology.ru` HSTS есть, у `special-tech.ru` в проверке заголовка не было.

3. Унифицировать аналитику.
   - На `specialtechnology.ru` есть Метрика, на `special-tech.ru` по HTML не видно.

4. Проверить `/lk/`.
   - Ссылка есть в навигации `special-tech.ru`, но в robots закрыт `/lk/`. Если кабинет важен для клиентов, нужен понятный landing/login flow и контроль noindex.

5. Проверить визуально мобильные первые экраны.
   - Headless Chromium из snap не смог сохранить screenshots из-за AppArmor `Permission denied`, поэтому полноценная визуальная проверка не завершена в этом проходе.

## Рекомендуемый порядок работ

1. За 1 день:
   - Исправить `Alpha ONE+` -> `Alpha.One+`.
   - Убрать/уточнить `MES` в hero-плашках, если это не отдельное направление.
   - Добавить Метрику/цели на `special-tech.ru`.
   - Настроить редирект `/sitemap.xml` -> `/sitemap-index.xml`.

2. За 2-3 дня:
   - Переписать первый экран `special-tech.ru` как четкий "быстрый расчет лицензий инженером".
   - Добавить блок "какие вводные нужны".
   - Добавить пример результата расчета.
   - Добавить FAQ и FAQPage schema.

3. За 1-2 недели:
   - Расширить SEO-структуру по кластерам Alpha.One+, Alpha.SCADA, Alpha.Historian, Alpha.Reports, импортозамещение WinCC/Ignition.
   - Добавить кейсы/типовые архитектуры.
   - Развести страницы для интеграторов и конечных заказчиков.

## Выполнено 2026-07-21

### `specialtechnology.ru`

- Сохранены бэкапы публичных страниц перед деплоем:
  - `state/tasks/2026-07-21-spectech-site-audit/backups/specialtechnology-before-deploy/alarms.html`
  - `state/tasks/2026-07-21-spectech-site-audit/backups/specialtechnology-before-deploy/scada-comparison.html`
- На `blog/scada-comparison.html` заменено устаревшее `Alpha ONE+` и недоточечные редакции на `Alpha.One+`, `Alpha.SCADA`, `Alpha.Platform`; убраны числовые пределы из этой фразы, чтобы не закреплять спорные/устаревшие значения в обзорной статье.
- На `blog/alarms.html` обновлена статья с `Alpha.Alarms 3.30` на `Alpha.HMI.Alarms 3.3`, удалены видимые упоминания `Alpha.Trends`, старого API-примера и старого запуска `Alpha.Alarms.App.exe`.
- Измененные файлы загружены через штатный HTTP deploy endpoint.
- Публичная проверка после деплоя:
  - `https://specialtechnology.ru/blog/alarms.html` вернул `200`; title/H1: `Система тревог Alpha.HMI.Alarms 3.3`; старые термины `Alpha.Alarms`, `Alpha.Trends`, `Alpha ONE+` не найдены.
  - `https://specialtechnology.ru/blog/scada-comparison.html` вернул `200`; фраза про редакции содержит `Alpha.One+`, `Alpha.SCADA`, `Alpha.Platform`; старый термин `Alpha ONE+` не найден.

### `special-tech.ru`

- Найден и использован Astro-источник: `transfers/main-server-evidence-20260709/root-openclaw-workspace/special-tech-astro/`.
- В `src/pages/index.astro` плашка `SCADA / MES / Historian` заменена на `SCADA / Historian / Reports`.
- В `src/layouts/BaseLayout.astro` добавлена Yandex.Metrika `107569860`.
- В `public/.htaccess` добавлены:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - редирект `sitemap.xml` -> `sitemap-index.xml`
- `npm ci` выполнен по lock-файлу; `npm run build` прошел успешно.
- Подготовлены артефакты:
  - полный `dist`: `state/tasks/2026-07-21-spectech-site-audit/artifacts/special-tech-dist-20260721T1012.tar.gz`
  - минимальный публичный архив без `/lk/`: `state/tasks/2026-07-21-spectech-site-audit/artifacts/special-tech-public-pages-20260721T1012.tar.gz`
- Production deploy `special-tech.ru` не выполнен: на публичном домене нет живого HTTP deploy endpoint, а FTP-пароль в локальном логе замаскирован. Для прод-выкладки нужен доступ к FTP/панели Reg.ru или восстановленный deploy endpoint.
