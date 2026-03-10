"""
Export IR graphs and traces to JSONL for audit / training. One line per record: {endpoint, graph, traces}.
When traces include node_id (graph-native tracing), each record also gets trace_paths, coverage, hot_io_nodes.
"""
import json
from typing import Any, Dict, List, Optional, TextIO, Tuple

from tooling.graph_api import endpoint_entry_label, label_edges, label_nodes


def execution_path_stats(
    traces: List[Dict[str, Any]],
    graph: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    From graph-native trace events (with node_id), compute:
    - trace_paths: list of node_id sequences (one path per contiguous run)
    - coverage: per-node execution counts
    - hot_io_nodes: io nodes ranked by execution count then by total duration_ms
    """
    path: List[str] = []
    paths: List[List[str]] = []
    coverage: Dict[str, int] = {}
    duration_by_node: Dict[str, float] = {}
    for e in traces or []:
        nid = e.get("node_id")
        if nid:
            path.append(nid)
            coverage[nid] = coverage.get(nid, 0) + 1
            duration_by_node[nid] = duration_by_node.get(nid, 0.0) + float(e.get("duration_ms") or 0)
        else:
            if path:
                paths.append(path)
                path = []
    if path:
        paths.append(path)
    node_by_id = {}
    if graph and graph.get("nodes"):
        node_by_id = {n.get("id"): n for n in graph["nodes"] if n.get("id")}
    io_nodes = [nid for nid in node_by_id if (node_by_id.get(nid) or {}).get("effect") == "io"]
    hot = [(nid, coverage.get(nid, 0), duration_by_node.get(nid, 0.0)) for nid in io_nodes]
    hot.sort(key=lambda x: (-x[1], -x[2]))
    hot_io_nodes = [{"node_id": nid, "count": c, "total_duration_ms": d} for nid, c, d in hot]
    return {
        "trace_paths": paths,
        "coverage": coverage,
        "hot_io_nodes": hot_io_nodes,
    }


def _iter_endpoints(ir: Dict[str, Any]) -> List[tuple]:
    """(path, method) for each endpoint in ir."""
    out: List[Tuple[str, str]] = []
    core = (ir.get("services") or {}).get("core") or {}
    eps = core.get("eps") or {}
    for path, methods in (eps or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, ep in methods.items():
            if isinstance(ep, dict):
                out.append((path, (method or "G").upper()))
    return out


def graph_snapshot(ir: Dict[str, Any], label_id: str) -> Dict[str, Any]:
    """Minimal graph snapshot for one label: nodes, edges, entry, exits."""
    body = (ir.get("labels") or {}).get(str(label_id)) or {}
    return {
        "label_id": label_id,
        "nodes": body.get("nodes") or [],
        "edges": body.get("edges") or [],
        "entry": body.get("entry"),
        "exits": body.get("exits") or [],
    }


def export_jsonl(
    ir: Dict[str, Any],
    traces_by_endpoint: Optional[Dict[Tuple[str, str], List[Dict[str, Any]]]] = None,
    *,
    stream: Optional[TextIO] = None,
) -> List[str]:
    """
    Emit one JSONL record per endpoint: {endpoint: {path, method}, graph: {...}, traces: [...]}.
    If stream is provided, write each line to it. Returns list of lines (for in-memory use).
    traces_by_endpoint: optional {(path, method): [trace_events]}.
    """
    lines: List[str] = []
    traces_by_endpoint = traces_by_endpoint or {}
    for path, method in _iter_endpoints(ir):
        label_id = endpoint_entry_label(ir, path, method)
        graph = graph_snapshot(ir, label_id) if label_id else None
        traces = traces_by_endpoint.get((path, method), traces_by_endpoint.get((path, method.upper()), []))
        record = {
            "endpoint": {"path": path, "method": method},
            "graph": graph,
            "traces": traces,
        }
        if any(e.get("node_id") for e in traces):
            stats = execution_path_stats(traces, graph)
            record["trace_paths"] = stats["trace_paths"]
            record["coverage"] = stats["coverage"]
            record["hot_io_nodes"] = stats["hot_io_nodes"]
        line = json.dumps(record, ensure_ascii=False, default=str)
        lines.append(line)
        if stream is not None:
            stream.write(line + "\n")
    return lines
