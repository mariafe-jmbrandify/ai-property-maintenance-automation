"""KPI calculations for the operations dashboard (Scenario 11)."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from statistics import mean
from typing import Any, Iterable, Mapping

from .pricing import _money


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator * 100, 1) if denominator else 0.0


def _hours(start: datetime | None, end: datetime | None) -> float | None:
    if not start or not end:
        return None
    return (end - start).total_seconds() / 3600


def first_visit_resolution_rate(orders: Iterable[Mapping[str, Any]]) -> float:
    done = [o for o in orders if o.get("repair_completed_at")]
    return _rate(sum(1 for o in done if o.get("first_visit_resolution")), len(done))


def callback_rate(orders: Iterable[Mapping[str, Any]]) -> float:
    done = [o for o in orders if o.get("repair_completed_at")]
    return _rate(sum(1 for o in done if o.get("callback_required")), len(done))


def average_hours(orders: Iterable[Mapping[str, Any]], start_field: str, end_field: str) -> float | None:
    values = [h for o in orders if (h := _hours(o.get(start_field), o.get(end_field))) is not None]
    return round(mean(values), 1) if values else None


def revenue_by_pm_company(orders: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Decimal | int]]:
    out: dict[str, dict[str, Decimal | int]] = defaultdict(lambda: {"jobs": 0, "revenue": Decimal("0"), "gross_profit": Decimal("0")})
    for o in orders:
        if not o.get("invoice_total"):
            continue
        row = out[o.get("pm_company_name", "Unknown")]
        row["jobs"] += 1
        row["revenue"] += _money(o["invoice_total"])
        row["gross_profit"] += _money(o["invoice_total"]) - _money(o.get("internal_cost_total"))
    return dict(out)
