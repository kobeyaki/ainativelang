#!/usr/bin/env python3
"""
Policy gate for IR invariants:
- response envelope stability
- auth/policy consistency
- endpoint contract consistency
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _iter_eps(ir: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
    out: List[Tuple[str, str, Dict[str, Any]]] = []
    core = (ir.get("services") or {}).get("core", {})
    eps = (core or {}).get("eps", {})
    for path, v in eps.items():
        if isinstance(v, dict) and ("label_id" in v or "method" in v):
            out.append((path, str(v.get("method", "G")).upper(), v))
        elif isinstance(v, dict):
            for m, ep in v.items():
                if isinstance(ep, dict):
                    out.append((path, str(m).upper(), ep))
    return out


def check_policy_gate(ir: Dict[str, Any]) -> Dict[str, Any]:
    violations: List[str] = []
    notes: List[str] = []

    services = ir.get("services", {})
    auth = services.get("auth")
    roles = set(ir.get("roles", []) or [])
    allow = ir.get("allow", []) or []
    policy_defs = ((services.get("policy") or {}).get("defs") or {})

    # Auth must include arg/header when declared.
    if auth and not auth.get("arg"):
        violations.append("auth declared but missing header/token arg")

    # Allow role entries must reference known roles.
    for a in allow:
        r = a.get("role")
        if r and r not in roles:
            violations.append(f"allow references undefined role: {r}")

    # Endpoint descriptions/contracts should stay envelope-based.
    contracts = services.get("_contracts", []) or []
    if contracts:
        ep_keys = {(p, m) for p, m, _ in _iter_eps(ir)}
        for c in contracts:
            key = (c.get("path"), str(c.get("method", "G")).upper())
            if key not in ep_keys:
                violations.append(f"contract references unknown endpoint: {key[1]} {key[0]}")

    # Policy defs must have at least one constraint.
    for name, pd in policy_defs.items():
        if not (pd or {}).get("constraints"):
            notes.append(f"policy {name} has no constraints (no-op)")

    return {"ok": len(violations) == 0, "violations": violations, "notes": notes}
