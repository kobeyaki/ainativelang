"""
Tests for tooling/policy_validator.py (simple IR policy checks).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.policy_validator import validate_ir_against_policy


def _compile(code: str):
    c = AICodeCompiler()
    ir = c.compile(code.strip() + "\n")
    assert not ir.get("errors"), ir.get("errors")
    return ir


def test_policy_forbids_http_adapter():
    code = """
S core web /api
E /ping G ->L1 ->out
L1: R http.Get "https://example.com" ->out J out
"""
    ir = _compile(code)
    policy = {"forbidden_adapters": ["http"]}
    res = validate_ir_against_policy(ir, policy)
    assert not res["ok"]
    errs = res["errors"]
    assert any(e["code"] == "POLICY_ADAPTER_FORBIDDEN" for e in errs)


def test_policy_allows_db_when_only_http_forbidden():
    code = """
S core web /api
E /users G ->L1 ->users
L1: R db.F User * ->users J users
"""
    ir = _compile(code)
    policy = {"forbidden_adapters": ["http"]}
    res = validate_ir_against_policy(ir, policy)
    assert res["ok"], res.get("errors")


def test_policy_forbids_network_privilege_tier():
    code = """
S core web /api
E /ping G ->L1 ->out
L1: R http.Get "https://example.com" ->out J out
"""
    ir = _compile(code)
    policy = {"forbidden_privilege_tiers": ["network"]}
    res = validate_ir_against_policy(ir, policy)
    assert not res["ok"]
    errs = res["errors"]
    assert any(e["code"] == "POLICY_PRIVILEGE_TIER_FORBIDDEN" for e in errs)


def test_policy_forbids_operator_sensitive_privilege_tier():
    code = """
L1: R svc.caddy status ->out J out
"""
    ir = _compile(code)
    policy = {"forbidden_privilege_tiers": ["operator_sensitive"]}
    res = validate_ir_against_policy(ir, policy)
    assert not res["ok"]
    errs = res["errors"]
    assert any(e["code"] == "POLICY_PRIVILEGE_TIER_FORBIDDEN" for e in errs)


def test_policy_mixed_privilege_tier_violations():
    code = """
S core web /api
E /ping G ->L1 ->out
L1:
  R http.Get "https://example.com" ->h
  R svc.caddy status ->s
  J h
"""
    ir = _compile(code)
    policy = {"forbidden_privilege_tiers": ["network", "operator_sensitive"]}
    res = validate_ir_against_policy(ir, policy)
    assert not res["ok"]
    errs = res["errors"]
    codes = {e["code"] for e in errs}
    assert "POLICY_PRIVILEGE_TIER_FORBIDDEN" in codes
