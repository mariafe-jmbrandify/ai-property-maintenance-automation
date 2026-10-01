# ADR-002: The assessment fee is waived on approval, billed alone on decline

**Status:** Accepted

## Context

The original design promised the PM that the assessment fee "will be credited toward the total repair cost and will not be billed separately", but the billing example then subtracted it from the repair price ($325 − $75 = $250 due). Both cannot be true:

- If the client price already includes the assessment fee (it does: internal cost = fee + labor + materials, then markup), subtracting it again gives the fee away twice. Gross profit on the example would drop from $85 to $10.
- Subtracting only makes sense if the fee was already invoiced at the assessment visit.

## Decision

`pricing.assessment_credit_mode` supports both models, with **`waive` as the default**:

| Mode | When to use | Approved repair invoice | Declined estimate |
|------|-------------|-------------------------|-------------------|
| `waive` (default) | Fee is not invoiced at the visit | Repair price; fee line shown as "credited, not billed" at $0 | Assessment fee only |
| `deduct` | Fee is invoiced at the visit | Repair price minus the fee already paid | Assessment fee only |

## Consequences

- The estimate disclaimer matches what the invoice actually does.
- Profit reporting is correct in both modes (`tests/test_billing.py`).
