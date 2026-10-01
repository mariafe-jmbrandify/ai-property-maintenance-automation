from datetime import datetime, timedelta

from maintenance_ops.followups import approval_follow_up, detect_exceptions, tenant_follow_up

NOW = datetime(2026, 7, 20, 12, 0)


def test_approval_follow_up_steps():
    assert approval_follow_up(NOW - timedelta(minutes=10), NOW) is None
    assert approval_follow_up(NOW - timedelta(minutes=25), NOW) == "Initial follow-up"
    assert approval_follow_up(NOW - timedelta(hours=25), NOW) == "Reminder"
    assert approval_follow_up(NOW - timedelta(hours=49), NOW) == "Escalate"


def test_tenant_follow_up_steps():
    assert tenant_follow_up(NOW - timedelta(hours=2), NOW) is None
    assert tenant_follow_up(NOW - timedelta(hours=25), NOW) == "Send reminder SMS"
    assert tenant_follow_up(NOW - timedelta(hours=49), NOW) == "Notify admin and escalate to PM"


def test_closed_orders_are_ignored():
    assert detect_exceptions({"status": "Closed", "received_at": NOW - timedelta(days=9)}, NOW) == []


def test_sla_and_emergency_detected():
    wo = {"status": "Customer Verified", "priority": "Emergency", "received_at": NOW - timedelta(hours=1)}
    types = {e.type for e in detect_exceptions(wo, NOW)}
    assert {"SLA: tenant contact", "SLA: estimate creation", "Emergency not dispatched"} <= types


def test_approved_repair_without_technician():
    wo = {"status": "Repair Approved", "received_at": NOW, "first_tenant_contact_at": NOW, "estimate_id": "EST-1"}
    assert [e.type for e in detect_exceptions(wo, NOW)] == ["Approved repair unassigned"]
