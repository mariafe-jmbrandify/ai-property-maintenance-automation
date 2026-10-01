# Changelog

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
