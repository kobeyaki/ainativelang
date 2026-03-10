#!/usr/bin/env python3
"""
Structured tool API CLI for agent loops.

Usage examples:
  echo '{"action":"compile","code":"S core web /api"}' | ainl-tool-api
  ainl-tool-api --request-file request.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler
from scripts.compat_gate import check_compat_gate
from scripts.contracts_gate import check_contracts
from scripts.feedback_loop import collect_feedback
from scripts.patch_mode import apply_patch_ir
from scripts.plan_delta import compute_plan_delta
from scripts.policy_gate import check_policy_gate
from scripts.viability import evaluate_viability


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(x) for x in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)


def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    action = (req.get("action") or "").strip()
    strict = bool(req.get("strict", False))
    compiler = AICodeCompiler(strict_mode=strict)

    if action == "compile":
        code = req.get("code", "")
        ir = compiler.compile(code)
        return {"ok": True, "action": action, "ir": to_jsonable(ir)}

    if action == "validate":
        code = req.get("code", "")
        ir = compiler.compile(code)
        return {"ok": len(ir.get("errors", [])) == 0, "action": action, "errors": ir.get("errors", []), "meta": ir.get("meta", [])}

    if action == "emit":
        code = req.get("code", "")
        target = (req.get("target") or "ir").strip()
        ir = compiler.compile(code)
        if target == "ir":
            out = compiler.emit_ir_json(ir)
        elif target == "server":
            out = compiler.emit_server(ir)
        elif target == "react":
            out = compiler.emit_react(ir)
        elif target == "openapi":
            out = compiler.emit_openapi(ir)
        elif target == "prisma":
            out = compiler.emit_prisma_schema(ir)
        elif target == "sql":
            out = compiler.emit_sql_migrations(ir)
        else:
            return {"ok": False, "action": action, "error": f"Unsupported target: {target}"}
        return {"ok": True, "action": action, "target": target, "output": out, "errors": ir.get("errors", [])}

    if action == "plan_delta":
        base_ir = req.get("base_ir") or {}
        code = req.get("code", "")
        new_ir = req.get("new_ir")
        if new_ir is None:
            new_ir = compiler.compile(code)
        delta = compute_plan_delta(base_ir, new_ir)
        return {"ok": True, "action": action, "delta": to_jsonable(delta)}

    if action == "patch_apply":
        base_ir = req.get("base_ir") or {}
        allow_replace = bool(req.get("allow_replace", False))
        patch_ir = req.get("patch_ir")
        if patch_ir is None:
            patch_code = req.get("patch_code", "")
            patch_ir = compiler.compile(patch_code)
        patched = apply_patch_ir(base_ir, patch_ir, allow_replace=allow_replace)
        return {"ok": bool(patched.get("ok")), "action": action, **to_jsonable(patched)}

    if action == "policy_check":
        ir = req.get("ir")
        if ir is None:
            ir = compiler.compile(req.get("code", ""))
        pol = check_policy_gate(ir)
        ctr = check_contracts(ir)
        return {"ok": bool(pol.get("ok")) and bool(ctr.get("ok")), "action": action, "policy": pol, "contracts": ctr}

    if action == "compat_check":
        base_ir = req.get("base_ir") or {}
        ir = req.get("ir")
        if ir is None:
            ir = compiler.compile(req.get("code", ""))
        mode = req.get("mode") or ir.get("compat") or "add"
        comp = check_compat_gate(base_ir, ir, mode=mode)
        return {"ok": bool(comp.get("ok")), "action": action, "compat": comp}

    if action == "viability":
        code = req.get("code", "")
        timeout_s = float(req.get("timeout", 20.0))
        base_ir = req.get("base_ir")
        res = evaluate_viability(code=code, timeout_s=timeout_s, base_ir=base_ir)
        return {"ok": bool(res.get("ok")), "action": action, "viability": res}

    if action == "feedback":
        result = req.get("result") or {}
        fb = collect_feedback(result)
        return {"ok": True, "action": action, "feedback": fb}

    if action == "explain_error":
        # Minimal structured helper for local agent loops.
        error = str(req.get("error", "")).strip()
        hint = "Check op arity/scope and label targets."
        if "Unterminated string literal" in error:
            hint = "Close the quoted string before line end. Only \\\" and \\\\ are escapes in AINL 1.0."
        elif "requires at least" in error:
            hint = "Add the missing required slots for this op (see OP_REGISTRY in spec)."
        elif "label-only op" in error:
            hint = "Move this op inside an L<n>: block or convert to a top-level declaration op."
        return {"ok": True, "action": action, "hint": hint}

    return {"ok": False, "error": f"Unsupported action: {action}"}


def main() -> None:
    ap = argparse.ArgumentParser(description="AINL structured tool API CLI")
    ap.add_argument("--request-file", help="Path to JSON request file. If omitted, reads stdin.")
    args = ap.parse_args()

    if args.request_file:
        with open(args.request_file, "r", encoding="utf-8") as f:
            req = json.load(f)
    else:
        raw = sys.stdin.read().strip()
        req = json.loads(raw or "{}")

    try:
        res = handle_request(req)
    except Exception as e:
        res = {"ok": False, "error": str(e)}
    print(json.dumps(to_jsonable(res), indent=2))


if __name__ == "__main__":
    main()
