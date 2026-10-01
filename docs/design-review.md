# Design Review: What Changed From the Original Design

The original design document described the full lifecycle well. Turning it into a buildable, testable system surfaced a few contradictions and gaps. This page records each one and how it was resolved.

## Contradictions resolved

| # | In the original | Problem | Resolution |
|---|-----------------|---------|------------|
| 1 | Two different "Scenario 6" sections | One compared internal cost to a $150 internal limit; the other compared client price to a $120 PM limit | Merged into one Scenario 6 with one rule: client price vs. NTE, plus an optional internal cap. See [ADR-001](decisions/ADR-001-budget-decision-rule.md). |
| 2 | Same assessment ($75 + $120 + $45) shown as $240 and as $125 internal cost | Example numbers didn't add up | All examples recomputed by the code and pinned in tests. |
| 3 | "Assessment fee will not be billed separately" vs. invoice example $325 − $75 = $250 | Fee counted twice; profit example ($85) only matches the first | Default `waive` mode; `deduct` mode available if the fee is billed at the visit. See [ADR-002](decisions/ADR-002-assessment-fee-credit.md). |
| 4 | Budget limit $150 in one place, $120 in another | Unclear which applies | NTE resolves work order → PM company → global default ($120). |
| 5 | Two scenario lists (18 items and 14 items) with different numbering | Hard to follow and build | One list of 14 scenarios. Old items 1–2 merged into Scenario 1; "Internal Review" folded into Scenario 3; "Technician Dispatch" and "Repair Scheduling" merged into Scenario 8. |
| 6 | Status names varied ("New", "New Work Order", "Ready for Assessment Dispatch" set by both Scenario 3 and 4) | Scenarios trigger on exact strings | Canonical statuses and allowed transitions in [`config/status_lifecycle.yaml`](../config/status_lifecycle.yaml), enforced by `status.transition()`. |
| 7 | Technician assessment dispatch included the budget limit | Technicians shouldn't see client money; the system decides | Removed from the technician view. The decision engine tells the technician "repair now" or "stop after assessment". |
| 8 | Estimate title shown as `WO-45891 \| Plumbing Repair Assessment` and `WO#45891 - Plumbing Assessment - 123 Main St` | Two formats | One format: `WO-45891 - Plumbing Assessment - 123 Main St`. |

## Gaps filled

| # | Gap | Added |
|---|-----|-------|
| 1 | Scenario 7 (PM approval) was referenced but never written | Full [Scenario 7 spec](scenarios/07-pm-approval.md): approval package, follow-ups, owner approval, decline path |
| 2 | Same-visit repairs skipped QA and tenant sign-off | Same-visit repairs now enter Scenario 9 like any other repair |
| 3 | No duplicate protection on intake | Idempotency check on PM company + PM WO # |
| 4 | Two PM companies could share a work order number | Internal `record_id` key |
| 5 | Time-based KPIs read from overwritten cells | Append-only Status History sheet |
| 6 | AI output written straight to the database | JSON schema + validation; missing data → **Needs More Info** |
| 7 | No error handling per module | Error routes log to Exceptions and alert Operations |
| 8 | Scenario 11 pulled from GoHighLevel, which wasn't in the stack | Listed as optional in the tech stack |
| 9 | Emergency path only in Scenario 12 | Emergencies flagged at intake and pushed immediately |

## Kept exactly as designed

The three-audience separation, the initial-estimate-first rule, updating the same estimate after assessment, the PM WO # traveling to the invoice, the approval timeline (20 min / 24 h / 48 h), technician continuity for repairs, payment follow-ups (15 / 30 / 45 days), and the AI coordinator and knowledge base layers.
