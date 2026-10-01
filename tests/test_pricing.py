from decimal import Decimal

import pytest

from maintenance_ops.pricing import (APPROVAL_REQUIRED, WITHIN_LIMIT, InternalCost, client_price, decide,
                                     resolve_nte)


def test_internal_cost_total():
    assert InternalCost.from_values(75, 120, 45).total == Decimal("240.00")


def test_internal_cost_accepts_currency_strings():
    assert InternalCost.from_values("$75", "1,200", "45.50").total == Decimal("1320.50")


def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        InternalCost.from_values(75, -1, 0)


def test_client_price_applies_markup_and_rounds_up():
    # 240 * 1.35 = 324 -> rounded up to the next $5
    assert client_price(240) == Decimal("325.00")


def test_client_price_exact_multiple_not_bumped():
    assert client_price(100, markup_pct=50) == Decimal("150.00")


def test_client_price_without_rounding():
    assert client_price(325, markup_pct=30, round_up_to=1) == Decimal("422.50")


def test_over_nte_requires_approval():
    d = decide(InternalCost.from_values(75, 120, 45), nte_limit=120)
    assert d.outcome == APPROVAL_REQUIRED
    assert d.over_by == Decimal("205.00")
    assert d.next_status == "Pending PM Approval"


def test_within_nte_authorizes_same_visit_repair():
    d = decide(InternalCost.from_values(75, 60, 25), nte_limit=250)
    assert d.outcome == WITHIN_LIMIT
    assert d.same_visit_repair
    assert d.next_status == "Repair Completed"


def test_price_equal_to_nte_is_within_limit():
    d = decide(InternalCost.from_values(0, 100, 0), nte_limit=135, markup_pct=35)
    assert d.outcome == WITHIN_LIMIT


def test_internal_budget_cap_can_force_approval():
    d = decide(InternalCost.from_values(75, 60, 25), nte_limit=1000, internal_budget_limit=150)
    assert d.outcome == APPROVAL_REQUIRED
    assert "internal budget" in d.reason


def test_nte_resolution_order():
    assert resolve_nte("200", 150) == Decimal("200.00")
    assert resolve_nte(None, 150) == Decimal("150.00")
    assert resolve_nte(None, None) == Decimal("120.00")
