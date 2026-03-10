import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runtime.engine import RuntimeEngine
from runtime.adapters.base import AdapterRegistry, RuntimeAdapter


FIXTURES = [
    {
        "name": "add_and_return",
        "code": "L1: R core.add 2 3 ->x J x\n",
        "label": "1",
    },
    {
        "name": "if_then_call",
        "code": "L1: Set cond true If cond ->L2 ->L3\nL2: Call L9 ->ans J ans\nL3: Set bad nope J bad\nL9: X v add 20 22 J v\n",
        "label": "1",
    },
    {
        "name": "loop_sum",
        "code": "L1: X arr arr 1 2 3 Set sum 0 Loop arr item ->L2 ->L3\nL2: X sum add sum item J sum\nL3: J sum\n",
        "label": "1",
    },
    {
        "name": "call_shared_frame_mutation",
        "code": "L1: Set x 0 Call L2 J x\nL2: Set x 9 J null\n",
        "label": "1",
    },
]


def test_runtime_step_vs_graph_parity():
    for fx in FIXTURES:
        eng_step = RuntimeEngine.from_code(fx["code"], strict=False, trace=False, step_fallback=True)
        out_step = eng_step.run_label(fx["label"])

        eng_graph = RuntimeEngine.from_code(fx["code"], strict=False, trace=False, step_fallback=False)
        out_graph = eng_graph.run_label(fx["label"])

        assert out_step == out_graph, f"{fx['name']} mismatch: step={out_step!r}, graph={out_graph!r}"


class _AlwaysFail(RuntimeAdapter):
    def call(self, target, args, context):
        raise RuntimeError("always-fail")


class _Counter(RuntimeAdapter):
    def __init__(self):
        self.calls = 0

    def call(self, target, args, context):
        self.calls += 1
        return self.calls


class _FailOnce(RuntimeAdapter):
    def __init__(self):
        self.calls = 0

    def call(self, target, args, context):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("boom-once")
        return 7


def test_runtime_step_vs_graph_parity_err_after_failing_r():
    code = "L1: R ext.G /x ->out Err ->L9 J out\nL9: Set handled _error J handled\n"

    reg_step = AdapterRegistry(allowed=["core", "ext"])
    reg_step.register("ext", _AlwaysFail())
    eng_step = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg_step, step_fallback=True)
    out_step = eng_step.run_label("1")

    reg_graph = AdapterRegistry(allowed=["core", "ext"])
    reg_graph.register("ext", _AlwaysFail())
    eng_graph = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg_graph, step_fallback=False)
    out_graph = eng_graph.run_label("1")

    assert out_step == out_graph
    assert "always-fail" in str(out_step)


def test_runtime_step_vs_graph_parity_retry_on_failing_call():
    code = "L1: Call L2 ->res Retry @n1 2 0 J res\nL2: R ext.G /x ->v J v\n"

    reg_step = AdapterRegistry(allowed=["core", "ext"])
    flaky_step = _FailOnce()
    reg_step.register("ext", flaky_step)
    eng_step = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg_step, step_fallback=True)
    out_step = eng_step.run_label("1")

    reg_graph = AdapterRegistry(allowed=["core", "ext"])
    flaky_graph = _FailOnce()
    reg_graph.register("ext", flaky_graph)
    eng_graph = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg_graph, step_fallback=False)
    out_graph = eng_graph.run_label("1")

    assert out_step == out_graph == 7
    assert flaky_step.calls == flaky_graph.calls == 2


def test_runtime_step_vs_graph_parity_no_j_termination_no_replay():
    code = "L1: R ext.G /x ->out\n"

    reg_step = AdapterRegistry(allowed=["core", "ext"])
    ctr_step = _Counter()
    reg_step.register("ext", ctr_step)
    eng_step = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg_step, step_fallback=True)
    out_step = eng_step.run_label("1")

    reg_graph = AdapterRegistry(allowed=["core", "ext"])
    ctr_graph = _Counter()
    reg_graph.register("ext", ctr_graph)
    eng_graph = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg_graph, step_fallback=False)
    out_graph = eng_graph.run_label("1")

    assert out_step == out_graph == None
    assert ctr_step.calls == 1
    assert ctr_graph.calls == 1
