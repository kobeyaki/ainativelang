import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine
from adapters.mock import mock_registry
from scripts.contracts_gate import check_contracts


def test_capability_ops_compile_and_runtime_flow():
    code = """
S core web /api
C prodCache productKey 60
Q jobs 100 3
Txn orderTx db readwrite
Pol adminOnly role=admin auth=true
L1: CacheSet prodCache "p1" "payload" 60 CacheGet prodCache "p1" ->rows QueuePut jobs rows ->msg Tx begin orderTx Enf adminOnly Tx commit orderTx J rows
"""
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(code)
    assert not ir.get("errors"), ir.get("errors")
    eng = RuntimeEngine(ir, mock_registry(ir.get("types")))
    out = eng.run_label("1", frame={"_role": "admin", "_auth_present": True})
    assert out == "payload"


def test_policy_enforcement_runtime_violation():
    code = """
Pol adminOnly role=admin auth=true
L1: Enf adminOnly J data
"""
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(code)
    eng = RuntimeEngine(ir, mock_registry(ir.get("types")))
    with pytest.raises(RuntimeError):
        eng.run_label("1", frame={"_role": "user", "_auth_present": False})


def test_strict_capability_reference_validation():
    code = "L1: CacheGet missingCache k ->out J out\n"
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(code)
    assert any("undefined cache" in e for e in ir.get("errors", []))


def test_contract_gate_flags_missing_endpoint():
    code = """
S core web /api
Contract /users G A[User]
L1: J data
"""
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(code)
    res = check_contracts(ir)
    assert not res["ok"]
    assert any("contract missing endpoint" in v for v in res["violations"])
