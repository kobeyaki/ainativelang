import os
import sys

from hypothesis import given, settings, strategies as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.engine import RuntimeEngine
from helpers.recording_adapters import RecordingAdapter, RecordingAdapterRegistry


def _equivalence_program(a: int, b: int, cond: bool) -> str:
    cond_tok = "true" if cond else "false"
    return (
        f"L1: Set a {a} Set b {b} X s add a b If {cond_tok} ->L2 ->L3\n"
        "L2: Call L4 ->c J c\n"
        "L3: X c sub s 1 J c\n"
        "L4: X z mul s 2 J z\n"
    )


@settings(max_examples=60, deadline=None)
@given(a=st.integers(min_value=-100, max_value=100), b=st.integers(min_value=-100, max_value=100), cond=st.booleans())
def test_property_steps_vs_graph_equivalence(a: int, b: int, cond: bool):
    code = _equivalence_program(a, b, cond)
    out_steps = RuntimeEngine.from_code(code, strict=True, trace=False, step_fallback=True).run_label("1")
    out_graph = RuntimeEngine.from_code(code, strict=True, trace=False, step_fallback=False).run_label("1")
    assert out_steps == out_graph


@settings(max_examples=40, deadline=None)
@given(v=st.integers(min_value=-1000, max_value=1000))
def test_property_steps_vs_graph_side_effect_log_equivalence(v: int):
    code = f"L1: R ext.echo {v} ->out J out\n"

    reg_steps = RecordingAdapterRegistry(allowed=["core", "ext"])
    reg_steps.register("ext", RecordingAdapter())
    out_steps = RuntimeEngine.from_code(code, strict=True, trace=False, adapters=reg_steps, step_fallback=True).run_label("1")

    reg_graph = RecordingAdapterRegistry(allowed=["core", "ext"])
    reg_graph.register("ext", RecordingAdapter())
    out_graph = RuntimeEngine.from_code(code, strict=True, trace=False, adapters=reg_graph, step_fallback=False).run_label("1")

    assert out_steps == out_graph
    assert reg_steps.call_log == reg_graph.call_log
