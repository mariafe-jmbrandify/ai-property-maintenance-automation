# Scenario 6 — Assessment, Pricing & Budget Decision

| | |
|---|---|
| **Make.com name** | `06 - Assessment Pricing Decision` |
| **Trigger** | Technician submits the assessment form (webhook), or HCP estimate visit marked complete |
| **Exit status** | `Repair Completed` (same visit) or `Pending PM Approval` |
| **Systems** | Form (HCP checklist, Jotform, or Typeform), HCP, Google Sheets, Google Drive |
| **Rules** | PR-1 to PR-4, NTE-1 to NTE-4, EST-3, FEE-3 |
| **Code** | `maintenance_ops.pricing.decide`, `maintenance_ops.visibility.client_view` |
| **Decision record** | [ADR-001](../decisions/ADR-001-budget-decision-rule.md) |

## Objective

Collect the technician's assessment, calculate internal cost and client price, and decide in real time, while the technician is still on site, whether to **repair now** or **stop and request approval**. Keep internal costs away from the PM.

> This merges the two "Scenario 6" sections of the original design into one rule. See the [design review](../design-review.md).

## Flow

```mermaid
flowchart TD
    A[Technician submits assessment] --> B{All required fields + photos?}
    B -- no --> C[Return to technician with what's missing]
    B -- yes --> D[Internal cost = fee + labor + materials]
    D --> E[Client price = cost × 1.35, round up to $5]
    E --> F[Resolve NTE: work order → PM company → default]
    F --> G{Client price ≤ NTE<br/>and cost ≤ internal cap?}
    G -- yes --> H[Reply to technician: REPAIR NOW]
    H --> I[Technician completes repair + completion report]
    I --> J[HCP: update estimate → convert to job]
    J --> K[Status: Repair Completed → Scenario 9]
    G -- no --> L[Reply to technician: STOP after assessment]
    L --> M[HCP: update SAME estimate with scope + client price]
    M --> N[Status: Pending PM Approval → Scenario 7]
```

## Technician submission

Schema: [`prompts/schemas/assessment.schema.json`](../../prompts/schemas/assessment.schema.json).

| Field | Example |
|-------|---------|
| Estimate | EST-10001 |
| Findings | Braided supply line under the kitchen sink is corroded and actively leaking. |
| Troubleshooting | Verified water source · checked shut-off valve · pressure-tested line |
| Root cause | Corroded braided supply line |
| Recommendation | Replace supply line and compression fittings |
| Scope of work | Remove damaged line · install new line and fittings · pressure test · verify no leaks · clean area |
| Assessment fee cost (internal) | $75 |
| Labor (internal) | $120 |
| Materials (internal) | $45 |
| Photos | Before, during |

## Modules

| # | Module | Configuration |
|---|--------|---------------|
| 1 | **Webhooks → Custom webhook** | Receives the form submission |
| 2 | **Filter / Router** | Required fields present (schema `required`) and ≥ 1 photo. Else → SMS technician with missing items; stop. |
| 3 | Sheets → Search Rows | Work order by `estimate_id`; PM company for `default_nte_limit` |
| 4 | **HTTP → Make a request** to the rules engine (`python -m maintenance_ops.server`) | `POST /decide` with `assessment_fee`, `labor`, `materials`, `nte_limit`, `pm_default_nte`. Returns `outcome`, `internal_total`, `client_price`, `over_by`, `next_status`. |
| 5 | Sheets → Add a Row (`assessments`) | All costs (internal), `client_price`, `markup_pct` |
| 6 | **Twilio / WhatsApp → technician** | "REPAIR NOW – within approved limit" or "STOP after assessment – approval needed". No dollar amounts. |
| 7A | Within NTE: wait for completion report (same form, `repair_completed_onsite` = true), then HCP **update estimate → convert to job → mark complete** | — |
| 7B | Over NTE: HCP **update estimate** (same ID): findings, recommendation, scope, photos, one line "{{trade}} repair" at `client_price`, disclaimer | — |
| 8 | Sheets → Update a Row | `internal_cost_total`, `client_price`, `decision`, `status`, `first_visit_resolution` (Yes on 7A); append `status_history` |
| 9 | Over NTE only: notify Operations | Estimate #, PM WO #, client price, NTE, amount over, recommendation |

If you prefer not to host the rules engine, module 4 can be a Make **Tools → Set multiple variables** module:
`internal_total = fee + labor + materials` · `client_price = ceil(internal_total * 1.35 / 5) * 5` · `within = client_price <= nte`.
Keep the numbers in sync with `config/business_rules.yaml`.

## Worked examples

| | Within NTE | Over NTE |
|---|---|---|
| Internal cost | $75 + $60 + $25 = $160 | $75 + $120 + $45 = $240 |
| Client price | $216 → $220 | $324 → $325 |
| NTE | $250 | $120 |
| Outcome | Repair now | Approval required (over by $205) |

## Client estimate (what the PM sees)

```text
Estimate #: EST-10001
PM Work Order #: WO-45891
Property: 123 Main St, Unit 204 · Tenant: John Smith
Service: Plumbing repair

Assessment findings
The braided supply line beneath the kitchen sink has failed due to corrosion.

Recommended repair
• Replace braided supply line  • Replace compression fittings
• Pressure test plumbing       • Verify no additional leaks  • Clean work area

Plumbing repair ............................................ $325.00
Total ...................................................... $325.00

Assessment fee credit: If this estimate is approved and the repair is authorized, the
assessment fee will be credited toward the total repair cost and will not be billed
separately. If the estimate is declined, only the assessment fee will be invoiced.
```

**Never shown to the PM:** assessment fee cost, labor, materials, internal total, markup, technician pay, margin.

## Test checklist

- [ ] Incomplete form (no photos) is returned to the technician.
- [ ] $160 internal / $250 NTE → "REPAIR NOW"; status ends `Repair Completed`; `first_visit_resolution` = Yes.
- [ ] $240 internal / $120 NTE → "STOP"; same estimate ID updated to $325; status `Pending PM Approval`.
- [ ] A client price exactly equal to the NTE is treated as within the limit.
- [ ] The PM-facing estimate passes `leaked_fields() == []`.
- [ ] No new estimate is created in HCP.
