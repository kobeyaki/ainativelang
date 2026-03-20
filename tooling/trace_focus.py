"""
Helpers for deriving an execution focus point from trace events.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def trace_to_focus(traces: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[object], Optional[int]]:
    """
    Given a list of runtime trace events, return a suggested focus triple:

      (label_id, node_id_or_step_index, lineno)

    - Prefers graph-node focus (node_id) when present.
    - Falls back to step index when running in legacy steps mode.
    - Returns (None, None, None) when traces is empty.
    """
    if not traces:
        return None, None, None
    ev = traces[-1]
    label = ev.get("label")
    node_id = ev.get("node_id")
    step = ev.get("step")
    lineno = ev.get("lineno")
    focus_id: Optional[object] = node_id if node_id is not None else step
    return label, focus_id, lineno


__all__ = ["trace_to_focus"]
