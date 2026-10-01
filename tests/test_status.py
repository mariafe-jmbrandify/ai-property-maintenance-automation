import pytest

from maintenance_ops.status import InvalidTransition, allowed_next, can_transition, statuses, transition


def test_every_status_has_transition_rules():
    for s in statuses():
        allowed_next(s)


def test_every_transition_target_is_a_known_status():
    known = set(statuses())
    for s in statuses():
        assert set(allowed_next(s)) <= known, s


def test_happy_path_is_valid():
    path = ["New Work Order", "Customer Verified", "Awaiting Tenant Confirmation",
            "Ready for Assessment Dispatch", "Assessment Scheduled", "Pending Cost Review",
            "Pending PM Approval", "Repair Approved", "Repair Scheduled", "Repair Completed",
            "Ready for Tenant Confirmation", "Ready for Invoice", "Invoiced", "Closed"]
    for a, b in zip(path, path[1:]):
        assert can_transition(a, b), f"{a} -> {b}"


def test_cannot_skip_approval():
    with pytest.raises(InvalidTransition):
        transition("Pending PM Approval", "Repair Scheduled")


def test_closed_is_terminal():
    assert allowed_next("Closed") == []
