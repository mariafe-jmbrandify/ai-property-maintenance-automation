# ADR-003: Google Sheets as the operations database (for now)

**Status:** Accepted, revisit at ~2,000 work orders per year or 5+ concurrent editors

## Context

The platform needs a shared record of status, timestamps, and next actions that every scenario can read, write, and trigger on. Housecall Pro holds customers, estimates, and jobs, but not the PM-side data (NTE, approval contacts, PM WO # lifecycle), the exception queue, or KPI history.

## Decision

Use Google Sheets as the operations database, with:

- a documented schema ([data-model.md](../data-model.md)) and CSV templates,
- an append-only **Status History** tab so time-based KPIs are never lost to overwrites,
- protected **Assessments** and **Financials** tabs for internal cost data.

## Alternatives considered

| Option | Why not now |
|--------|-------------|
| Airtable | Better relations and interfaces, but adds a paid seat per user. Easy migration later; the schema maps 1:1. |
| Postgres / Supabase | Best for scale and reporting, but needs a UI for the office team. |
| Housecall Pro only | No place for PM approval data, exceptions, or KPI history. |

## Consequences

- Fast to build, transparent to the office team, free.
- The sheet is state, not a trigger: n8n reacts to events (Gmail, webhooks, schedules) and reads/writes the sheet, so there is no polling latency on the main path. The 10-minute Exception Monitor is the only scheduled reader.
- Row limits and concurrent edits become a problem at scale; the migration path is documented above.
