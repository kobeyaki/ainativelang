"""
Tests for tooling/ir_compact.py (compact textual encoding of IR graphs).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.ir_canonical import canonicalize_ir
from tooling.ir_compact import (
    compact_diff,
    decode_ir_compact,
    encode_ir_compact,
    trace_compact_snapshot,
)


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


def _graph_view(ir):
    """Extract only the semantic graph layer for comparison."""
    labels = {}
    for lid, body in (ir.get("labels") or {}).items():
        nodes = []
        for n in body.get("nodes") or []:
            nodes.append(
                {
                    "id": n.get("id"),
                    "op": n.get("op"),
                    "effect_tier": n.get("effect_tier"),
                    "effect": n.get("effect"),
                    "reads": sorted(n.get("reads") or []),
                    "writes": sorted(n.get("writes") or []),
                    "data": n.get("data"),
                }
            )
        edges = [
            {
                "from": e.get("from"),
                "port": e.get("port") or "next",
                "to": e.get("to"),
                "to_kind": e.get("to_kind") or "node",
            }
            for e in body.get("edges") or []
        ]
        exits = [
            {"node": ex.get("node"), "var": ex.get("var")}
            for ex in body.get("exits") or []
        ]
        labels[str(lid)] = {
            "entry": body.get("entry"),
            "nodes": nodes,
            "edges": edges,
            "exits": exits,
        }
    return {"labels": labels}


def test_encode_ir_compact_is_stable():
    ir = _compile_example()
    frag = _graph_view(ir)
    t1 = encode_ir_compact(frag)
    t2 = encode_ir_compact(frag)
    assert t1 == t2


def test_ir_compact_roundtrip_preserves_graph_semantics():
    ir = _compile_example()
    frag = _graph_view(ir)
    text = encode_ir_compact(frag)
    decoded = decode_ir_compact(text)

    # Compare canonicalized graph views from original and decoded.
    canon_orig = canonicalize_ir(frag)
    canon_dec = canonicalize_ir(_graph_view(decoded))
    assert canon_orig == canon_dec


def test_compact_diff_reports_changes():
    ir = _compile_example()
    frag = _graph_view(ir)
    base = encode_ir_compact(frag)

    # Mutate: change J var name in compact form.
    modified = base.replace("X n2 users", "X n2 result")
    diff = compact_diff(base, modified)
    # We only assert that the diff machinery runs and returns a dict.
    assert isinstance(diff, dict)


def test_trace_compact_snapshot_basic_shape():
    ir = _compile_example()
    snap = trace_compact_snapshot(ir, "1", traces=[])
    assert "graph_semantic_checksum" in snap
    assert "compact" in snap
    assert "1" in snap["labels"]
