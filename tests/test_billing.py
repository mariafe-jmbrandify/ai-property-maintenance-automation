from datetime import date
from decimal import Decimal

from maintenance_ops.billing import build_invoice, job_financials, payment_follow_up


def test_approved_repair_waives_assessment_fee():
    inv = build_invoice(approved=True, client_price=480)
    assert inv.invoice_type == "repair"
    assert inv.total == Decimal("480.00")
    fin = job_financials(inv, 240)
    assert fin.gross_profit == Decimal("240.00")
    assert fin.gross_margin_pct == Decimal("50.0")


def test_deduct_mode_subtracts_prebilled_fee():
    inv = build_invoice(approved=True, client_price=480, credit_mode="deduct")
    assert inv.total == Decimal("330.00")


def test_declined_estimate_bills_assessment_only():
    inv = build_invoice(approved=False, client_price=950)
    assert inv.invoice_type == "assessment_only"
    assert inv.total == Decimal("150.00")
    assert job_financials(inv, 75).gross_margin_pct == Decimal("50.0")


def test_payment_follow_up_schedule():
    sent = date(2026, 7, 1)
    assert payment_follow_up(sent, date(2026, 7, 10)) is None
    assert payment_follow_up(sent, date(2026, 7, 16)) == "Send Payment Reminder"
    assert payment_follow_up(sent, date(2026, 7, 31)) == "Escalate to Accounting"
    assert payment_follow_up(sent, date(2026, 8, 15)) == "Collections Review Required"
    assert payment_follow_up(sent, date(2026, 8, 15), paid=True) is None
