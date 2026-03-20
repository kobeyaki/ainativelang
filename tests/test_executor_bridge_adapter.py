"""Phase 3: ExecutorBridgeAdapter + strict contract for bridge.POST."""

from __future__ import annotations

import json
import os
import socketserver
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from runtime.adapters.base import AdapterError, AdapterRegistry
from runtime.adapters.builtins import CoreBuiltinAdapter
from runtime.adapters.executor_bridge import ExecutorBridgeAdapter
from runtime.engine import RuntimeEngine

ROOT = Path(__file__).resolve().parent.parent
ADAPTER_EXAMPLE = ROOT / "examples" / "integrations" / "executor_bridge_adapter_min.ainl"


class _H(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/v1/execute":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(n) if n else b"{}"
        body = json.loads(raw.decode("utf-8") or "{}")
        out = json.dumps({"ok": True, "echo": body}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *args) -> None:
        return


class _Srv(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def _serve():
    s = _Srv(("127.0.0.1", 0), _H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def _reg(endpoints: dict) -> AdapterRegistry:
    r = AdapterRegistry(allowed=["core", "bridge"])
    r.register("core", CoreBuiltinAdapter())
    r.register(
        "bridge",
        ExecutorBridgeAdapter(endpoints=endpoints, default_timeout_s=5.0),
    )
    return r


def test_executor_bridge_adapter_unknown_key():
    adp = ExecutorBridgeAdapter({"a": "http://127.0.0.1:9/x"})
    with pytest.raises(AdapterError, match="unknown executor"):
        adp.call("Post", ["missing", {}], {})


def test_executor_bridge_adapter_delegates_to_http():
    srv = _serve()
    try:
        url = f"http://127.0.0.1:{srv.server_port}/v1/execute"
        adp = ExecutorBridgeAdapter({"demo.echo": url}, default_timeout_s=5.0)
        env = adp.call("Post", ["demo.echo", {"x": 1}], {})
        assert env["ok"] is True
        assert env["status_code"] == 200
        assert env["body"]["echo"]["x"] == 1
    finally:
        srv.shutdown()


def test_executor_bridge_example_compiles_and_uses_bridge_post():
    code = ADAPTER_EXAMPLE.read_text(encoding="utf-8")
    ir = AICodeCompiler(strict_mode=False).compile(code, emit_graph=True)
    assert not ir.get("errors"), ir.get("errors")
    found = False
    for block in (ir.get("labels") or {}).values():
        for n in block.get("nodes") or []:
            d = n.get("data") or {}
            if str(d.get("adapter") or "").lower() == "bridge.post":
                found = True
                break
    assert found, "expected an R bridge.Post step in IR"


def test_executor_bridge_adapter_program_end_to_end():
    srv = _serve()
    try:
        url = f"http://127.0.0.1:{srv.server_port}/v1/execute"
        code = ADAPTER_EXAMPLE.read_text(encoding="utf-8")
        eng = RuntimeEngine.from_code(code, strict=False, adapters=_reg({"demo.echo": url}))
        out = eng.run_label(eng.default_entry_label(), frame={})
        assert out == "bridge_ok"
    finally:
        srv.shutdown()


def test_bridge_post_strict_effect_key_present():
    from tooling.effect_analysis import ADAPTER_EFFECT

    assert "bridge.POST" in ADAPTER_EFFECT
