import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from compiler_v2 import AICodeCompiler
from scripts.compat_gate import check_compat_gate
from scripts.policy_gate import check_policy_gate


def test_policy_gate_rejects_unknown_allow_role():
    c = AICodeCompiler()
    ir = c.compile("Allow admin /x G\n")
    res = check_policy_gate(ir)
    assert not res["ok"]
    assert any("undefined role" in v for v in res["violations"])


def test_policy_gate_accepts_known_role_and_allow():
    c = AICodeCompiler()
    ir = c.compile("S core web /api\nRole admin\nAllow admin /x G\nE /x G ->L1\nL1: J data\n")
    res = check_policy_gate(ir)
    assert res["ok"], res


def test_compat_gate_detects_breaking_removal():
    c = AICodeCompiler()
    old_ir = c.compile("S core web /api\nE /x G ->L1\nL1: J data\n")
    new_ir = c.compile("S core web /api\nE /y G ->L2\nL2: J data\n")
    res = check_compat_gate(old_ir, new_ir, mode="add")
    assert not res["ok"]
    assert any("endpoint removed" in b for b in res["breaks"])
