#!/usr/bin/env python3
"""
Contract gate checks for declared Contract ops against current endpoints.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _iter_eps(ir: Dict[str, Any]) -> set:
    out = set()
    core = (ir.get("services") or {}).get("core", {})
    eps = (core or {}).get("eps", {})
    for path, v in eps.items():
        if isinstance(v, dict) and ("label_id" in v or "method" in v):
            out.add((path, str(v.get("method", "G")).upper()))
        elif isinstance(v, dict):
            for m, ep in v.items():
                if isinstance(ep, dict):
                    out.add((path, str(m).upper()))
    return out


def check_contracts(ir: Dict[str, Any]) -> Dict[str, Any]:
    violations: List[str] = []
    eps = _iter_eps(ir)
    contracts = (ir.get("services", {}) or {}).get("_contracts", []) or []
    for c in contracts:
        path = c.get("path")
        method = str(c.get("method", "G")).upper()
        if (path, method) not in eps:
            violations.append(f"contract missing endpoint: {method} {path}")
    return {"ok": len(violations) == 0, "violations": violations}
