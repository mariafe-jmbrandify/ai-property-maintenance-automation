# Scenario Index

Scenarios are the business stages. In n8n, Scenarios 1–10 live in **one main workflow** (`Maintenance Ops · Work Order Lifecycle`): an intake branch plus an event router whose Switch sends each incoming event to its branch. Scenarios 11–14 are separate always-on workflows. See [n8n/README.md](../../n8n/README.md).

| # | Scenario | n8n workflow · starts on | Exit status | Code |
|---|----------|--------------------------|-------------|------|
| 1 | [Work Order Intake & AI Extraction](01-work-order-intake.md) | Main · **Gmail Trigger** | New Work Order · Needs More Info | `extraction` |
| 2 | [Tenant Verification & PM Company Linking](02-tenant-verification.md) | Main · continues from S01 | Customer Verified | — |
| 3 | [Initial Assessment Estimate & Internal Review](03-initial-estimate.md) | Main · continues from S02 | Awaiting Tenant Confirmation | `extraction.estimate_title` |
| 4 | [Tenant Confirmation & Discovery](04-tenant-confirmation.md) | Main · end of intake; replies on `/events/sms` | Ready for Assessment Dispatch | — |
| 5 | [Assessment Dispatch](05-assessment-dispatch.md) | Main · continues from S04 | Assessment Scheduled | `dispatch` |
| 6 | [Assessment, Pricing & Budget Decision](06-assessment-budget-decision.md) | Main · `/events/assessment_submitted` | Repair Completed · Pending PM Approval | `pricing`, `visibility` |
| 7 | [PM Approval & Owner Authorization](07-pm-approval.md) | Main · `/events/pm_reply` + Gmail Trigger | Repair Approved · Estimate Declined | `followups` |
| 8 | [Repair Scheduling & Dispatch](08-repair-scheduling.md) | Main · after S07 approved or S09 callback | Repair Scheduled | `dispatch` |
| 9 | [Completion, QA & Tenant Sign-off](09-completion-qa.md) | Main · `/events/job_completed`, `/events/sms` | Ready for Invoice · Callback Required | — |
| 10 | [Billing, Technician Pay & Reconciliation](10-billing-reconciliation.md) | Main · after S09 fixed or S07 declined | Invoiced → Closed | `billing` |
| 11 | [KPI Dashboard & Management Reporting](11-kpi-dashboard.md) | KPI Report · Schedule Trigger | — | `kpis` |
| 12 | [Exception Handling & Escalation](12-exception-handling.md) | Exception Monitor · every 10 min | Hold → normal flow | `followups` |
| 13 | [AI Operations Coordinator](13-ai-operations-coordinator.md) | Coordinator · Schedule + Slack Trigger | — | `followups` |
| 14 | [AI Knowledge Base & SOP Assistant](14-ai-knowledge-base.md) | SOP Assistant · Chat Trigger | — | — |

## Every scenario spec contains

Trigger and exit status · flow diagram · n8n nodes with configuration · data written · message templates · test checklist.

## Mapping from the original design

| Original | Now |
|----------|-----|
| Phase 1 Intake + Scenario 1 Email Intake + Scenario 2 AI Extraction | Scenario 1 |
| Phase 2 / Scenario 3 Tenant Verification | Scenario 2 |
| Phase 3 Initial Estimate + Phase 4 Internal Review | Scenario 3 |
| Phase 5 Tenant Confirmation | Scenario 4 |
| Phase 6 Assessment Appointment | Scenario 5 |
| Phase 7–8 + both "Scenario 6" sections | Scenario 6 |
| Phase 9 PM Approval (Scenario 7, not written) | Scenario 7 (new) |
| Phase 10 + Repair Scheduling + Technician Dispatch | Scenario 8 |
| Phase 11–12 Completion + QA | Scenario 9 |
| Phase 13 Billing | Scenario 10 |
| Phase 14 Reporting | Scenario 11 |
| Exception Handling | Scenario 12 |
| AI Operations Coordinator | Scenario 13 |
| AI Knowledge Base Assistant | Scenario 14 |
