#!/usr/bin/env python3
"""
Minimal local HTTP server for docs/integrations/EXTERNAL_EXECUTOR_BRIDGE.md (Phase 1).

Accepts POST /v1/execute with a JSON body matching the bridge request envelope,
returns HTTP 200 and a small JSON body. For manual runs with:
  examples/integrations/executor_bridge_min.ainl

Usage:
  python3 scripts/mock_executor_bridge.py
  # default bind 127.0.0.1:17300
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_POST(self) -> None:
        if self.path != "/v1/execute":
            self.send_error(404, "use POST /v1/execute")
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_error(400, "invalid JSON")
            return
        out = {
            "accepted": True,
            "executor": body.get("executor"),
            "run_id": body.get("run_id"),
            "echo_payload": body.get("payload"),
        }
        data = json.dumps(out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> int:
    host = "127.0.0.1"
    port = 17300
    httpd = HTTPServer((host, port), Handler)
    print(f"mock executor bridge listening on http://{host}:{port}/v1/execute", file=sys.stderr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
