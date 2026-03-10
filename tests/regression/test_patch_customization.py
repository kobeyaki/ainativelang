import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from compiler_v2 import AICodeCompiler
from scripts.patch_mode import apply_patch_ir
from scripts.plan_delta import compute_plan_delta


def test_patch_mode_safe_fail_conflict():
    c = AICodeCompiler()
    base = c.compile("S core web /api\nE /x G ->L1\nL1: J data\n")
    patch = c.compile("S core web /api\nE /x G ->L2\nL2: J data\n")
    merged = apply_patch_ir(base, patch, allow_replace=False)
    assert not merged["ok"]
    assert any("endpoint conflict" in x for x in merged["conflicts"])


def test_patch_mode_allow_replace():
    c = AICodeCompiler()
    base = c.compile("S core web /api\nE /x G ->L1\nL1: J data\n")
    patch = c.compile("S core web /api\nE /x G ->L2\nL2: J data\n")
    merged = apply_patch_ir(base, patch, allow_replace=True)
    assert merged["ok"]
    eps = merged["ir"]["services"]["core"]["eps"]["/x"]
    assert eps["G"]["label_id"] == "2"


def test_plan_delta_reports_additive_change():
    c = AICodeCompiler()
    base = c.compile("S core web /api\nE /x G ->L1\nL1: J data\n")
    new = c.compile("S core web /api\nE /x G ->L1\nE /y P ->L2\nL1: J data\nL2: J data\n")
    d = compute_plan_delta(base, new)
    assert not d["breaking"]
    assert ("/y", "P") in [tuple(x) for x in d["endpoints"]["added"]]
