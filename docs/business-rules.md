# Business Rules

Values below are defaults from [`config/business_rules.yaml`](../config/business_rules.yaml). Change the YAML, not the scenarios.

## 1. Work orders

| # | Rule |
|---|------|
| WO-1 | Every work order must be linked to a **PM company**, a **tenant**, a **property address**, and a **PM Work Order #**. |
| WO-2 | PM company data lives in dedicated fields (customer custom fields in Housecall Pro, columns in Sheets), never in notes. |
| WO-3 | A work order with missing required data is set to **Needs More Info** and assigned to Operations. It does not continue on guesses. |
| WO-4 | A duplicate email for the same PM company + PM Work Order # updates the existing record instead of creating a new one. |

## 2. Estimates

| # | Rule |
|---|------|
| EST-1 | Every new work order gets an **Initial Assessment Estimate** in Housecall Pro before any visit. It is not the repair price. |
| EST-2 | Estimate title format: `{PM WO #} - {Trade} Assessment - {Address}`, e.g. `WO-45891 - Plumbing Assessment - 123 Main St`. |
| EST-3 | After the assessment, the **same estimate is updated**. A new estimate is never created for the same work order. |
| EST-4 | The estimate converts to a job, and the job to an invoice, so the PM WO # carries through. |

## 3. Pricing

| # | Rule | Default |
|---|------|---------|
| PR-1 | Internal cost = assessment fee cost + labor + materials | — |
| PR-2 | Client price = internal cost ÷ (1 − target margin). Internal cost is 50% of the price, gross profit is the other 50%. | 50% margin (= 100% markup, price = 2 × cost) |
| PR-3 | Client prices round **up** to the nearest increment | $5 |
| PR-4 | Only the client price is shown to the PM company | — |
| PR-5 | Margin is measured on the price, markup on the cost. Always quote and report **margin**: 50% margin = 100% markup; 35% markup = 26% margin. | — |

## 4. Budget decision (NTE)

See [ADR-001](decisions/ADR-001-budget-decision-rule.md).

| # | Rule |
|---|------|
| NTE-1 | The NTE limit comes from the work order; if absent, from the PM company profile; if absent, the global default ($120). |
| NTE-2 | If **client price ≤ NTE** (and internal cost ≤ the optional internal cap), the technician completes the repair during the assessment visit. |
| NTE-3 | Otherwise the technician stops after the assessment. The client estimate goes to the PM for approval. |
| NTE-4 | Emergencies follow the PM company's emergency rules (stored in `pm_companies`); the technician makes the property safe first. |

## 5. Assessment fee

See [ADR-002](decisions/ADR-002-assessment-fee-credit.md).

| # | Rule |
|---|------|
| FEE-1 | If the repair is approved, the assessment fee is credited: it is not billed separately. |
| FEE-2 | If the estimate is declined, only the assessment fee is invoiced: $150 default ($75 visit cost at a 50% margin). |
| FEE-3 | Client estimates carry the disclaimer: *"If this estimate is approved and the repair is authorized, the assessment fee will be credited toward the total repair cost and will not be billed separately. If the estimate is declined, only the assessment fee will be invoiced."* |

## 6. Follow-ups and timers

| Waiting on | Step 1 | Step 2 | Step 3 |
|-----------|--------|--------|--------|
| PM approval | 20 min: initial follow-up | 24 h: reminder | 48 h: escalate → Approval Delayed |
| Owner approval (when the PM requires it) | Reminders every 24 h | — | 48 h max, then escalate |
| Tenant response | 24 h: reminder SMS | 48 h: notify admin + escalate to PM | — |
| Technician accepting a dispatch | 15 min: offer to next technician | No one accepts: alert dispatcher | — |
| Invoice payment | 15 days: reminder | 30 days: escalate to accounting | 45 days: collections review |

## 7. Service levels (SLAs)

| Stage | Target |
|-------|--------|
| First tenant contact after intake | 15 minutes |
| Initial estimate created | 30 minutes |
| Assessment scheduled | 24 hours |
| PM approval follow-up | Every 24 hours |
| Invoice generated after closure | Same business day (8 h) |

## 8. Dispatch

| # | Rule |
|---|------|
| DIS-1 | A technician is dispatched only when the tenant confirmed service, gave availability and entry instructions, the estimate exists, and the HCP customer exists. |
| DIS-2 | Match on trade, service area, available day, and capacity. Rank by exact trade match, lightest workload, then rating. |
| DIS-3 | For repairs, prefer the technician who did the assessment. |
| DIS-4 | Technician messages never include the PM company, PM WO #, or any pricing. |

## 9. Quality and closure

| # | Rule |
|---|------|
| QA-1 | A job cannot close without findings, action taken, repair completed, materials, before **and** after photos, and technician remarks. |
| QA-2 | Same-visit repairs go through the same QA and tenant sign-off as scheduled repairs. |
| QA-3 | If the tenant reports the issue remains, a callback job is created and linked to the original job. |
