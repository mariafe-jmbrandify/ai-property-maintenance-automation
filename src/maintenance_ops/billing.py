"""Invoicing, assessment fee credit, profit, and payment follow-up (Scenario 10).

See docs/decisions/ADR-002-assessment-fee-credit.md for why the default
credit mode is "waive".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from .config import business_rules
from .pricing import _money


@dataclass(frozen=True)
class Invoice:
    invoice_type: str                 # "repair" or "assessment_only"
    lines: list[tuple[str, Decimal]] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return sum((amount for _, amount in self.lines), Decimal("0.00"))


def build_invoice(*, approved: bool, client_price: Any, service_label: str = "Repair",
                  credit_mode: str | None = None) -> Invoice:
    """Build the client-facing invoice. Internal costs never appear here."""
    rules = business_rules()["pricing"]
    fee = _money(rules["assessment_fee"]["client_price"])
    mode = credit_mode or rules["assessment_credit_mode"]

    if not approved:
        return Invoice("assessment_only", [("Assessment visit", fee)])

    price = _money(client_price)
    if mode == "deduct":
        return Invoice("repair", [(service_label, price), ("Assessment fee credit", -fee)])
    if mode == "waive":
        return Invoice("repair", [(service_label, price), ("Assessment fee (credited, not billed)", Decimal("0.00"))])
    raise ValueError(f"Unknown assessment_credit_mode: {mode}")


@dataclass(frozen=True)
class JobFinancials:
    invoice_total: Decimal
    technician_cost: Decimal
    gross_profit: Decimal
    gross_margin_pct: Decimal


def job_financials(invoice: Invoice, internal_total: Any) -> JobFinancials:
    cost = _money(internal_total)
    profit = invoice.total - cost
    margin = (profit / invoice.total * 100).quantize(Decimal("0.1")) if invoice.total else Decimal("0.0")
    return JobFinancials(invoice.total, cost, profit, margin)


def payment_follow_up(sent_on: date, today: date, paid: bool = False) -> str | None:
    """Return the follow-up action due for an unpaid invoice, if any."""
    if paid:
        return None
    days = (today - sent_on).days
    steps = business_rules()["follow_ups"]["payment_days"]
    if days >= steps["collections"]:
        return "Collections Review Required"
    if days >= steps["escalate"]:
        return "Escalate to Accounting"
    if days >= steps["reminder"]:
        return "Send Payment Reminder"
    return None
