# ADR-001: One budget decision rule, based on the client price vs. the NTE limit

**Status:** Accepted

## Context

The original design described the "AI Budget Decision Engine" two different ways:

- Version A (Phase 8, first Scenario 6): compare **total internal cost** with the **internal budget limit** ($150).
- Version B (second Scenario 6): compare the **client unit price** with the **PM maintenance limit** ($120).

The examples were also inconsistent (the same $75 + $120 + $45 assessment was shown as both $240 and $125 internal cost). Two rules applied to the same visit can disagree: a $140 internal cost passes a $150 internal limit while its $190 client price breaks a $120 NTE. The technician would repair a job the PM never authorized.

## Decision

1. The **primary rule** compares what the PM will be billed (client price) with what the PM authorized (NTE). That is the commitment that actually binds the vendor.
2. An **optional internal cap** (`decision.internal_budget_limit`) can further restrict same-visit repairs, for example for new technicians. It can only make the rule stricter, never looser.
3. The NTE limit resolves in order: work order → PM company default → global default.
4. The decision is computed by code (`maintenance_ops.pricing.decide`), not by the AI. The AI step in Scenario 6 only validates and summarizes the technician's submission.

## Consequences

- The PM is never billed above their NTE without written approval.
- Different PM companies can have different limits without changing any scenario.
- The tests in `tests/test_pricing.py` pin the behavior, including the equal-to-NTE edge case (allowed).
