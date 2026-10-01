from decimal import Decimal

import pytest

from maintenance_ops.pricing import (APPROVAL_REQUIRED, WITHIN_LIMIT, InternalCost, client_price, decide,
                                     markup_to_margin, resolve_nte)


def test_internal_cost_total():
    assert InternalCost.from_values(75, 120, 45).total == Decimal("240.00")


def test_internal_cost_accepts_currency_strings():
    assert InternalCost.from_values("$75", "1,200", "45.50").total == Decimal("1320.50")


def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        InternalCost.from_values(75, -1, 0)


def test_client_price_targets_50_percent_margin():
    # 50% margin: cost is half the price, so 240 -> 480 (a 100% markup)
    assert client_price(240) == Decimal("480.00")


def test_client_price_rounds_up_to_5():
    # 163 / 0.5 = 326 -> 330
    assert client_price(163) == Decimal("330.00")


def test_client_price_exact_multiple_not_bumped():
    assert client_price(100) == Decimal("200.00")


def test_client_price_other_margin_without_rounding():
    assert client_price(325, margin_pct=30, round_up_to=1) == Decimal("464.29")


def test_margin_of_100_percent_rejected():
    with pytest.raises(ValueError):
        client_price(100, margin_pct=100)


def test_markup_vs_margin():
    assert markup_to_margin(100) == Decimal("50.0")
    assert markup_to_margin(35) == Decimal("25.9")


def test_over_nte_requires_approval():
    d = decide(InternalCost.from_values(75, 120, 45), nte_limit=120)
    assert d.outcome == APPROVAL_REQUIRED
    assert d.client_price == Decimal("480.00")
    assert d.over_by == Decimal("360.00")
    assert d.next_status == "Pending PM Approval"


def test_within_nte_authorizes_same_visit_repair():
    d = decide(InternalCost.from_values(75, 60, 25), nte_limit=350)
    assert d.client_price == Decimal("320.00")
    assert d.outcome == WITHIN_LIMIT
    assert d.same_visit_repair
    assert d.next_status == "Repair Completed"


def test_price_equal_to_nte_is_within_limit():
    d = decide(InternalCost.from_values(0, 100, 0), nte_limit=200)
    assert d.outcome == WITHIN_LIMIT


def test_internal_budget_cap_can_force_approval():
    d = decide(InternalCost.from_values(75, 60, 25), nte_limit=1000, internal_budget_limit=150)
    assert d.outcome == APPROVAL_REQUIRED
    assert "internal budget" in d.reason


def test_nte_resolution_order():
    assert resolve_nte("200", 150) == Decimal("200.00")
    assert resolve_nte(None, 150) == Decimal("150.00")
    assert resolve_nte(None, None) == Decimal("120.00")
