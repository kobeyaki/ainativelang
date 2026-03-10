"""
Tests for tooling/ir_canonical.py: canonicalization and semantic hashes.
Run: pytest tests/test_ir_canonical.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.ir_canonical import (
    attach_label_and_node_hashes,
    canonicalize_ir,
    graph_semantic_checksum,
)


def _simple_ir():
    c = AICodeCompiler()
    ir = c.compile("S core web /api\nE /x G ->L1 ->data\nL1: R db.F User * ->data J data\n")
    assert not ir.get("errors"), ir.get("errors")
    return ir


def test_canonicalize_ir_stable_labels_nodes_edges():
    ir = _simple_ir()
    canon1 = canonicalize_ir(ir)
    canon2 = canonicalize_ir(ir)
    assert canon1 == canon2
    # labels keys sorted and nodes sorted by id
    lids = list((canon1.get("labels") or {}).keys())
    assert lids == sorted(lids, key=str)
    nodes = canon1["labels"]["1"]["nodes"]
    ids = [n["id"] for n in nodes]
    assert ids == sorted(ids, key=str)


def test_attach_hashes_adds_label_and_node_hashes():
    ir = _simple_ir()
    ir = attach_label_and_node_hashes(ir)
    lbl = ir["labels"]["1"]
    assert "id_hash" in lbl
    assert lbl["id_hash"].startswith("sha256:")
    for n in lbl["nodes"]:
        assert "hash" in n
        assert n["hash"].startswith("sha256:")


def test_graph_semantic_checksum_stable_across_reordering():
    ir = _simple_ir()
    c1 = graph_semantic_checksum(ir)
    # Reorder nodes manually and ensure checksum does not change.
    lbl = ir["labels"]["1"]
    lbl["nodes"] = list(reversed(lbl["nodes"]))
    c2 = graph_semantic_checksum(ir)
    assert c1 == c2

