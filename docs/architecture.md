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

    subgraph Orchestration["n8n · main workflow + 4 always-on workflows"]
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

## Orchestration in n8n

Decision record: [ADR-004](decisions/ADR-004-n8n-orchestrator.md).

| Workflow | Triggers | Scenarios |
|----------|----------|-----------|
| `Maintenance Ops · Work Order Lifecycle` (main) | Gmail Trigger (new work orders), Webhook `POST /events/:event`, Gmail Trigger (approval replies) | 1–10 |
| `Maintenance Ops · Exception Monitor` | Schedule Trigger every 10 min + daily 08:00 | 12 (and 7/10 follow-up timers) |
| `Maintenance Ops · KPI Report` | Schedule Trigger daily 06:00, Monday 07:00 | 11 |
| `Maintenance Ops · Coordinator` | Schedule Trigger + Slack Trigger | 13 |
| `Maintenance Ops · SOP Assistant` | Chat Trigger | 14 |

### Event router

Everything that happens *after* intake arrives as an event on one webhook. The Switch node sends it to its branch; the branch loads the work order from Google Sheets, acts, and writes the new status back. No execution sits waiting for days, so every branch is short, easy to debug and safe to re-run.

```mermaid
flowchart LR
    TW[Twilio inbound SMS / WhatsApp] -->|/events/sms| WH[Webhook<br/>POST /events/:event]
    FORM[Assessment form] -->|/events/assessment_submitted| WH
    HCP[Housecall Pro webhooks] -->|/events/pm_reply · job_completed · invoice_paid| WH
    WA[WhatsApp dispatch buttons] -->|/events/dispatch_reply| WH
    WH --> SW{Switch<br/>route by event}
    SW -->|sms| LK[Look up active WO by phone] --> ST{Switch by status}
    ST -->|awaiting confirmation| R2[tenant_reply · S04–05]
    ST -->|awaiting sign-off| R6[tenant_signoff · S09–10]
    SW -->|assessment_submitted| R3[S06 budget decision]
    SW -->|pm_reply| R4[S07 approval → S08 / S10]
    SW -->|job_completed| R5[S09 QA]
    SW -->|dispatch_reply| R7[resume S05 offer]
```

| Event | Sent by | Branch |
|-------|---------|--------|
| `sms` | Twilio inbound webhook (tenant texts) | Resolved by work order status → `tenant_reply` or `tenant_signoff` |
| `dispatch_reply` | WhatsApp quick-reply buttons | Resumes the waiting dispatch offer (Scenario 5) |
| `assessment_submitted` | Technician assessment form | Scenario 6 |
| `pm_reply` | Housecall Pro estimate approved / declined (email replies use a second Gmail Trigger into the same branch) | Scenario 7 |
| `job_completed` | Housecall Pro job completed or the completion form | Scenario 9 |
| `invoice_paid` | Housecall Pro invoice paid | Scenario 10 payment status |

Short in-run waits (a technician accepting within 15 minutes, a reviewer clicking Approve) use a **Wait** node set to *On Webhook Call*. Anything measured in hours or days (approvals, tenant replies, payments) is handled by the Exception Monitor reading timestamps from the sheet.

The rules engine (`python -m maintenance_ops.server`) is called with **HTTP Request** nodes (`/decide`, `/extraction`). Without it, the same formulas fit in **Code** nodes; keep them in sync with `config/business_rules.yaml`.

## Systems and their jobs

| System | Role | System of record for |
|--------|------|----------------------|
| PM platforms | Source of work orders; receive status updates | PM Work Order #, NTE limit, PM-side status |
| Gmail | Intake inbox, PM notifications | Original work order email |
| n8n | Orchestration: triggers, event routing, AI agents, retries | Execution history |
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
- **Error routes.** Every n8n node that calls an external API uses **On Error → Continue (using error output)**, wired to a node that logs to the Exceptions sheet and alerts Operations, and the workflows share an **Error Workflow**; nothing fails silently.
- **Human in the loop.** Missing data, failed QA, declined estimates, and anything the AI is unsure about route to a person with a clear next action.
