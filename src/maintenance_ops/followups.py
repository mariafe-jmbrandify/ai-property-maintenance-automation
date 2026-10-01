"""Follow-up timers, SLA checks, and exception detection (Scenarios 7, 12, 13)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from .config import business_rules

APPROVAL_STEPS = ("Initial follow-up", "Reminder", "Escalate")
TENANT_STEPS = ("Send reminder SMS", "Notify admin and escalate to PM")


def _minutes(start: datetime | None, now: datetime) -> float | None:
    return None if start is None else (now - start).total_seconds() / 60


def _step_due(elapsed: float | None, thresholds: list[int], labels: tuple[str, ...]) -> str | None:
    if elapsed is None:
        return None
    due = None
    for minutes, label in zip(thresholds, labels):
        if elapsed >= minutes:
            due = label
    return due


def approval_follow_up(requested_at: datetime | None, now: datetime) -> str | None:
    rules = business_rules()["follow_ups"]["pm_approval_minutes"]
    return _step_due(_minutes(requested_at, now), rules, APPROVAL_STEPS)


def tenant_follow_up(contacted_at: datetime | None, now: datetime) -> str | None:
    rules = business_rules()["follow_ups"]["tenant_response_minutes"]
    return _step_due(_minutes(contacted_at, now), rules, TENANT_STEPS)


@dataclass(frozen=True)
class OpsException:
    type: str
    owner: str
    action: str


def detect_exceptions(wo: Mapping[str, Any], now: datetime) -> list[OpsException]:
    """Inspect one active work order and return every exception that needs an owner."""
    rules = business_rules()
    sla = rules["sla_minutes"]
    status = wo.get("status", "")
    found: list[OpsException] = []

    if status in rules["coordinator"]["inactive_statuses"]:
        return found

    received = wo.get("received_at")
    if received and not wo.get("first_tenant_contact_at"):
        if _minutes(received, now) > sla["initial_tenant_contact"]:
            found.append(OpsException("SLA: tenant contact", "Dispatcher", "Contact the tenant now"))
    if received and not wo.get("estimate_id") and _minutes(received, now) > sla["estimate_creation"]:
        found.append(OpsException("SLA: estimate creation", "Operations", "Create the initial assessment estimate"))

    if status in ("Awaiting Tenant Confirmation", "Waiting Tenant Response"):
        step = tenant_follow_up(wo.get("tenant_contacted_at"), now)
        if step:
            found.append(OpsException("Tenant not responding", "Dispatcher", step))

    if status in ("Pending PM Approval", "Approval Delayed", "Awaiting Owner Approval"):
        step = approval_follow_up(wo.get("approval_requested_at"), now)
        if step:
            found.append(OpsException("PM approval pending", "Operations", step))

    if status == "Repair Approved" and not wo.get("repair_technician"):
        found.append(OpsException("Approved repair unassigned", "Dispatcher", "Assign a technician immediately"))

    if wo.get("priority") == "Emergency" and status in (
        "New Work Order", "Customer Verified", "Awaiting Tenant Confirmation", "Ready for Assessment Dispatch"
    ):
        found.append(OpsException("Emergency not dispatched", "Dispatcher", "Create emergency job and assign on-call technician"))

    if status in ("Access Failed", "Waiting Parts", "Callback Required", "QA Revision Required"):
        found.append(OpsException(status, "Operations", "Follow the Scenario 12 recovery playbook"))

    return found
