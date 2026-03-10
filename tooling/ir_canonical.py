"""
Canonical IR utilities for AINL.

Single source of truth for:
- deterministic label/node/edge ordering
- semantic checksum computation
- stable label/node content hashes
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Tuple


SEMANTIC_NODE_KEYS: Tuple[str, ...] = ("id", "op", "effect", "effect_tier", "reads", "writes", "data")


def _canonical_node(node: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k in SEMANTIC_NODE_KEYS:
        if k in node and node[k] is not None:
            v = node[k]
            if k in ("reads", "writes") and isinstance(v, list):
                out[k] = sorted(v)
            else:
                out[k] = v
    return out


def _canonical_edge(edge: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "from": edge.get("from"),
        "to": edge.get("to"),
        "to_kind": edge.get("to_kind", "node"),
        "port": edge.get("port") or "next",
    }


def _canonical_label(body: Dict[str, Any]) -> Dict[str, Any]:
    nodes = body.get("nodes") or []
    edges = body.get("edges") or []
    exits = body.get("exits") or []

    canon_nodes = sorted(
        (_canonical_node(n) for n in nodes if isinstance(n, dict) and n.get("id")),
        key=lambda n: str(n.get("id")),
    )
    canon_edges = sorted(
        (_canonical_edge(e) for e in edges if isinstance(e, dict)),
        key=lambda e: (
            str(e.get("from")),
            str(e.get("port") or "next"),
            str(e.get("to")),
            str(e.get("to_kind", "node")),
        ),
    )
    canon_exits = sorted(
        (
            {"node": ex.get("node"), "var": ex.get("var")}
            for ex in exits
            if isinstance(ex, dict)
        ),
        key=lambda ex: (str(ex.get("node")), str(ex.get("var"))),
    )
    return {
        "entry": body.get("entry"),
        "nodes": canon_nodes,
        "edges": canon_edges,
        "exits": canon_exits,
    }


def canonicalize_ir(ir: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a deep-copied IR with deterministic ordering.

    Canonicalization applies to labels and graph fields only; unrelated top-level
    metadata is preserved.
    """
    out = copy.deepcopy(ir or {})
    labels = out.get("labels") or {}
    canon_labels: Dict[str, Any] = {}
    for lid in sorted(labels.keys(), key=str):
        body = labels.get(lid) or {}
        canon = _canonical_label(body)
        canon_labels[str(lid)] = {
            **body,
            "entry": canon["entry"],
            "nodes": canon["nodes"],
            "edges": canon["edges"],
            "exits": canon["exits"],
        }
    out["labels"] = canon_labels
    return out


def _semantic_view(ir: Dict[str, Any]) -> Dict[str, Any]:
    labels = ir.get("labels") or {}
    return {
        "labels": {
            str(lid): _canonical_label(body or {})
            for lid, body in labels.items()
        }
    }


def graph_semantic_checksum(ir: Dict[str, Any]) -> str:
    canon = canonicalize_ir(_semantic_view(ir or {}))
    payload = json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def attach_label_and_node_hashes(ir: Dict[str, Any]) -> Dict[str, Any]:
    labels = (ir or {}).get("labels") or {}
    for _, body in labels.items():
        canon_label = _canonical_label(body or {})
        payload = json.dumps(canon_label, sort_keys=True, separators=(",", ":")).encode("utf-8")
        body["id_hash"] = "sha256:" + hashlib.sha256(payload).hexdigest()
        for n in body.get("nodes") or []:
            if not isinstance(n, dict):
                continue
            canon_node = _canonical_node(n)
            npayload = json.dumps(canon_node, sort_keys=True, separators=(",", ":")).encode("utf-8")
            n["hash"] = "sha256:" + hashlib.sha256(npayload).hexdigest()
    return ir


# Backward-compatible aliases (legacy names).
def semantic_checksum(ir: Dict[str, Any]) -> str:
    return graph_semantic_checksum(ir)


def annotate_hashes(ir: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(ir or {})
    out = attach_label_and_node_hashes(out)
    out["graph_semantic_checksum"] = graph_semantic_checksum(out)
    return out


__all__ = [
    "canonicalize_ir",
    "graph_semantic_checksum",
    "attach_label_and_node_hashes",
    "semantic_checksum",
    "annotate_hashes",
]

