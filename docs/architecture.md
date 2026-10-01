# Architecture

## Goals

1. Every work order moves forward automatically until a human decision is actually needed.
2. Every work order always has a **status**, a **next action**, an **owner**, and a **due time**.
3. The PM Work Order # follows the job from intake to invoice.
4. Property managers, technicians, and the internal team each see only what they should.
5. Money and approvals follow written rules, not AI judgment.

## System context

```mermaid
flowchart TB
    subgraph Sources["Work order sources"]
        AF[AppFolio]
        PMe[Property Meld]
        RV[Rentvine]
        BU[Buildium]
    end

    subgraph Orchestration["Orchestration (Make.com or n8n)"]
        S1[1 Intake] --> S2[2 Verify] --> S3[3 Estimate] --> S4[4 Tenant] --> S5[5 Dispatch] --> S6[6 Assess & decide]
        S6 --> S7[7 PM approval] --> S8[8 Schedule repair] --> S9[9 QA]
        S6 -->|within NTE| S9
        S9 --> S10[10 Billing]
        S11[11 KPIs]:::bg
        S12[12 Exceptions]:::bg
        S13[13 AI coordinator]:::bg
        S14[14 Knowledge base]:::bg
    end

    Sources -->|email| S1
    S1 & S2 & S3 & S4 & S5 & S6 & S7 & S8 & S9 & S10 <--> DB[(Google Sheets)]
    S2 & S3 & S5 & S6 & S8 & S9 & S10 <--> HCP[Housecall Pro]
    S1 & S5 & S6 & S9 --> AI[OpenAI / Claude]
    S6 --> RE[Rules engine]
    S5 & S7 & S8 & S9 -->|API or browser automation| Sources

    classDef bg fill:#eef,stroke:#88a
```

## Systems and their jobs

| System | Role | System of record for |
|--------|------|----------------------|
| PM platforms | Source of work orders; receive status updates | PM Work Order #, NTE limit, PM-side status |
| Gmail | Intake inbox, PM notifications | Original work order email |
| Make.com / n8n | Orchestration, timers, routing | Scenario run history |
| AI (OpenAI / Claude) | Extraction, classification, tenant conversation, QA review, narrative reports | Nothing (stateless) |
| Rules engine | Pricing, NTE decision, status guard, visibility filters, SLA timers | Business rules (`config/`) |
| Google Sheets | Operations database and dashboard source | Status, timestamps, next action, KPIs |
| Housecall Pro | Field service CRM | Customers, estimates, jobs, invoices, schedule |
| Google Drive | Photo and document storage | Before / during / after photos |
| Twilio / WhatsApp | Tenant and technician messaging | Message delivery |

**Why Google Sheets in the middle?** See [ADR-003](decisions/ADR-003-google-sheets-operations-db.md). In short: every scenario can trigger on a status change, the team can see and correct data without new software, and it is easy to migrate to Airtable or Postgres later because the schema is documented in [data-model.md](data-model.md).

## The record that follows the job

```mermaid
flowchart LR
    PMC[PM Company<br/>PM001] --> WO[Work order<br/>WO-45891]
    WO --> C[HCP customer<br/>CUST-12345]
    C --> E[Estimate<br/>EST-10001]
    E --> J[Job<br/>JOB-20001]
    J --> I[Invoice<br/>INV-10001]
```

- `record_id` (e.g. `MO-2026-0001`) is our internal key. It prevents collisions when two PM companies use the same work order number.
- `pm_work_order_number` appears in the estimate title, on every PM message, and on the invoice.
- PM company details live in **dedicated fields**, never in free-text notes, so billing and approvals can route on them.

## Status lifecycle

The full list and allowed transitions live in [`config/status_lifecycle.yaml`](../config/status_lifecycle.yaml). Scenarios trigger on these exact strings.

```mermaid
stateDiagram-v2
    [*] --> NewWorkOrder: Scenario 1
    NewWorkOrder --> CustomerVerified: 2
    CustomerVerified --> AwaitingTenantConfirmation: 3
    CustomerVerified --> NeedsMoreInfo: 3 (admin review)
    NeedsMoreInfo --> AwaitingTenantConfirmation
    AwaitingTenantConfirmation --> ReadyForAssessmentDispatch: 4
    ReadyForAssessmentDispatch --> AssessmentScheduled: 5
    AssessmentScheduled --> PendingCostReview: 6
    PendingCostReview --> RepairCompleted: within NTE
    PendingCostReview --> PendingPMApproval: over NTE
    PendingPMApproval --> RepairApproved: 7
    PendingPMApproval --> AwaitingOwnerApproval: 7
    AwaitingOwnerApproval --> RepairApproved
    PendingPMApproval --> EstimateDeclined: 7
    AwaitingOwnerApproval --> EstimateDeclined
    RepairApproved --> RepairScheduled: 8
    RepairScheduled --> RepairCompleted: 9
    RepairCompleted --> QARevisionRequired: QA fails
    QARevisionRequired --> RepairCompleted
    RepairCompleted --> ReadyForTenantConfirmation: QA passes
    ReadyForTenantConfirmation --> CallbackRequired: issue remains
    CallbackRequired --> RepairScheduled
    ReadyForTenantConfirmation --> ReadyForInvoice: tenant confirms
    EstimateDeclined --> ReadyForInvoice: assessment invoice
    ReadyForInvoice --> Invoiced: 10
    Invoiced --> Closed
    Closed --> [*]
```

Hold states from Scenario 12 (`Waiting Tenant Response`, `Access Failed`, `Waiting Parts`, `Approval Delayed`, `Cancelled`) can interrupt the flow and return to it.

Every status change appends a row to the **Status History** sheet. KPIs such as approval time and response time are calculated from that history, not from overwritten cells.

## Audience views

| Data | PM company | Technician | Internal |
|------|:---:|:---:|:---:|
| PM Work Order #, PM company | ✅ | ❌ | ✅ |
| Estimate #, Job #, Invoice # | ✅ | ✅ (estimate/job) | ✅ |
| Address, unit, tenant name | ✅ | ✅ | ✅ |
| Tenant phone, entry instructions, pets | ❌ | ✅ | ✅ |
| Findings, scope of work, photos | ✅ | ✅ | ✅ |
| Client price / invoice total | ✅ | ❌ | ✅ |
| Assessment fee cost, labor, materials, markup, margin, technician pay | ❌ | ❌ | ✅ |

Implemented in [`visibility.py`](../src/maintenance_ops/visibility.py). Any outbound PM or technician message should pass `leaked_fields(payload) == []` before sending.

## Failure handling principles

- **Validate before write.** AI output is parsed against a JSON schema and validated before it reaches the database.
- **Idempotency.** Scenario 1 checks for an existing `pm_work_order_number` + `pm_company_id` before creating a row, so a re-sent email does not create a duplicate job.
- **Error routes.** Every Make.com module that calls an external API has an error handler that logs to the Exceptions sheet and alerts Operations; nothing fails silently.
- **Human in the loop.** Missing data, failed QA, declined estimates, and anything the AI is unsure about route to a person with a clear next action.
