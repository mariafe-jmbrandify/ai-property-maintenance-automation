"""Minimal HTTP wrapper so Make.com / n8n can call the rules engine.

    python -m maintenance_ops.server --port 8080

POST /decide      {"assessment_fee": 75, "labor": 120, "materials": 45, "nte_limit": 120}
POST /extraction  <AI extraction JSON>  -> validated + normalized, with missing fields and next status

Standard library only. Put it behind HTTPS and a shared-secret header
(X-API-Key, checked against MAINTENANCE_OPS_API_KEY) before exposing it publicly.
"""

from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .extraction import validate
from .pricing import InternalCost, decide, resolve_nte


def handle(path: str, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    if path == "/decide":
        cost = InternalCost.from_values(body.get("assessment_fee"), body.get("labor"), body.get("materials"))
        result = decide(cost, resolve_nte(body.get("nte_limit"), body.get("pm_default_nte")))
        return 200, {**{k: str(v) for k, v in result.__dict__.items()}, "next_status": result.next_status}
    if path == "/extraction":
        result = validate(body)
        return 200, {"data": result.data, "missing": result.missing, "warnings": result.warnings, "next_status": result.next_status}
    return 404, {"error": f"unknown path {path}"}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        expected = os.environ.get("MAINTENANCE_OPS_API_KEY")
        if expected and self.headers.get("X-API-Key") != expected:
            return self._send(401, {"error": "unauthorized"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            status, payload = handle(self.path, body)
        except (ValueError, TypeError) as exc:
            status, payload = 400, {"error": str(exc)}
        self._send(status, payload)

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    ThreadingHTTPServer(("0.0.0.0", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
