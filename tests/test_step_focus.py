"""
Tests for tooling/step_focus.py (step -> node mapping).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.step_focus import map_step_to_node


def _compile_example():
    c = AICodeCompiler()
    code = """
S core web /api
E /users G ->L1 ->users
L1: R db.F User * ->users J users
"""
    ir = c.compile(code.strip() + "\n")
    assert not ir.get("errors"), ir.get("errors")
    return ir


def test_map_step_to_node_by_lineno_and_op():
    ir = _compile_example()
    # Both R and J are on same lineno=3; check mapping for each op.
    nid_r = map_step_to_node(ir, "1", lineno=3, op="R")
    nid_j = map_step_to_node(ir, "1", lineno=3, op="J")
    assert nid_r != nid_j
    assert {nid_r, nid_j} == {"n1", "n2"}


def test_map_step_to_node_preceding_lineno():
    ir = _compile_example()
    # Ask for lineno beyond any node; should pick nearest preceding.
    nid = map_step_to_node(ir, "1", lineno=10, op=None)
    assert nid in {"n1", "n2"}

