"""
Best-effort mapping from legacy step traces to graph nodes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from tooling.graph_api import label_nodes


def map_step_to_node(
    ir: Dict[str, Any],
    label_id: str,
    *,
    step_index: Optional[int] = None,
    lineno: Optional[int] = None,
    op: Optional[str] = None,
) -> Optional[str]:
    """
    Heuristic mapping from a step (label, step_index, lineno, op) to a graph node id.

    Strategy:
      1) Prefer nodes whose data.lineno equals lineno, and whose op matches.
      2) Fallback to any node with matching lineno.
      3) Fallback to nearest preceding lineno.
      4) If still ambiguous, return None.
    """
    nodes = label_nodes(ir, label_id)
    if not nodes:
        return None

    def _n_lineno(n: Dict[str, Any]) -> Optional[int]:
        d = n.get("data") or {}
        ln = d.get("lineno", n.get("lineno"))
        try:
            return int(ln) if ln is not None else None
        except Exception:
            return None

    def _n_op(n: Dict[str, Any]) -> Optional[str]:
        return n.get("op") or (n.get("data") or {}).get("op")

    entries: List[tuple] = []
    for nid, n in nodes.items():
        entries.append((nid, _n_lineno(n), _n_op(n)))

    if lineno is not None:
        # Exact lineno + op match.
        if op is not None:
            for nid, ln, nop in entries:
                if ln == lineno and nop == op:
                    return nid
        # Any node with same lineno.
        for nid, ln, _ in entries:
            if ln == lineno:
                return nid
        # Nearest preceding lineno.
        preceding = [(nid, ln) for nid, ln, _ in entries if ln is not None and ln < lineno]
        if preceding:
            preceding.sort(key=lambda x: x[1], reverse=True)
            return preceding[0][0]

    return None


__all__ = ["map_step_to_node"]
