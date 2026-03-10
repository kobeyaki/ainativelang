import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.adapters.base import AdapterError
from runtime.adapters.tools import ToolBridgeAdapter


def _sum_tool(a, b, context=None):
    return int(a) + int(b)


def _err_tool(*args, **kwargs):
    raise RuntimeError("boom")


def test_tools_adapter_happy_path_and_idempotency():
    adp = ToolBridgeAdapter({"sum": _sum_tool}, allow_tools=["sum"])
    r1 = adp.call("sum", [2, 3], {})
    r2 = adp.call("sum", [2, 3], {})
    assert r1 == 5
    assert r2 == 5


def test_tools_adapter_allowlist_and_registration_validation():
    adp = ToolBridgeAdapter({"sum": _sum_tool}, allow_tools=["sum"])
    try:
        adp.call("nope", [1], {})
        assert False, "expected allowlist block"
    except Exception as e:
        assert isinstance(e, AdapterError)
    adp2 = ToolBridgeAdapter({}, allow_tools=["missing"])
    try:
        adp2.call("missing", [], {})
        assert False, "expected missing tool error"
    except Exception as e:
        assert isinstance(e, AdapterError)
        assert "not registered" in str(e)


def test_tools_adapter_error_mapping():
    adp = ToolBridgeAdapter({"err": _err_tool}, allow_tools=["err"])
    try:
        adp.call("err", [], {})
        assert False, "expected mapped tool execution error"
    except Exception as e:
        assert isinstance(e, AdapterError)
        assert "tool execution error" in str(e)
