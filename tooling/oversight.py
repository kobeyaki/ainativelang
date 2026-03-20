"""
Oversight utilities: compile-time and runtime audit reports over the canonical graph IR.

Goals:
- Provide a stable, machine-readable report that agents can diff and reason about.
- Summarize graph semantics (effects, adapters, endpoints) and changes between IR versions.
- Attach execution-time evidence (trace + adapter metrics) to the graph.

All functions are pure and side-effect free.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from tooling.graph_api import (
    endpoint_entry_label,
    frame_reads,
    frame_writes,
    label_nodes,
    nodes_using_adapter,
    trace_annotate_graph,
)
from tooling.graph_diff import graph_diff
from tooling.graph_export import execution_path_stats, graph_snapshot
from tooling.ir_compact import compact_slice_snapshot
from tooling.trace_focus import trace_to_focus
from tooling.step_focus import map_step_to_node


def _endpoint_iter(ir: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
    """Return [(path, method, ep), ...] for all endpoints."""
    services = ir.get("services") or {}
    core = services.get("core") or {}
    eps = core.get("eps") or {}
    out: List[Tuple[str, str, Dict[str, Any]]] = []
    for path, methods in (eps or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, ep in methods.items():
            if isinstance(ep, dict):
                out.append((path, (method or ep.get("method", "G") or "G").upper(), ep))
    return out


def _effect_summary(ir: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate effect_summary and node effects across all labels."""
    labels = ir.get("labels") or {}
    effect_counts: Dict[str, int] = {}
    node_effect_counts: Dict[str, int] = {}
    for body in labels.values():
        summary = body.get("effect_summary") or {}
        for eff in summary.get("effects") or []:
            effect_counts[eff] = effect_counts.get(eff, 0) + 1
        for n in body.get("nodes") or []:
            eff = n.get("effect")
            if eff:
                node_effect_counts[eff] = node_effect_counts.get(eff, 0) + 1
    return {
        "label_effects": effect_counts,
        "node_effects": node_effect_counts,
    }


