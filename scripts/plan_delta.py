#!/usr/bin/env python3
"""
Compute high-level additive/extend/refactor/replace plan delta between IR snapshots.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _ep_keys(ir: Dict[str, Any]) -> set:
    out = set()
    core = ir.get("services", {}).get("core", {})
    eps = core.get("eps", {}) or {}
    for path, v in eps.items():
        if isinstance(v, dict) and ("label_id" in v or "method" in v):
            out.add((path, (v.get("method") or "G").upper()))
        elif isinstance(v, dict):
            for m, ep in v.items():
                if isinstance(ep, dict):
                    out.add((path, str(m).upper()))
    return out


def _type_keys(ir: Dict[str, Any]) -> set:
    return set((ir.get("types") or {}).keys())


def _label_keys(ir: Dict[str, Any]) -> set:
    return set((ir.get("labels") or {}).keys())


def compute_plan_delta(base_ir: Dict[str, Any], new_ir: Dict[str, Any]) -> Dict[str, Any]:
    be, ne = _ep_keys(base_ir), _ep_keys(new_ir)
    bt, nt = _type_keys(base_ir), _type_keys(new_ir)
    bl, nl = _label_keys(base_ir), _label_keys(new_ir)

    def _pack(add: set, rem: set) -> Dict[str, List[Any]]:
        return {"added": sorted(list(add)), "removed": sorted(list(rem))}

    eps = _pack(ne - be, be - ne)
    types = _pack(nt - bt, bt - nt)
    labels = _pack(nl - bl, bl - nl)
    breaking = bool(eps["removed"] or types["removed"] or labels["removed"])

    actions: List[Dict[str, Any]] = []
    for x in eps["added"]:
        actions.append({"kind": "add", "target": "endpoint", "value": x})
    for x in types["added"]:
        actions.append({"kind": "add", "target": "type", "value": x})
    for x in labels["added"]:
        actions.append({"kind": "add", "target": "label", "value": x})
    for x in eps["removed"]:
        actions.append({"kind": "replace", "target": "endpoint", "value": x})
    for x in types["removed"]:
        actions.append({"kind": "replace", "target": "type", "value": x})
    for x in labels["removed"]:
        actions.append({"kind": "replace", "target": "label", "value": x})

    return {
        "breaking": breaking,
        "endpoints": eps,
        "types": types,
        "labels": labels,
        "actions": actions,
    }
