"""
Tests for tooling/security_report.py (privilege map over IR).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.security_report import analyze_ir


def _compile(code: str):
    c = AICodeCompiler()
    ir = c.compile(code.strip() + "\n")
    assert not ir.get("errors"), ir.get("errors")
    return ir


def test_security_report_core_only():
    code = "L1: R core.ADD 2 3 ->x J x"
    ir = _compile(code)
    rep = analyze_ir(ir)
    summary = rep["summary"]
    adapters = summary["adapters"]
    assert "core" in adapters
    assert adapters["core"]["privilege_tiers"] == ["pure"]
    assert summary["privilege_tiers"] == ["pure"]


def test_security_report_local_state_and_network():
    code = """
S core web /api
E /users G ->L1 ->out
L1:
  R sqlite.Execute "INSERT INTO users VALUES(1)" ->r1
  R http.Get "https://example.com" ->r2
  J r2
"""
    ir = _compile(code)
    rep = analyze_ir(ir)
    summary = rep["summary"]
    tiers = set(summary["privilege_tiers"])
    assert "local_state" in tiers
    assert "network" in tiers
    adapters = summary["adapters"]
    assert "sqlite" in adapters and "local_state" in adapters["sqlite"]["privilege_tiers"]
    assert "http" in adapters and "network" in adapters["http"]["privilege_tiers"]


def test_security_report_operator_sensitive():
    code = "L1: R svc.caddy status ->out J out"
    ir = _compile(code)
    rep = analyze_ir(ir)
    summary = rep["summary"]
    tiers = set(summary["privilege_tiers"])
    assert "operator_sensitive" in tiers
    adapters = summary["adapters"]
    assert "svc" in adapters
    assert "operator_sensitive" in adapters["svc"]["privilege_tiers"]
