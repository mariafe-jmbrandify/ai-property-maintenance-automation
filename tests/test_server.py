from maintenance_ops.server import handle


def test_decide_endpoint():
    status, body = handle("/decide", {"assessment_fee": 75, "labor": 120, "materials": 45, "nte_limit": 120})
    assert status == 200
    assert body["outcome"] == "APPROVAL_REQUIRED"
    assert body["client_price"] == "325.00"
    assert body["next_status"] == "Pending PM Approval"


def test_decide_uses_pm_default_when_work_order_has_no_nte():
    _, body = handle("/decide", {"assessment_fee": 75, "labor": 60, "materials": 25, "pm_default_nte": 250})
    assert body["outcome"] == "WITHIN_LIMIT"


def test_extraction_endpoint_flags_missing():
    _, body = handle("/extraction", {"pm_company": "ABC"})
    assert body["next_status"] == "Needs More Info"


def test_unknown_path():
    assert handle("/nope", {})[0] == 404
