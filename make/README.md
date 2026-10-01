# Make.com Blueprints

Exported scenario blueprints go in `make/blueprints/` as each scenario is built and passes its test checklist.

## Naming

| Scenario name in Make.com | Blueprint file |
|---------------------------|----------------|
| `01 - Work Order Intake AI Extraction` | `blueprints/01-work-order-intake.json` |
| `02 - Tenant Verification HCP Customer` | `blueprints/02-tenant-verification.json` |
| … | … |

Helper scenarios use a letter suffix: `04b - Tenant Conversation Webhook`, `07b - Approval Intake`, `07c - Approval Follow-ups`, `10b - Payment Follow-ups`.

## Exporting

1. Open the scenario → **⋯** → **Export Blueprint**.
2. Before committing, remove connection IDs, webhook URLs, spreadsheet IDs, and any email addresses or phone numbers. Replace them with placeholders such as `{{GOOGLE_SHEETS_SPREADSHEET_ID}}`.
3. Commit the JSON with the scenario number in the message: `feat(s06): assessment decision blueprint`.

## Importing

**Create a new scenario → ⋯ → Import Blueprint**, then reconnect each module to your own connections and replace the placeholders using `.env.example` as the checklist.

## n8n

The same flows work in n8n. Use **Gmail Trigger**, **Google Sheets Trigger**, **HTTP Request** (Housecall Pro API), **Code** nodes for the rules (port of `src/maintenance_ops`), and **Wait** nodes for follow-up timers. Export workflows to `n8n/` with the same numbering.
