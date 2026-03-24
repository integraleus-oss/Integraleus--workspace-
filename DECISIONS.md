# DECISIONS

---
### ID: D-2026-03-07-01
TYPE: DECISION
STATUS: STABLE
DATE: 2026-03-07
TITLE: Memory baseline (anti-drift light)
CONTENT: Используем минимальную структуру памяти из 5 файлов: CONSTITUTION.md, STATE.md, DECISIONS.md, MEMORY.md, memory/YYYY-MM-DD.md.
RATIONALE: Достаточно для continuity без перегруза протоколами.

---
### ID: D-2026-03-07-02
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-03-07
TITLE: Memory update loop
CONTENT: После значимого обсуждения формируется Candidate memory block; запись в DECISIONS/STATE делается только после явного approve от пользователя.
RATIONALE: Сохраняем контроль качества и убираем шум.

---
### ID: D-2026-03-18-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-03-18
TITLE: Model routing and fallback policy
CONTENT: Ручной выбор пользователя имеет высший приоритет. По умолчанию main session работает на Sonnet. Opus используется для аналитики, коммерческих писем, расчётов, длинных документов и задач с высокой ценой ошибки. Codex используется для кода, shell/ssh/docker/devops, конфигов, отладки и технического исполнения. Fallback chains: routine = Sonnet → Codex → Opus; analysis = Opus → Sonnet → Codex; technical = Codex → Sonnet → Opus. При timeout/provider error/empty response/repeated transport failure допускается не более 1 retry, затем переход на следующую модель по приоритету; silent failure недопустим.
RATIONALE: Уменьшаем зависания и молчание агента, сохраняя качество на важных задачах и скорость на рутине.

---
### ID: D-2026-03-21-01
TYPE: POLICY
STATUS: ACTIVE
DATE: 2026-03-21
TITLE: Gateway-level fallback chains (Main + Garden)
CONTENT: На обоих серверах настроены fallback chains на уровне gateway (agents.defaults.model.fallbacks). Main: Opus (API key) → Codex (OAuth) → Qwen3-Coder-Free (OpenRouter). Garden: Codex (OAuth) → Qwen3-Coder-Free (OpenRouter). OpenRouter ключ: отдельный, общий для обоих серверов (profile openrouter:fallback / openrouter:garden). Мониторинг OAuth ошибок Garden добавлен в HEARTBEAT.md.
RATIONALE: Исключить простой при протухании OAuth или даунтайме провайдера. Три уровня: платный API key → OAuth подписка → бесплатная модель.

---
### ID: D-2026-03-23-01
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-03-23
TITLE: Маркировка оценочных суждений в документах
CONTENT: Все оценочные данные, субъективные суждения и приблизительные цифры в генерируемых документах должны быть явно помечены (например: «оценка автора», «приблизительно», «по экспертной оценке»). Фактические данные и проверяемые утверждения — без пометок. Цель: читатель всегда понимает, где факт, а где мнение/оценка.
RATIONALE: Честность и прозрачность перед читателем. Пользователь явно попросил ввести это правило.

---
### ID: D-2026-03-23-02
TYPE: RULE
STATUS: ACTIVE
DATE: 2026-03-23
TITLE: Актуальность моделей в документах
CONTENT: При генерации документов, содержащих упоминания ИИ-моделей (названия, размеры, рекомендации), перед генерацией выполнять веб-поиск актуальных версий. Не использовать устаревшие поколения (например Qwen 2.5, если уже вышел Qwen 3.5). Указывать дату актуальности в документе.
RATIONALE: Модели обновляются быстро, документы с устаревшими рекомендациями вводят в заблуждение.
