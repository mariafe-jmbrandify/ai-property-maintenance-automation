from maintenance_ops.visibility import client_view, leaked_fields, technician_view

RECORD = {
    "pm_work_order_number": "WO-45891", "pm_company_name": "ABC Property Management",
    "estimate_id": "EST-10001", "property_address": "123 Main St", "tenant_name": "John Smith",
    "tenant_phone": "(555) 111-1111", "scope_of_work": "Replace supply line", "client_price": "480.00",
    "labor_cost": "120", "material_cost": "45", "internal_cost_total": "240", "gross_profit": "85",
    "entry_instructions": "Gate code 4589",
}


def test_client_view_hides_internal_costs():
    view = client_view(RECORD)
    assert view["client_price"] == "480.00"
    assert leaked_fields(view) == []


def test_technician_view_hides_pm_and_money():
    view = technician_view(RECORD)
    assert "pm_company_name" not in view
    assert "pm_work_order_number" not in view
    assert "client_price" not in view
    assert leaked_fields(view) == []
    assert view["entry_instructions"] == "Gate code 4589"


def test_leak_detector_flags_internal_fields():
    assert "labor_cost" in leaked_fields(RECORD)
