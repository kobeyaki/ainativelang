#!/usr/bin/env python3
"""
Compatibility gate for IR changes (endpoint stability + type compatibility).
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _iter_eps(ir: Dict[str, Any]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for _srv, data in (ir.get("services") or {}).items():
        eps = (data or {}).get("eps", {})
        for path, v in eps.items():
            if isinstance(v, dict) and ("label_id" in v or "method" in v):
                out.append((path, str(v.get("method", "G")).upper()))
            elif isinstance(v, dict):
                for m, ep in v.items():
                    if isinstance(ep, dict):
                        out.append((path, str(m).upper()))
    return out


def _type_fields(ir: Dict[str, Any]) -> Dict[str, set]:
    out: Dict[str, set] = {}
    for name, td in (ir.get("types") or {}).items():
        out[name] = set((td or {}).get("fields", {}).keys())
    return out


def check_compat_gate(base_ir: Dict[str, Any], new_ir: Dict[str, Any], mode: str = "add") -> Dict[str, Any]:
    mode = (mode or "add").strip().lower()
    base_eps = set(_iter_eps(base_ir))
    new_eps = set(_iter_eps(new_ir))
    base_types = _type_fields(base_ir)
    new_types = _type_fields(new_ir)

    breaks: List[str] = []
    notes: List[str] = []

    for ep in sorted(base_eps - new_eps):
        breaks.append(f"endpoint removed: {ep[1]} {ep[0]}")
    for ep in sorted(new_eps - base_eps):
        notes.append(f"endpoint added: {ep[1]} {ep[0]}")

    for t, fields in base_types.items():
        if t not in new_types:
            breaks.append(f"type removed: {t}")
            continue
        removed_fields = fields - new_types[t]
        if removed_fields:
            breaks.append(f"type {t}: removed fields {sorted(list(removed_fields))}")
    for t in sorted(set(new_types.keys()) - set(base_types.keys())):
        notes.append(f"type added: {t}")

    ok = not (mode == "add" and breaks)
    return {"ok": ok, "mode": mode, "breaks": breaks, "notes": notes}
