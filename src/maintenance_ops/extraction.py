"""Validation and normalization of the AI work order extraction (Scenario 1).

The AI module returns JSON matching prompts/schemas/work_order.schema.json.
Never write AI output to the database without passing it through validate().
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from .config import business_rules

REQUIRED = ("pm_company", "pm_work_order_number", "property_address", "tenant_name", "issue_description")
CONTACT = ("tenant_phone", "tenant_email")


@dataclass
class ExtractionResult:
    data: dict[str, Any]
    missing: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.missing

    @property
    def next_status(self) -> str:
        return "New Work Order" if self.is_complete else "Needs More Info"


def normalize_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return raw.strip()
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def normalize_money(raw: Any) -> float | None:
    if raw in (None, ""):
        return None
    cleaned = re.sub(r"[^\d.]", "", str(raw))
    return float(cleaned) if cleaned else None


def validate(ai_output: Mapping[str, Any]) -> ExtractionResult:
    rules = business_rules()
    data = {k: (v.strip() if isinstance(v, str) else v) for k, v in ai_output.items()}
    result = ExtractionResult(data=data)

    for key in REQUIRED:
        if not data.get(key):
            result.missing.append(key)
    if not any(data.get(k) for k in CONTACT):
        result.missing.append("tenant_phone or tenant_email")

    data["tenant_phone"] = normalize_phone(data.get("tenant_phone"))
    data["nte_limit"] = normalize_money(data.get("nte_limit"))

    priority = (data.get("priority") or "Normal").title()
    if priority not in rules["priorities"]:
        result.warnings.append(f"Unknown priority {priority!r}; defaulted to Normal")
        priority = "Normal"
    data["priority"] = priority

    trade = data.get("trade")
    if trade and trade not in rules["trades"]:
        result.warnings.append(f"Unknown trade {trade!r}; left for AI classification in Scenario 5")
        data["trade"] = None

    email = data.get("tenant_email")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        result.warnings.append(f"Tenant email looks invalid: {email!r}")

    return result


def estimate_title(pm_work_order_number: str, trade: str | None, property_address: str) -> str:
    """Standard Housecall Pro estimate title. The PM WO # always comes first."""
    return f"{pm_work_order_number} - {trade or 'General Maintenance'} Assessment - {property_address}"
