"""Command-line demo: run sample assessments through the decision engine.

    python -m maintenance_ops.cli demo
    python -m maintenance_ops.cli decide --labor 120 --materials 45 --nte 120
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .billing import build_invoice, job_financials
from .config import business_rules
from .pricing import InternalCost, decide
from .visibility import client_view, leaked_fields

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "samples" / "sample_assessments.json"


def _print_case(case: dict) -> None:
    fee = business_rules()["pricing"]["assessment_fee"]["internal_cost"]
    cost = InternalCost.from_values(case.get("assessment_fee_cost", fee), case["labor_cost"], case["material_cost"])
    decision = decide(cost, case["nte_limit"])
    print(f"\n=== {case['pm_work_order_number']} | {case['scenario']} ===")
    print(f"Internal cost ${cost.total} -> client price ${decision.client_price} vs NTE ${decision.nte_limit}")
    print(f"Decision: {decision.outcome} ({decision.reason}) -> status '{decision.next_status}'")

    approved = decision.same_visit_repair or case.get("pm_response") == "approved"
    if not decision.same_visit_repair:
        print(f"PM response: {case.get('pm_response', 'pending')}")
    invoice = build_invoice(approved=approved, client_price=decision.client_price, service_label=f"{case['trade']} repair")
    fin = job_financials(invoice, cost.total if approved else cost.assessment_fee)
    for label, amount in invoice.lines:
        print(f"  invoice line: {label:<40} ${amount}")
    print(f"  invoice total ${invoice.total} | gross profit ${fin.gross_profit} ({fin.gross_margin_pct}%)")

    record = {**case, "client_price": str(decision.client_price), "internal_cost_total": str(cost.total)}
    view = client_view(record)
    assert not leaked_fields(view), "internal fields leaked into the client view"
    print("  PM client view:", json.dumps(view))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="maintenance-ops")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="Run the sample assessments")
    d = sub.add_parser("decide", help="Price one assessment and decide")
    d.add_argument("--labor", type=float, required=True)
    d.add_argument("--materials", type=float, required=True)
    d.add_argument("--nte", type=float, required=True)
    d.add_argument("--assessment-fee", type=float, default=None)
    args = parser.parse_args(argv)

    if args.cmd == "demo":
        for case in json.loads(SAMPLES.read_text(encoding="utf-8")):
            _print_case(case)
    else:
        fee = args.assessment_fee if args.assessment_fee is not None else business_rules()["pricing"]["assessment_fee"]["internal_cost"]
        result = decide(InternalCost.from_values(fee, args.labor, args.materials), args.nte)
        print(json.dumps({k: str(v) for k, v in result.__dict__.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
