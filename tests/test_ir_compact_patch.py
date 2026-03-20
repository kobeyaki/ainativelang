"""
Tests for tooling/ir_compact_patch.py (compact patch DSL over graphs).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.ir_compact_patch import apply_compact_patches, parse_compact_patches


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


def test_parse_compact_patches_rewire_and_setnode():
    text = "P REWIRE label=1 from=n1 port=next to=n2 kind=node\n" "P SETNODE label=1 node=n2 data={\"var\":\"quote\"}\n"
    patches = parse_compact_patches(text)
    assert len(patches) == 2
    assert patches[0]["op"] == "rewire_edge"
    assert patches[1]["op"] == "set_node_data"


def test_apply_compact_patches_sets_node_data_and_rewires():
    ir = _compile_example()
    text = "\n".join(
        [
            "P SETNODE label=1 node=n2 data={\"var\":\"result\"}",
            "P REWIRE label=1 from=n1 port=next to=n2 kind=node",
        ]
    )
    res = apply_compact_patches(ir, text)
    assert res["ok"], res.get("error")
    new_ir = res["ir"]
    label = new_ir["labels"]["1"]
    n2 = next(n for n in label["nodes"] if n.get("id") == "n2")
    assert n2.get("data", {}).get("var") == "result"
    # Edge from n1 next should still point to n2.
    assert any(e.get("from") == "n1" and (e.get("port") or "next") == "next" and e.get("to") == "n2" for e in label["edges"])


def test_apply_compact_patches_by_hash_and_preconditions():
    ir = _compile_example()
    label = ir["labels"]["1"]
    n2 = next(n for n in label["nodes"] if n.get("op") == "J")
    n2_hash = n2["hash"]
    checksum = ir["graph_semantic_checksum"]
    label_hash = label["id_hash"]
    text = "\n".join(
        [
            f"P SETNODE label=1 node_hash={n2_hash} requires_checksum={checksum} requires_label_hash={label_hash} data={{\"var\":\"by_hash\"}}",
        ]
    )
    res = apply_compact_patches(ir, text)
    assert res["ok"], res.get("error")
    new_ir = res["ir"]
    new_n2 = next(n for n in new_ir["labels"]["1"]["nodes"] if n.get("id") == n2["id"])
    assert new_n2.get("data", {}).get("var") == "by_hash"
