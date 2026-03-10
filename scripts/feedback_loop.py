#!/usr/bin/env python3
"""
Failure-to-fix feedback helper for targeted retry loops.
"""
from __future__ import annotations

from typing import Any, Dict, List


CODE_HINTS = {
    "CONTRACT_VIOLATION": "Align endpoint signature with declared Contract path/method/response_type.",
    "POLICY_VIOLATION": "Add/fix auth/role/policy declarations and ensure Enf points to valid policy.",
    "COMPAT_BREAK": "Avoid removals; prefer additive changes or explicit replace mode.",
    "PATCH_CONFLICT": "Regenerate as additive patch, or mark intended replacement explicitly.",
}


def collect_feedback(result: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[Dict[str, str]] = []
    for key in ("compat", "policy"):
        block = result.get(key) or {}
        if key == "compat" and not block.get("ok", True):
            for br in block.get("breaks", []) or []:
                issues.append({"code": "COMPAT_BREAK", "detail": br})
        if key == "policy" and not block.get("ok", True):
            for v in block.get("violations", []) or []:
                issues.append({"code": "POLICY_VIOLATION", "detail": v})
    if not (result.get("patch", {}) or {}).get("ok", True):
        for c in (result.get("patch", {}) or {}).get("conflicts", []) or []:
            issues.append({"code": "PATCH_CONFLICT", "detail": c})
    if not (result.get("contracts", {}) or {}).get("ok", True):
        for c in (result.get("contracts", {}) or {}).get("violations", []) or []:
            issues.append({"code": "CONTRACT_VIOLATION", "detail": c})

    return {
        "issues": issues,
        "hints": [{"code": i["code"], "hint": CODE_HINTS.get(i["code"], "Fix reported violations and retry.")}
                  for i in issues],
        "retry_recommended": len(issues) > 0,
    }
