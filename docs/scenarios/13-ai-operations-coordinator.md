# Scenario 13 — AI Operations Coordinator

| | |
|---|---|
| **Make.com name** | `13 - AI Operations Coordinator` |
| **Trigger** | Every 5 minutes; daily 7:00 AM queue; daily 6:00 PM summary; chat messages |
| **Systems** | Google Sheets, OpenAI / Claude, Slack / Teams / GHL, Gmail |
| **Code** | `maintenance_ops.followups` (rules first), prompt [`05-operations-coordinator.md`](../../prompts/05-operations-coordinator.md) |

## Objective

Act as a virtual operations manager: watch every active work order, keep `next_action` / `owner` / `due` current, surface bottlenecks, and answer staff questions from live data. It orchestrates the other scenarios; it doesn't replace them.

## Flow

```mermaid
flowchart TD
    A[Every 5 min] --> B[Read active work orders<br/>status not Closed / Cancelled / Paid]
    B --> C[Rules: phase, SLAs, timers, exceptions]
    C --> D[AI: prioritize + write next actions]
    D --> E[Update next_action, owner, due]
    E --> F{High priority?}
    F -- yes --> G[Notify owner now]
    F -- no --> H[Add to daily queue]
```

## Capabilities

| Capability | How |
|-----------|-----|
| Next action per work order | Rules decide what is overdue; AI writes the action and reason |
| SLA monitoring | Targets from `config/business_rules.yaml` |
| Daily priority queue (7 AM) | High: emergencies, approvals > 48 h, callbacks today. Medium: waiting on tenant or parts. Low: invoice follow-ups, warranty expirations. |
| Staff chat | "Which jobs need dispatch today?" "What's waiting on PM approval?" "Which invoices are overdue?" The AI answers from a filtered Sheets query, never from memory. |
| Recommendations | e.g. "ABC averages 72 h approvals; send their estimates before noon." |
| Daily summary (6 PM) | Received, completed, pending approval, emergencies, revenue, outstanding, response time, FVR, callback rate, alerts |
| Pattern log | Repeat issues at the same property, frequently replaced parts, seasonal trends, slow-paying clients |

## Guardrails

- The coordinator **recommends and notifies**. It does not approve estimates, change prices, or close work orders.
- Every AI statement must cite a work order and a field value; the prompt forbids inventing facts.
- Tenant personal data stays out of Slack summaries (use record ID and address only).

## Test checklist

- [ ] An approved repair with no technician appears as high priority within 5 minutes.
- [ ] A chat question returns the same list as a manual filter on the sheet.
- [ ] Daily summary numbers match Scenario 11.
