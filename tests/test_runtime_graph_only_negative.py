import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.engine import RuntimeEngine
from runtime.adapters.base import AdapterRegistry, RuntimeAdapter


class AlwaysFailAdapter(RuntimeAdapter):
    def call(self, target, args, context):
        raise RuntimeError("always-fail")


def test_graph_only_retry_exhaustion_raises():
    code = """
L1: R ext.op x ->out Retry 1 0 J out
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", AlwaysFailAdapter())
    eng = RuntimeEngine.from_code(code, strict=True, trace=False, adapters=reg, step_fallback=False)
    try:
        eng.run_label("1")
        assert False, "expected retry exhaustion error"
    except Exception as e:
        msg = str(e)
        assert "always-fail" in msg
        assert "label=1" in msg


def test_graph_only_missing_err_handler_raises():
    code = """
L1: R ext.op x ->out J out
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", AlwaysFailAdapter())
    eng = RuntimeEngine.from_code(code, strict=True, trace=False, adapters=reg, step_fallback=False)
    try:
        eng.run_label("1")
        assert False, "expected unhandled error"
    except Exception as e:
        msg = str(e)
        assert "always-fail" in msg
        assert "label=1" in msg


def test_graph_only_while_limit_exceeded():
    code = """
L1: Set cond true While cond ->L2 ->L3
L2: J keep_going
L3: J done
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False)
    try:
        eng.run_label("1")
        assert False, "expected while limit error"
    except Exception as e:
        msg = str(e)
        assert "while loop iteration limit exceeded" in msg
        assert "label=1" in msg


def test_graph_only_err_handler_recursion_is_rejected():
    code = """
L1: R ext.op x ->out Err ->L1 J out
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", AlwaysFailAdapter())
    eng = RuntimeEngine.from_code(code, strict=True, trace=False, adapters=reg, step_fallback=False)
    try:
        eng.run_label("1")
        assert False, "expected recursion guard error"
    except Exception as e:
        msg = str(e)
        assert "error handler recursion detected" in msg
        assert "handler=1" in msg
        assert "failing_op=R" in msg
        assert "label=1" in msg


def test_graph_only_ambiguous_linear_node_edges_raise():
    ir = {
        "labels": {
            "1": {
                "entry": "n1",
                "nodes": [
                    {"id": "n1", "op": "Set", "data": {"op": "Set", "name": "x", "ref": 1}},
                    {"id": "n2", "op": "Set", "data": {"op": "Set", "name": "x", "ref": 2}},
                    {"id": "n3", "op": "Set", "data": {"op": "Set", "name": "x", "ref": 3}},
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "to_kind": "node"},
                    {"from": "n1", "to": "n3", "to_kind": "node"},
                ],
                "legacy": {"steps": []},
            }
        },
        "source": {"lines": []},
        "cst": {"lines": []},
    }
    eng = RuntimeEngine(ir=ir, trace=False, step_fallback=False)
    try:
        eng.run_label("1")
        assert False, "expected ambiguous node edge error"
    except Exception as e:
        msg = str(e)
        assert "ambiguous graph next edges" in msg
