# Store Generator skill audit

Source: `https://aizorlab.ru/wp-content/uploads/2026/08/store-generator.zip`

SHA-256: `8a81e09e4e4c718767deee62b3398acd5785a56e5494baebf6fcffcec29c1f32`

## Checklist

- [x] Archive downloaded and inventoried without executing its contents
- [x] `SKILL.md` and `GUIDE.md` read completely
- [x] YAML/frontmatter validated with OpenClaw skill validator
- [x] Privileged commands and credential flows reviewed
- [x] WordPress MCP and Application Password guidance checked against official docs
- [x] Findings summarized

## Verdict

The archive is not malware by itself: it contains only `SKILL.md` and `GUIDE.md`, no executable payloads. It is a detailed prompt/playbook, not a deterministic installer. Its demo speed comes from a fixed Storefront layout, six synthetic products, hard-coded Russian shipping/payment defaults, and broad root-level automation.

Do not run it unchanged on a production or shared VPS. It disables SSH host-key verification, requests root credentials, uses plain HTTP on a public port, removes the default nginx site, opens UFW, installs unpinned latest packages, creates an admin-bound MCP Application Password, and asks the agent to return credentials in chat. It has no backup/rollback, TLS, least-privilege, secret handling, idempotency, staging, or production acceptance gates.

## What it automates

- WordPress, WooCommerce, and Storefront installation
- Database/user creation and nginx/UFW configuration
- Six demo products and AI images via OpenRouter
- Fixed branded homepage, content pages, menus, logo, favicon, and WebP copies
- Russian currency, shipping, and manual payment defaults
- WordPress MCP Adapter installation and an Application Password
- Basic curl/grep checks

## Material findings

1. **Critical - server takeover blast radius.** Root SSH plus `StrictHostKeyChecking=no` makes host impersonation possible and gives a prompt-driven agent unrestricted control.
2. **Critical - credentials over insecure transport.** The site is configured as `http://<ip>:8081`, while the skill creates an admin Application Password. WordPress says Application Passwords should be used only over HTTPS.
3. **High - destructive shared-host behavior.** It removes `/etc/nginx/sites-enabled/default`, may delete other enabled sites as a suggested fix, restarts nginx, and opens a firewall port.
4. **High - supply-chain drift.** WordPress core, WooCommerce, Storefront, and the MCP Adapter are installed from moving latest releases without hashes or pinned versions.
5. **High - secrets exposed to conversations/logs.** SSH, database, WordPress admin, and MCP passwords are inserted in commands or returned to the user. There is no vault, redaction, rotation, or revocation step.
6. **High - not sale-ready.** "Card payment" is only a bank-transfer instruction. No acquiring, online receipt/fiscalization, order email test, privacy/offer/consent, refund workflow, tax, inventory, or real shipping integration is configured.
7. **Medium - fragile and non-idempotent.** Fixed names (`shop`, `shop_user`, `/var/www/shop`, port 8081) collide on rerun; there is no state detection or rollback.
8. **Medium - weak verification.** HTTP 200 and grep checks do not test checkout completion, payment, email, permissions, responsive layout, accessibility, performance, backup restore, or security headers.
9. **Medium - demo content presented as facts.** Synthetic testimonials, ratings, review counts, contact details, delivery promises, and return claims can be published without business approval.
10. **Low - skill packaging.** It validates successfully, but at 401 lines it is oversized; the long HTML template belongs in `assets/`, operational details in `references/`, and deterministic deployment in reviewed scripts.

## Safe adaptation

- Run only on a fresh staging VPS or container snapshot; never on an existing shared host.
- Use a dedicated non-root deploy user with narrowly scoped sudo; enforce SSH host keys and key-only auth.
- Provision TLS/domain before enabling WordPress Application Passwords; create a separate least-privileged automation user and revoke its credential after deployment.
- Pin versions and hashes; keep nginx in a site-specific file; never remove unrelated configs; use a configurable, validated firewall rule.
- Store secrets outside prompts and shell history; do not echo or return them in chat.
- Add preflight inventory, idempotent steps, backup/snapshot, rollback, and explicit approval before firewall/nginx/database mutations.
- Mark all products, reviews, contacts, prices, shipping, payments, and legal texts as drafts until human approval.
- Add end-to-end checkout/email, security, accessibility, mobile, performance, and restore tests before any production claim.

## Bottom line

Useful as a demo recipe and source of layout ideas. Unsafe as a production deployment skill. The impressive result is mostly repeatable orchestration and a fixed template, not evidence that DeepSeek V4 Pro alone built a commerce system from one sentence.
