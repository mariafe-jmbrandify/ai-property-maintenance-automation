"""Internal costing, client pricing, and the budget decision engine (Scenario 6).

Decision rule (see docs/decisions/ADR-001-budget-decision-rule.md):

    client_price = round_up(internal_total * (1 + markup), round_up_to)

    Same-visit repair is authorized when
        client_price <= NTE limit
        AND (internal_budget_limit is not set OR internal_total <= internal_budget_limit)

    Otherwise the technician stops after the assessment and the client
    estimate is routed to PM approval (Scenario 7).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from .config import business_rules

WITHIN_LIMIT = "WITHIN_LIMIT"
APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


def _money(value: Any) -> Decimal:
    if value is None or value == "":
        return Decimal("0")
    if isinstance(value, str):
        value = value.replace("$", "").replace(",", "").strip()
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class InternalCost:
    assessment_fee: Decimal
    labor: Decimal
    materials: Decimal

    @property
    def total(self) -> Decimal:
        return self.assessment_fee + self.labor + self.materials

    @classmethod
    def from_values(cls, assessment_fee: Any, labor: Any, materials: Any) -> "InternalCost":
        parts = [_money(assessment_fee), _money(labor), _money(materials)]
        if any(p < 0 for p in parts):
            raise ValueError("Costs cannot be negative")
        return cls(*parts)


def client_price(internal_total: Any, markup_pct: float | None = None, round_up_to: int | None = None) -> Decimal:
    """Apply the company markup and round UP to the configured increment."""
    rules = business_rules()["pricing"]
    markup = Decimal(str(rules["markup_pct"] if markup_pct is None else markup_pct)) / 100
    step = int(rules["round_up_to"] if round_up_to is None else round_up_to)
    raw = _money(internal_total) * (1 + markup)
    if step <= 1:
        return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(math.ceil(raw / step) * step).quantize(Decimal("0.01"))


def resolve_nte(work_order_limit: Any = None, pm_company_default: Any = None) -> Decimal:
    """Work-order NTE wins, then the PM company default, then the global default."""
    for candidate in (work_order_limit, pm_company_default):
        if candidate not in (None, ""):
            return _money(candidate)
    return _money(business_rules()["decision"]["default_nte_limit"])


@dataclass(frozen=True)
class BudgetDecision:
    outcome: str
    internal_total: Decimal
    client_price: Decimal
    nte_limit: Decimal
    over_by: Decimal
    reason: str

    @property
    def same_visit_repair(self) -> bool:
        return self.outcome == WITHIN_LIMIT

    @property
    def next_status(self) -> str:
        return "Repair Completed" if self.same_visit_repair else "Pending PM Approval"


def decide(cost: InternalCost, nte_limit: Any, internal_budget_limit: Any = "config", markup_pct: float | None = None) -> BudgetDecision:
    """Run the budget decision engine for one assessment."""
    if internal_budget_limit == "config":
        internal_budget_limit = business_rules()["decision"]["internal_budget_limit"]
    nte = _money(nte_limit)
    price = client_price(cost.total, markup_pct=markup_pct)

    if price > nte:
        return BudgetDecision(APPROVAL_REQUIRED, cost.total, price, nte, price - nte,
                              f"Client price ${price} exceeds the ${nte} NTE limit")
    if internal_budget_limit is not None and cost.total > _money(internal_budget_limit):
        cap = _money(internal_budget_limit)
        return BudgetDecision(APPROVAL_REQUIRED, cost.total, price, nte, Decimal("0.00"),
                              f"Internal cost ${cost.total} exceeds the ${cap} internal budget limit")
    return BudgetDecision(WITHIN_LIMIT, cost.total, price, nte, Decimal("0.00"),
                          f"Client price ${price} is within the ${nte} NTE limit")
