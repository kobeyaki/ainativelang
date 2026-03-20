"""
Tests for tooling/graph_slice.py (graph slicing and compact slice snapshots).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.graph_slice import graph_slice
from tooling.ir_compact import compact_slice_snapshot


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


def test_graph_slice_includes_start_and_neighbors():
    ir = _compile_example()
    sliced = graph_slice(ir, "1", "n1", depth=1)
    body = sliced["labels"]["1"]
    node_ids = {n.get("id") for n in body["nodes"]}
    assert "n1" in node_ids
    # depth=1 from n1 should also include n2
    assert "n2" in node_ids
    assert body["entry"] == "n1"


def test_compact_slice_snapshot_basic_shape():
    ir = _compile_example()
    snap = compact_slice_snapshot(ir, "1", "n1", depth=1, traces=[])
    assert "graph_semantic_checksum" in snap
    assert "compact" in snap
    assert snap["trace_count"] == 0
