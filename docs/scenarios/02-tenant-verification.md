# Scenario 2 — Tenant Verification & PM Company Linking

| | |
|---|---|
| **n8n workflow** | `Maintenance Ops · Work Order Lifecycle` → intake branch, after the row is appended (`S02`) |
| **Trigger** | None of its own: continues from Scenario 1 in the same execution |
| **Exit status** | `Customer Verified` |
| **Systems** | Google Sheets, Housecall Pro |
| **Rules** | WO-1, WO-2 |

## Objective

Find or create the tenant as a Housecall Pro customer and attach the PM company relationship in **dedicated custom fields**, so billing and approvals can route on them later.

## Flow

```mermaid
flowchart TD
    A[From Scenario 1: row appended] --> B[Search PM Companies]
    B --> C{PM company found and active?}
    C -- no --> X[Exception: unknown PM company → Operations]
    C -- yes --> D[HCP: search customer<br/>phone → email → name + address]
    D --> E{Customer exists?}
    E -- yes --> F[HCP: update contact details + custom fields]
    E -- no --> G[HCP: create customer + custom fields]
    F --> H[Sheets: save hcp_customer_id, status Customer Verified]
    G --> H
```

## n8n nodes

Housecall Pro has no built-in n8n node, so every Housecall Pro call is an **HTTP Request** node using a shared **Header Auth** credential (`Authorization: Token {{HOUSECALL_PRO_API_KEY}}`). API access depends on your Housecall Pro plan; check it before building.

| # | Node | Configuration |
|---|------|---------------|
| 1 | **Google Sheets → Get Row(s)** | `pm_companies` where `pm_company_id` = the work order's. |
| 2 | **IF** · PM company active? | False → append to `exceptions` (`Unknown PM company`) and stop this branch. |
| 3 | **HTTP Request** · HCP search customers | `GET /customers?q={{tenant_phone}}`; if empty, retry with email, then name + address (three requests chained through IF nodes, or one **Code** node that tries each). |
| 4 | **IF** · customer found? | — |
| 5a | **HTTP Request** · HCP update customer | Phone, email, address + custom fields `PM Company`, `PM Company ID`, `Billing Account`, `Work Order Source`. |
| 5b | **HTTP Request** · HCP create customer | Same fields. |
| 6 | **Merge** (append) | Joins both routes. |
| 7 | **Google Sheets → Update Row** | `hcp_customer_id`, `status` = `Customer Verified`; append `status_history` (and `customers` on 5b). |

## Data structure in Housecall Pro

Use custom fields, not notes:

```text
❌ Notes: "PM Company - ABC Management"

✅ Customer:  John Smith
   Address:   123 Main St, Unit 204
   Custom fields:
     PM Company:      ABC Property Management
     PM Company ID:   PM001
     Billing Account: ABC-001
```

## Test checklist

- [ ] Existing tenant (same phone) is updated, not duplicated.
- [ ] New tenant is created with all PM custom fields filled.
- [ ] Work order row has `hcp_customer_id` and status `Customer Verified`.
- [ ] A work order from an unknown PM company creates an exception and stops.