def _adapter_summary(ir: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize adapter use across all labels."""
    summary: Dict[str, Any] = {}
    for name in ("db", "api", "ext", "cache", "queue", "txn", "tools", "http", "fs", "auth"):
        uses = nodes_using_adapter(ir, name)
        if not uses:
            continue
        summary[name] = {
            "labels": sorted({lid for lid, _ in uses}),
            "nodes": [{"label_id": lid, "node_id": nid} for lid, nid in uses],
        }
    return summary


def _label_rw_summary(ir: Dict[str, Any]) -> Dict[str, Any]:
    """Per-label frame read/write summary."""
    labels = ir.get("labels") or {}
    out: Dict[str, Any] = {}
    for lid in sorted(labels.keys(), key=str):
        reads = sorted(frame_reads(ir, lid))
        writes = sorted(frame_writes(ir, lid))
        out[lid] = {"reads": reads, "writes": writes}
    return out


def compile_oversight_report(
    current_ir: Dict[str, Any],
    previous_ir: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a compile-time oversight report for one IR, optionally diffed against a previous IR.

    Report shape (stable, agent-facing):
      {
        "schema": { "ir_version", "graph_schema_version" },
        "summary": { counts... },
        "labels": { ... per-label rw/effects ... },
        "endpoints": [ { path, method, label_id, return_var } ],
        "adapters": { adapter_name: { labels: [...], nodes: [...] } },
        "effects": { label_effects, node_effects },
        "graph_diff": { ... }  # only when previous_ir provided
      }
    """
    ir = current_ir or {}
    labels = ir.get("labels") or {}
    services = ir.get("services") or {}

    # Basic counts.
    total_labels = len(labels)
    total_nodes = sum(len((body or {}).get("nodes") or []) for body in labels.values())
    total_edges = sum(len((body or {}).get("edges") or []) for body in labels.values())

    # Endpoint summary.
    endpoints: List[Dict[str, Any]] = []
    for path, method, ep in _endpoint_iter(ir):
        label_id = ep.get("label_id")
        if isinstance(label_id, str) and label_id.startswith("L"):
            label_id = label_id[1:]
        endpoints.append(
            {
                "path": path,
                "method": method,
                "label_id": str(label_id) if label_id is not None else None,
                "return_var": ep.get("return_var"),
            }
        )

    # Effect and adapter summaries.
    effects = _effect_summary(ir)
    adapters = _adapter_summary(ir)
    label_rw = _label_rw_summary(ir)

    graph_diff_block: Optional[Dict[str, Any]] = None
    if previous_ir is not None:
        graph_diff_block = graph_diff(previous_ir, current_ir)

    # Services/capabilities light summary (for audits).
    capabilities = ir.get("capabilities") or {}
    core = services.get("core") or {}

    report: Dict[str, Any] = {
        "schema": {
            "ir_version": ir.get("ir_version"),
            "graph_schema_version": ir.get("graph_schema_version"),
        },
        "summary": {
            "labels": total_labels,
            "nodes": total_nodes,
            "edges": total_edges,
            "endpoints": len(endpoints),
        },
        "labels": {
            "frame_rw": label_rw,
        },
        "endpoints": endpoints,
        "effects": effects,
        "adapters": adapters,
        "services": {
            "core": {
                "mode": core.get("mode"),
                "path": core.get("path"),
                "endpoint_count": len((core.get("eps") or {})),
            },
        },
        "capabilities": capabilities,
    }
    if graph_diff_block is not None:
        report["graph_diff"] = graph_diff_block
    return report


def runtime_oversight_report(
    ir: Dict[str, Any],
    run_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a runtime oversight report for a single run.

    Expects a payload similar to scripts/runtime_runner_service._run_once:
      {
        "ok": bool,
        "label": str,
        "out": any,
        "duration_ms": float,
        "runtime_version": str,
        "ir_version": str,
        "trace": [...],                # optional, list of events with node_id/port_taken
        "adapter_calls": [...],        # optional call log
        "adapter_p95_ms": { adapter: p95 },
        ...
      }

    Returns a stable audit structure focusing on:
      - outcome + latency
      - per-node execution/coverage (when node_id trace is present)
      - hot io nodes
      - adapter usage and latency
    """
    label = str(run_payload.get("label") or "")
    trace = run_payload.get("trace") or []
    adapter_calls = run_payload.get("adapter_calls") or []
    adapter_p95 = run_payload.get("adapter_p95_ms") or {}

    # Graph snapshot + path stats for this label.
    body = (ir.get("labels") or {}).get(label) or {}
    graph = graph_snapshot(ir, label) if body else None
    stats = execution_path_stats(trace, graph or {})

    # Per-node execution summary from graph_api.
    trace_ann = trace_annotate_graph(ir, trace)

    # Adapter usage summary (names + counts) from call log, if any.
    adapter_counts: Dict[str, int] = {}
    if isinstance(adapter_calls, list):
        for ev in adapter_calls:
            if isinstance(ev, dict):
                name = ev.get("adapter") or ev.get("name")
                if name:
                    adapter_counts[name] = adapter_counts.get(name, 0) + 1

    return {
        "schema": {
            "runtime_version": run_payload.get("runtime_version"),
            "ir_version": run_payload.get("ir_version"),
        },
        "summary": {
            "ok": bool(run_payload.get("ok", True)),
            "label": label,
            "duration_ms": run_payload.get("duration_ms"),
        },
        "graph": graph,
        "trace": {
            "paths": stats.get("trace_paths"),
            "coverage": stats.get("coverage"),
            "hot_io_nodes": stats.get("hot_io_nodes"),
            "per_node": trace_ann.get("labels", {}).get(label, {}),
        },
        "adapters": {
            "counts": adapter_counts,
            "p95_ms": adapter_p95,
        },
    }


def runtime_debug_envelope(
    ir: Dict[str, Any],
    run_payload: Dict[str, Any],
    *,
    trace_tail_limit: int = 64,
    slice_depth: int = 2,
) -> Dict[str, Any]:
    """
    Canonical runtime debug envelope for agents/UIs.

    Shape:
      {
        "ok": bool,
        "error": { ... } | None,
        "trace_tail": [ ... last N events ... ],
        "focus": { "label": str|None, "focus": str|int|None, "lineno": int|None, "mode": "graph"|"steps"|None },
        "slice": { ...compact_slice_snapshot... } | None,
      }
    """
    ok = bool(run_payload.get("ok", True))
    trace = run_payload.get("trace") or []
    tail = trace[-trace_tail_limit:] if trace_tail_limit and len(trace) > trace_tail_limit else trace

    label, focus_id, lineno = trace_to_focus(tail)
    mode: Optional[str] = None
    if focus_id is not None:
        # If we have a node_id in the last event, treat as graph mode; else steps.
        last_ev = tail[-1] if tail else {}
        mode = "graph" if "node_id" in last_ev else "steps"

    slice_block: Optional[Dict[str, Any]] = None
    if label is not None and focus_id is not None:
        # Graph mode: use node_id directly.
        if mode == "graph":
            try:
                slice_block = compact_slice_snapshot(ir, str(label), str(focus_id), depth=slice_depth, traces=tail)
            except Exception:
                slice_block = None
        # Steps mode: best-effort map to nearest node via lineno/op.
        elif mode == "steps":
            last_ev = tail[-1] if tail else {}
            op = last_ev.get("op")
            nid = map_step_to_node(ir, str(label), step_index=focus_id, lineno=lineno, op=op)
            if nid is not None:
                try:
                    slice_block = compact_slice_snapshot(ir, str(label), nid, depth=slice_depth, traces=tail)
                except Exception:
                    slice_block = None

    return {
        "ok": ok,
        "error": run_payload.get("error"),
        "trace_tail": tail,
        "focus": {
            "label": label,
            "focus": focus_id,
            "lineno": lineno,
            "mode": mode,
        },
        "slice": slice_block,
    }
