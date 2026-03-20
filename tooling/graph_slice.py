"""
Graph slicing utilities: extract minimal subgraphs around a node.

Used for agent-facing debug/context exports (compact slices around errors).
"""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, List, Set, Tuple


def graph_slice(
    ir: Dict[str, Any],
    label_id: str,
    start_node_id: str,
    *,
    depth: int = 2,
    include_err: bool = True,
) -> Dict[str, Any]:
    """
    Produce a sliced IR fragment around a given node within a label.

    Returns:
      {"labels": {label_id: {"entry": start_node_id, "nodes": [...], "edges": [...], "exits": [...]}}}
    """
    labels = ir.get("labels") or {}
    lid = str(label_id)
    body = (labels.get(lid) or {}).copy()
    nodes = list(body.get("nodes") or [])
    edges = list(body.get("edges") or [])
    exits = list(body.get("exits") or [])

    node_ids: Set[str] = {n.get("id") for n in nodes if n.get("id")}
    if start_node_id not in node_ids:
        raise KeyError(f"start_node_id {start_node_id!r} not found in label {lid!r}")

    # Build adjacency by (from, port) -> to.
    adj: Dict[str, List[Tuple[str, str]]] = {}
    for e in edges:
        if e.get("to_kind", "node") != "node":
            continue
        fr = e.get("from")
        to = e.get("to")
        port = e.get("port") or "next"
        if not fr or not to:
            continue
        adj.setdefault(fr, []).append((port, to))

    # BFS over node graph up to depth.
    visited: Set[str] = set()
    q: Deque[Tuple[str, int]] = deque()
    visited.add(start_node_id)
    q.append((start_node_id, 0))
    while q:
        cur, d = q.popleft()
        if d >= depth:
            continue
        for port, nxt in adj.get(cur, []):
            if not include_err and port == "err":
                continue
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, d + 1))

    # If include_err, ensure err-port edges from visited nodes and their targets are not dropped,
    # even if they lie just beyond the depth horizon.
    if include_err:
        for e in edges:
            if (e.get("port") or "next") == "err" and e.get("from") in visited:
                if e.get("to_kind", "node") == "node" and e.get("to"):
                    visited.add(e.get("to"))

    sliced_nodes = [n for n in nodes if n.get("id") in visited]
    sliced_edges: List[Dict[str, Any]] = []
    for e in edges:
        fr = e.get("from")
        to_kind = e.get("to_kind", "node")
        to = e.get("to")
        if fr not in visited:
            continue
        if to_kind == "node" and to not in visited:
            continue
        sliced_edges.append(e)

    sliced_exits = [ex for ex in exits if ex.get("node") in visited]

    return {
        "labels": {
            lid: {
                "entry": start_node_id,
                "nodes": sliced_nodes,
                "edges": sliced_edges,
                "exits": sliced_exits,
            }
        }
    }


__all__ = ["graph_slice"]
