#!/usr/bin/env python3
"""
Safe patch-mode IR merge: additive/extend-first, fail on conflict unless explicit replace.
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple


def _iter_eps(eps: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
    out: List[Tuple[str, str, Dict[str, Any]]] = []
    for path, v in (eps or {}).items():
        if isinstance(v, dict) and ("label_id" in v or "method" in v):
            out.append((path, str(v.get("method", "G")).upper(), v))
        elif isinstance(v, dict):
            for m, ep in v.items():
                if isinstance(ep, dict):
                    out.append((path, str(m).upper(), ep))
    return out


def _set_ep(eps: Dict[str, Any], path: str, method: str, ep: Dict[str, Any]) -> None:
    eps.setdefault(path, {})
    if isinstance(eps[path], dict) and ("label_id" in eps[path] or "method" in eps[path]):
        cur = eps[path]
        eps[path] = {str(cur.get("method", "G")).upper(): cur}
    eps[path][method] = ep


def apply_patch_ir(base_ir: Dict[str, Any], patch_ir: Dict[str, Any], allow_replace: bool = False) -> Dict[str, Any]:
    out = copy.deepcopy(base_ir)
    conflicts: List[str] = []

    # Services (core endpoints + capability defs)
    out_services = out.setdefault("services", {})
    p_services = patch_ir.get("services", {})

    base_core = out_services.setdefault("core", {"eps": {}, "ui": {}})
    patch_core = p_services.get("core", {})
    base_eps = base_core.setdefault("eps", {})
    for path, method, ep in _iter_eps(patch_core.get("eps", {})):
        has_existing = any((p == path and m == method) for p, m, _ in _iter_eps(base_eps))
        if has_existing and not allow_replace:
            conflicts.append(f"endpoint conflict: {method} {path}")
            continue
        _set_ep(base_eps, path, method, ep)

    # Merge other service buckets conservatively.
    for srv_name, srv_val in p_services.items():
        if srv_name == "core":
            continue
        if srv_name not in out_services:
            out_services[srv_name] = copy.deepcopy(srv_val)
            continue
        if isinstance(srv_val, dict) and isinstance(out_services[srv_name], dict):
            for k, v in srv_val.items():
                if k not in out_services[srv_name]:
                    out_services[srv_name][k] = copy.deepcopy(v)
                elif out_services[srv_name][k] != v and not allow_replace:
                    conflicts.append(f"service conflict: {srv_name}.{k}")
                elif allow_replace:
                    out_services[srv_name][k] = copy.deepcopy(v)

    # Types
    out_types = out.setdefault("types", {})
    for t, td in (patch_ir.get("types") or {}).items():
        if t in out_types and out_types[t] != td and not allow_replace:
            conflicts.append(f"type conflict: {t}")
            continue
        out_types[t] = copy.deepcopy(td)

    # Labels
    out_labels = out.setdefault("labels", {})
    for lid, body in (patch_ir.get("labels") or {}).items():
        if lid in out_labels and out_labels[lid] != body and not allow_replace:
            conflicts.append(f"label conflict: {lid}")
            continue
        out_labels[lid] = copy.deepcopy(body)

    return {"ok": len(conflicts) == 0, "ir": out, "conflicts": conflicts}
