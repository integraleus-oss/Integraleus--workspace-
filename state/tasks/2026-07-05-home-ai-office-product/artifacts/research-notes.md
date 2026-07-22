# Research Notes: Aizor and AI Office Builders

Checked: 2026-07-05

## Aizor Public Surface

Sources:
- Official site: `https://aizor.ai/`
- Download page: `https://aizor.ai/download`
- Cabinet links observed on site: `https://lk.aizor.ai/login`, `https://lk.aizor.ai/register`, `https://lk.aizor.ai/dashboard`
- Public API base observed in frontend chunks: `https://api.aizor.ai`
- Public offer: `https://aizor.ai/offer`, updated 2026-07-04
- Marketplace API sample: `https://api.aizor.ai/api/v1/marketplace/catalog?sort=popular&limit=50`
- Public plans API: `https://api.aizor.ai/api/v1/subscription/public-plans`

### Positioning

Aizor positions itself as a desktop AI-agent platform for automating work on a user's computer. The public metadata says: "AI-agent for your computer", with automation of tasks, code generation, and file management. The main hero copy in the JS bundle positions Aizor as a "platform for creating AI agents".

The product is not only a chat UI. The visible product shape is:

- Public marketing site.
- Downloadable desktop agent.
- Separate web cabinet.
- Public marketplace.
- Subscription/token billing.
- Author/partner/referral programs.
- Support chat.

### Commercial Model

Public plans API returned:

| id | name | monthly RUB | tokens | skills | devices | max agents | rpm | concurrent |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| trial | Ознакомительный | 0 | 100000 | 3 | 1 | 3 | 5 | 1 |
| basic | Старт | 1990 | 375000 | 10 | 3 | 10 | 30 | 3 |
| pro | Бизнес | 4990 | 935000 | 20 | 7 | 20 | 60 | 5 |
| premium | Команда | 9990 | 1965000 | 999 | 999 | 999 | 120 | 10 |
| enterprise | Максимум | 21990 | 4535000 | 999 | 999 | 999 | 300 | 20 |

Offer terms include:

- Desktop app access.
- Compute resources/tokens for AI-agent work.
- Personal cabinet for account/subscription.
- Built-in chat support.
- Marketplace of ready-made AI agents.
- Authors receive revenue share from usage of their solutions.
- Referral program.
- Refund path via `support@aizor.ai`.
- Legal entity listed as LLP "CIT", Kazakhstan.

### Marketplace

Public marketplace API returned `total=426`, with at least 50 public cards visible without auth.

Card model includes:

- `name`, `slug`, short/long description.
- Setup guide in Markdown.
- Cover image.
- Category.
- Tags.
- Setup level.
- Prerequisites.
- Required integrations and tools.
- Skills count.
- Author.
- Version metadata.
- Installs, rating, reviews.
- Official/editor-choice flags.

Observed categories/use cases:

- Finance: receipts, invoices, bank/account summaries, tax calendar.
- Analytics: marketplace metrics, reputation dashboard, revenue anomalies, content analytics, stock forecast.
- Content/marketing: SEO article, alt/meta, shorts A/B, trend response, VK/Yandex metrics, email reactivation.
- Sales: pipeline review, tender compliance, CRM from calls.
- Support: RAG over archive, reviews/questions, helpdesk routing, delivery escalation.
- HR: interview assessment, churn risk.
- Admin/legal: court deadlines, inventory, marking/MRC compliance.
- Development: bug triage, incident postmortem.

Pattern: Aizor sells "work roles" and "business outcomes", not raw tools. Many cards mention familiar Russian/CIS business systems in tags or guides: Telegram, YouGile, 1C, Google Sheets, Yandex, VK, Ozon, Wildberries, 2GIS, amoCRM, RetailCRM, UniSender, Usedesk, SDEK, Почта России, Честный знак.

### Product Signals Worth Copying

- Marketplace cards are use-case oriented and concrete.
- Each solution has a setup guide, prerequisites, and integration requirements.
- Pricing is simple for users: plans plus token pool.
- There is a creator economy hook: publish agents and earn from usage.
- Desktop app is framed as "agent for your computer", which makes local files/apps understandable to non-technical users.
- Public site emphasizes "without technical knowledge" and "first result quickly".

### Product Signals to Treat Carefully

- Security details are mostly marketing/legal from the public surface; actual permission boundaries are not visible without installing.
- Desktop automation is powerful but risky: screen/files/browser/actions require explicit approval UX and logs.
- Marketplace agents from users require moderation, versioning, install-time permission display, and emergency disable paths.

## Adjacent Platforms

Sources:

- Zapier Agents: `https://zapier.com/agents`
- Zapier safety article: `https://zapier.com/blog/safe-trustworthy-ai-agents/`
- Lindy: `https://www.lindy.ai/`
- Yandex AI Studio agents docs: `https://aistudio.yandex.ru/docs/en/ai-studio/concepts/agents/`
- Yandex Agent Atelier: `https://aistudio.yandex.ru/en/agent-atelier`
- MWS AI Agents Platform: `https://mts.ai/product/ai-agents-platform/`
- Kore.ai Artemis: `https://www.kore.ai/ai-agent-platform`

Common product patterns:

- Plain-language/no-code agent creation.
- Prebuilt templates or marketplace.
- Integration catalogue as the product moat.
- Knowledge/data grounding.
- Scheduled/background work.
- Human-in-the-loop approvals.
- Guardrails and permissions.
- Run logs/traces/observability.
- Model choice hidden behind task/plan, not exposed first.
- Team/admin governance for enterprise.

## Initial Conclusion

Aizor's benchmark value is not model quality. It is packaging:

- Roles instead of configs.
- Marketplace instead of folder of scripts.
- Setup wizard instead of YAML.
- Russian business integrations instead of generic developer tooling.
- Subscription/token mental model instead of API keys.
- Desktop/local context as a consumer-friendly story.

For Home, the right analogue is not a public SaaS clone first. It is a local/private "agent factory" UI over OpenClaw: catalogue, wizard, permissions, schedules, logs, and role packages that compile into OpenClaw agents/skills/cron/message routes.
