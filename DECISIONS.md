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
