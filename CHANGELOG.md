# Changelog

## 1.2.0 — 2026-10-01

### Changed
- **Pricing now targets a 50% gross margin** instead of a 35% markup: `client_price = internal_cost / (1 − 0.50)`, i.e. internal cost is half the price (a 100% markup). The old 35% markup was only a 25.9% margin.
- `pricing.markup_pct` replaced by `pricing.target_margin_pct: 50` in `config/business_rules.yaml`; `assessments.markup_pct` column renamed `target_margin_pct`.
- Declined-estimate assessment fee raised from $75 to $150 so it also earns 50% on the $75 visit cost.
- All worked examples, sample sheets, scenario specs, tests and visuals recomputed: the reference job ($240 internal) is now $480 to the PM with $240 gross profit.

### Added
- `markup_to_margin()` helper and business rule PR-5 (always report margin, not markup); 3 more tests (43 total).

## 1.1.0 — 2026-10-01

### Changed
- **Orchestrator is now n8n** ([ADR-004](docs/decisions/ADR-004-n8n-orchestrator.md)). Scenarios 1–10 run in one main workflow with an intake branch and an event router (`POST /events/:event` → Switch); Scenarios 11–14 are separate always-on workflows.
- Every scenario spec now lists its n8n nodes, its branch and its trigger instead of Make.com modules.
- Architecture doc gains an Orchestration in n8n section with the event table; ADR-003 updated (sheet is state, not a polling trigger).
- Exception Monitor runs every 10 minutes (was hourly) so the 20-minute approval follow-up fires on time.
- Prompts reference n8n AI Agent, Structured Output Parser and expressions.
- `make/` renamed to `n8n/` with workflow, credential, webhook and export conventions.

### Added
- README banner and two system visuals in `docs/images/`.
- `N8N_BASE_URL`, `RULES_ENGINE_URL` and `MAINTENANCE_OPS_API_KEY` in `.env.example`.

## 1.0.0 — 2026-10-01

### Added
- 14 scenario specifications with flow diagrams, Make.com modules, message templates, and test checklists.
- Scenario 7 (PM Approval & Owner Authorization), previously referenced but unspecified.
- `config/business_rules.yaml` and `config/status_lifecycle.yaml` as the single source of truth.
- Python rules engine (`src/maintenance_ops`) for pricing, the NTE decision, status transitions, audience views, dispatch ranking, follow-up timers, exceptions, billing, and KPIs; 40 unit tests and GitHub Actions CI.
- Google Sheets templates for 12 tabs, including append-only Status History and Exceptions.
- AI prompts with JSON schemas for extraction, classification, tenant discovery, QA, coordination, and reporting.
- Architecture decision records ADR-001 to ADR-003 and a design review.

### Changed
- Merged the two conflicting Scenario 6 designs into one budget rule (client price vs. NTE + optional internal cap).
- Assessment fee credit defaults to "waive" so invoices match the estimate disclaimer.
- Same-visit repairs now pass through QA and tenant sign-off.
- Unified status names and the estimate title format.
