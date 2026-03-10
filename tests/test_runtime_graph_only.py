import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.engine import RuntimeEngine
from runtime.adapters.base import AdapterRegistry, RuntimeAdapter


class FlakyAdapter(RuntimeAdapter):
    def __init__(self):
        self.calls = 0

    def call(self, target, args, context):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("boom-once")
        return 7


class AlwaysFailAdapter(RuntimeAdapter):
    def call(self, target, args, context):
        raise RuntimeError("always-fail")


class CountingAdapter(RuntimeAdapter):
    def __init__(self):
        self.calls = 0

    def call(self, target, args, context):
        self.calls += 1
        return self.calls


def test_graph_only_retry_port_recovers():
    code = """
L1: R ext.G /x ->out Retry 2 0 J out
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", FlakyAdapter())
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=False)
    out = eng.run_label("1")
    assert out == 7


def test_graph_only_retry_recovers_failing_call_node():
    code = """
L1: Call L2 ->res Retry @n1 2 0 J res
L2: R ext.G /x ->v J v
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    flaky = FlakyAdapter()
    reg.register("ext", flaky)
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=False)
    out = eng.run_label("1")
    assert out == 7
    assert flaky.calls == 2


def test_graph_only_err_port_routes_handler():
    code = """
L1: R ext.G /x ->out Err ->L9 J out
L9: Set handled _error J handled
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", AlwaysFailAdapter())
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=False)
    out = eng.run_label("1")
    assert "always-fail" in str(out)


def test_graph_only_if_and_call_flow():
    code = """
L1: Set cond true If cond ->L2 ->L3
L2: Call L9 J _call_result
L3: Set bad "nope" J bad
L9: R core.add 20 22 ->v J v
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False)
    out = eng.run_label("1")
    assert out == 42


def test_graph_only_call_with_explicit_out():
    code = """
L1: Call L9 ->ans J ans
L9: R core.add 8 9 ->v J v
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False)
    out = eng.run_label("1")
    assert out == 17


def test_graph_only_non_r_error_routes_err_handler():
    code = """
L1: X x div 1 0 Err ->L9 J x
L9: Set handled _error J handled
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False)
    out = eng.run_label("1")
    assert "division by zero" in str(out)


def test_graph_without_j_does_not_fallback_after_execution():
    code = """
L1: R ext.G /x ->out
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    counter = CountingAdapter()
    reg.register("ext", counter)
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=True)
    out = eng.run_label("1")
    assert out is None
    assert counter.calls == 1


def test_graph_err_only_path_can_fallback_to_steps():
    ir = {
        "labels": {
            "1": {
                "entry": "n1",
                "nodes": [{"id": "n1", "op": "Err", "data": {"op": "Err", "handler": "L9"}}],
                "edges": [],
                "legacy": {"steps": [{"op": "J", "var": "x"}]},
            }
        },
        "source": {"lines": []},
        "cst": {"lines": []},
    }
    eng = RuntimeEngine(ir=ir, trace=False, step_fallback=True)
    out = eng.run_label("1", {"x": 5})
    assert out == 5


def test_graph_nonmeta_execution_does_not_step_fallback():
    reg = AdapterRegistry(allowed=["core", "ext"])
    counter = CountingAdapter()
    reg.register("ext", counter)
    ir = {
        "labels": {
            "1": {
                "entry": "n1",
                "nodes": [
                    {"id": "n1", "op": "Err", "data": {"op": "Err", "handler": "L9"}},
                    {"id": "n2", "op": "R", "data": {"op": "R", "adapter": "ext", "target": "op", "args": [], "out": "x"}},
                ],
                "edges": [{"from": "n1", "to": "n2", "to_kind": "node"}],
                "legacy": {"steps": [{"op": "R", "adapter": "ext", "target": "op", "args": [], "out": "x"}]},
            }
        },
        "source": {"lines": []},
        "cst": {"lines": []},
    }
    eng = RuntimeEngine(ir=ir, adapters=reg, trace=False, step_fallback=True)
    out = eng.run_label("1")
    assert out is None
    assert counter.calls == 1


def test_graph_if_no_value_return_does_not_fallthrough_to_linear_node():
    reg = AdapterRegistry(allowed=["core", "ext"])
    counter = CountingAdapter()
    reg.register("ext", counter)
    ir = {
        "labels": {
            "1": {
                "entry": "n1",
                "nodes": [
                    {"id": "n1", "op": "Set", "data": {"op": "Set", "name": "cond", "ref": True}},
                    {"id": "n2", "op": "If", "data": {"op": "If", "cond": "cond"}},
                    {"id": "n3", "op": "R", "data": {"op": "R", "adapter": "ext", "target": "op", "args": [], "out": "x"}},
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "to_kind": "node"},
                    {"from": "n2", "to": "2", "to_kind": "label", "port": "then"},
                    {"from": "n2", "to": "3", "to_kind": "label", "port": "else"},
                    {"from": "n2", "to": "n3", "to_kind": "node"},
                ],
                "legacy": {"steps": []},
            },
            "2": {"legacy": {"steps": [{"op": "Set", "name": "x", "ref": 9}, {"op": "J", "var": "null"}]}},
            "3": {"legacy": {"steps": [{"op": "J", "var": "null"}]}},
        },
        "source": {"lines": []},
        "cst": {"lines": []},
    }
    eng = RuntimeEngine(ir=ir, adapters=reg, trace=False, step_fallback=False)
    out = eng.run_label("1")
    assert out is None
    assert counter.calls == 0


def test_graph_linear_edge_prefers_explicit_next_port():
    ir = {
        "labels": {
            "1": {
                "entry": "n1",
                "nodes": [
                    {"id": "n1", "op": "Set", "data": {"op": "Set", "name": "x", "ref": 1}},
                    {"id": "n2", "op": "Set", "data": {"op": "Set", "name": "x", "ref": 2}},
                    {"id": "n3", "op": "J", "data": {"op": "J", "var": "x"}},
                    {"id": "n4", "op": "Set", "data": {"op": "Set", "name": "x", "ref": 99}},
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "to_kind": "node", "port": "next"},
                    {"from": "n1", "to": "n4", "to_kind": "node", "port": "alt"},
                    {"from": "n2", "to": "n3", "to_kind": "node"},
                ],
                "legacy": {"steps": []},
            }
        },
        "source": {"lines": []},
        "cst": {"lines": []},
    }
    eng = RuntimeEngine(ir=ir, trace=False, step_fallback=False)
    out = eng.run_label("1")
    assert out == 2


def test_graph_mode_is_canonical_when_graph_exists_unless_force_steps():
    ir = {
        "labels": {
            "1": {
                "entry": "n1",
                "nodes": [{"id": "n1", "op": "J", "data": {"op": "J", "var": "g"}}],
                "edges": [],
                "legacy": {"steps": [{"op": "J", "var": "s"}]},
            }
        },
        "source": {"lines": []},
        "cst": {"lines": []},
    }
    eng = RuntimeEngine(ir=ir, trace=False, step_fallback=True)
    out_graph = eng.run_label("1", {"g": 10, "s": 20})
    out_steps = eng._run_label("1", {"g": 10, "s": 20}, [], force_steps=True)
    assert out_graph == 10
    assert out_steps == 20
