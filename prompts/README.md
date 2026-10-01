# Prompts

| File | Scenario | Purpose |
|------|----------|---------|
| [01-work-order-extraction.md](01-work-order-extraction.md) | 1 | Email → structured work order JSON |
| [02-trade-classification.md](02-trade-classification.md) | 5 | Classify the trade when intake could not |
| [03-tenant-discovery.md](03-tenant-discovery.md) | 4 | SMS/WhatsApp confirmation and discovery agent |
| [04-scope-validation.md](04-scope-validation.md) | 9 | Compare completed work to approved scope |
| [05-operations-coordinator.md](05-operations-coordinator.md) | 13 | Prioritize the work queue |
| [06-weekly-management-report.md](06-weekly-management-report.md) | 11 | Narrative for the weekly KPI report |

Principles used in every prompt:

- **AI interprets, rules decide.** Money, approvals, and status changes are decided by deterministic rules (`src/maintenance_ops`), never by the model.
- **Null, never guess.** Missing data routes the work order to a human, not to an invented value.
- **Audience-safe.** Prompts that talk to tenants or PMs never receive internal cost fields.
