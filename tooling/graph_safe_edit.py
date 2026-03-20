"""
Safe graph edit entrypoints for agents.

This module wraps `tooling.graph_rewrite.apply_patch` with:
- deterministic normalize + effect-analysis + light graph validation (via graph_rewrite)
- graph diff (`tooling.graph_diff.graph_diff`) between old/new IR
- a minimal oversight report surface: which labels/endpoints changed and a human_summary

Contract for agents:

    result = safe_apply_patch(ir, patch)

Returns:
    {
        "ok": True,
        "ir": new_ir,
        "diff": { ... },      # output of graph_diff(old_ir, new_ir, label_id=patch.get("label_id"))
        "report": {           # minimal oversight surface
            "label_ids": [...],
            "endpoints_affected": [ {"path": str, "method": str, "label_id": str} ],
            "human_summary": str,
            "per_label_summary": [str],
        },
    }
or, on failure:
    {
        "ok": False,
        "error": { "code": str, "message": str, "details": list },
    }

Agents SHOULD treat any ok=False as "do not use this IR".
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

from tooling.graph_diff import graph_diff
from tooling.graph_export import export_jsonl
from tooling.graph_rewrite import apply_patch


def _labels_to_endpoints(ir: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    Build mapping {label_id: [{"path": path, "method": method}]} from IR services.core.eps.
    """
    out: Dict[str, List[Dict[str, str]]] = {}
    core = (ir.get("services") or {}).get("core") or {}
    eps = core.get("eps") or {}
    for path, methods in (eps or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, ep in methods.items():
            if not isinstance(ep, dict):
                continue
            lid = ep.get("label_id")
            if lid is None:
                continue
            # Normalize label id to bare numeric string (e.g. "1")
            lid_str = str(lid).lstrip("L").split(":")[-1]
            method_str = (ep.get("method") or method or "G").upper()
            out.setdefault(lid_str, []).append({"path": path, "method": method_str, "label_id": lid_str})
    return out


def _build_oversight_report(
    old_ir: Dict[str, Any],
    new_ir: Dict[str, Any],
    diff: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Minimal oversight surface for humans/agents:
    - which label ids changed
    - which endpoints (path, method) reference those labels
    - human_summary / per_label_summary from graph_diff

    Note: JSONL export is intentionally left to callers (via tooling.graph_export.export_jsonl)
    so they can choose which traces to attach.
    """
    changed_label_ids: List[str] = []
    for bucket in ("added_nodes", "removed_nodes", "added_edges", "removed_edges", "rewired_edges"):
        for item in diff.get(bucket) or []:
            lid = item.get("label_id")
            if lid is not None:
                lid_str = str(lid)
                if lid_str not in changed_label_ids:
                    changed_label_ids.append(lid_str)
    for (lid, _nid) in (diff.get("changed_nodes") or {}).keys():
        lid_str = str(lid)
        if lid_str not in changed_label_ids:
            changed_label_ids.append(lid_str)

    labels_to_eps = _labels_to_endpoints(new_ir)
    endpoints_affected: List[Dict[str, str]] = []
    for lid in changed_label_ids:
        for ep in labels_to_eps.get(lid, []):
            endpoints_affected.append(ep)

    return {
        "label_ids": changed_label_ids,
        "endpoints_affected": endpoints_affected,
        "human_summary": diff.get("human_summary"),
        "per_label_summary": diff.get("per_label_summary") or [],
    }


def safe_apply_patch(
    ir: Dict[str, Any],
    patch: Dict[str, Any],
    *,
    normalize: bool = True,
    re_annotate_effects: bool = True,
    strict_validate: bool = True,
) -> Dict[str, Any]:
    """
    Apply a structured graph patch with normalization, effect-analysis, strict validation,
    and a graph diff + minimal oversight report.

    This is the primary entrypoint agents should use when editing graphs.
    """
    try:
        old_ir = copy.deepcopy(ir)
    except Exception as e:  # pragma: no cover - extremely unlikely, but we surface it explicitly
        return {
            "ok": False,
            "error": {"code": "SAFE_COPY", "message": str(e), "details": []},
        }

    new_ir, err = apply_patch(
        ir,
        patch,
        normalize=normalize,
        re_annotate_effects=re_annotate_effects,
        strict_validate=strict_validate,
    )
    if err:
        return {"ok": False, "error": err}

    # Restrict diff to the target label when given; otherwise diff all labels.
    label_id = patch.get("label_id")
    diff = graph_diff(old_ir, new_ir, label_id=str(label_id)) if label_id is not None else graph_diff(old_ir, new_ir)
    report = _build_oversight_report(old_ir, new_ir, diff)

    return {
        "ok": True,
        "ir": new_ir,
        "diff": diff,
        "report": report,
    }


__all__ = ["safe_apply_patch"]
