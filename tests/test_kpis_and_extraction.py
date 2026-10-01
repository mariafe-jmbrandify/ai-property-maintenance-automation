import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from maintenance_ops.extraction import estimate_title, normalize_phone, validate
from maintenance_ops.kpis import average_hours, callback_rate, first_visit_resolution_rate, revenue_by_pm_company

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "samples" / "sample_ai_extraction.json"

ORDERS = [
    {"pm_company_name": "ABC", "repair_completed_at": 1, "first_visit_resolution": True, "invoice_total": 325, "internal_cost_total": 240,
     "approval_requested_at": datetime(2026, 7, 5, 9), "approval_received_at": datetime(2026, 7, 6, 9)},
    {"pm_company_name": "ABC", "repair_completed_at": 1, "first_visit_resolution": False, "callback_required": True, "invoice_total": 220, "internal_cost_total": 160},
    {"pm_company_name": "XYZ", "repair_completed_at": 1, "first_visit_resolution": True, "invoice_total": 100, "internal_cost_total": 70},
    {"pm_company_name": "XYZ"},
]


def test_kpis():
    assert first_visit_resolution_rate(ORDERS) == 66.7
    assert callback_rate(ORDERS) == 33.3
    assert average_hours(ORDERS, "approval_requested_at", "approval_received_at") == 24.0
    by_pm = revenue_by_pm_company(ORDERS)
    assert by_pm["ABC"]["revenue"] == Decimal("545.00")
    assert by_pm["ABC"]["gross_profit"] == Decimal("145.00")


def test_sample_extraction_is_complete():
    result = validate(json.loads(SAMPLE.read_text()))
    assert result.is_complete
    assert result.next_status == "New Work Order"
    assert result.data["tenant_phone"] == "(555) 111-1111"
    assert result.data["nte_limit"] == 120.0


def test_missing_fields_route_to_needs_more_info():
    result = validate({"pm_company": "ABC", "issue_description": "Leak", "priority": "urgent!!"})
    assert "pm_work_order_number" in result.missing
    assert "tenant_phone or tenant_email" in result.missing
    assert result.next_status == "Needs More Info"
    assert result.data["priority"] == "Normal"


def test_phone_normalization_keeps_unparseable_values():
    assert normalize_phone("+1 (555) 222-3333") == "(555) 222-3333"
    assert normalize_phone("ext 12") == "ext 12"


def test_estimate_title_starts_with_pm_work_order():
    assert estimate_title("WO-45891", "Plumbing", "123 Main St") == "WO-45891 - Plumbing Assessment - 123 Main St"
