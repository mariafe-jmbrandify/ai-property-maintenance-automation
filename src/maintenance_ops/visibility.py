"""Audience-specific views of a work order.

The platform serves three audiences that must never see each other's data:

* PM client view   -> scope, photos, client price. Never internal costs or margin.
* Technician view  -> everything needed onsite. Never PM company, PM WO #, or money.
* Internal view    -> everything.
"""

from __future__ import annotations

from typing import Any, Mapping

CLIENT_FIELDS = (
    "pm_work_order_number", "estimate_id", "job_id", "invoice_id",
    "property_address", "unit", "tenant_name", "trade",
    "findings", "recommendation", "scope_of_work", "photos_url",
    "client_price", "invoice_total", "status", "appointment_window",
)

TECHNICIAN_FIELDS = (
    "estimate_id", "job_id", "property_address", "unit",
    "tenant_name", "tenant_phone", "trade", "priority",
    "issue_description", "scope_of_work", "entry_instructions",
    "pet_notes", "photos_url", "appointment_window",
)

INTERNAL_ONLY_FIELDS = (
    "assessment_fee_cost", "labor_cost", "material_cost", "internal_cost_total",
    "markup_pct", "technician_pay", "gross_profit", "gross_margin_pct",
)


def _project(record: Mapping[str, Any], allowed: tuple[str, ...]) -> dict[str, Any]:
    return {key: record[key] for key in allowed if key in record and record[key] not in (None, "")}


def client_view(record: Mapping[str, Any]) -> dict[str, Any]:
    return _project(record, CLIENT_FIELDS)


def technician_view(record: Mapping[str, Any]) -> dict[str, Any]:
    return _project(record, TECHNICIAN_FIELDS)


def leaked_fields(payload: Mapping[str, Any]) -> list[str]:
    """Return internal-only fields present in an outbound payload (should be empty)."""
    return [key for key in INTERNAL_ONLY_FIELDS if key in payload]
