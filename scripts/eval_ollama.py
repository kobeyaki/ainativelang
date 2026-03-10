#!/usr/bin/env python3
"""
Evaluate a local Ollama model on AINL generation quality.

Input format (JSONL):
  {"id":"crud_users","prompt":"Generate AINL for users CRUD dashboard"}

Usage:
  ainl-ollama-eval --model qwen2.5:7b --prompts data/evals/ollama_prompts.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler
from scripts.feedback_loop import collect_feedback
from scripts.retrieval_playbook import compose_playbook_context, load_playbooks
from scripts.viability import evaluate_viability


SYSTEM_PROMPT = (
    "You are generating AINL 1.0 source only.\n"
    "Output ONLY raw AINL code, no markdown fences, no explanations.\n"
    "Prefer compact valid programs with S/D/E/L/R/J and optional UI declarations.\n"
)


def guidance_items_from_errors(errors: List[str]) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    seen_codes = set()

    def add(code: str, message: str) -> None:
        if code in seen_codes:
            return
        seen_codes.add(code)
        items.append({"code": code, "message": message})

    if not errors:
        return items

    if any("auto-closed label" in e and "inside label block" in e for e in errors):
        add(
            "LABEL_SCOPE",
            "Avoid top-level ops (S/D/E/U/Role/Desc) inside label blocks. Start a new label after J/R steps, or move declarations above labels."
        )
    if any("unknown op" in e.lower() for e in errors):
        add(
            "UNKNOWN_OP",
            "Use canonical AINL ops only (for example: S, D, E, L:, R, J, U, If, Call, Bind)."
        )
    if any("arity" in e.lower() or "invalid slot" in e.lower() for e in errors):
        add(
            "ARITY",
            "Check argument counts for each op, especially E/Bind/If. Include required label targets such as ->L<n>."
        )
    if any(("target label" in e.lower()) or ("missing label" in e.lower()) for e in errors):
        add(
            "LABEL_TARGET",
            "Ensure every ->L<n> target exists and each targeted label ends with exactly one J step."
        )
    if any("unterminated string" in e.lower() for e in errors):
        add(
            "STRING_UNTERMINATED",
            'Close all quoted strings. In AINL, only \\" and \\\\ are semantic escapes.'
        )
    if not items:
        add("STRICT_VALIDATION", "Program failed strict validation; regenerate with stricter structural constraints and verify labels/arity.")
    return items


def guidance_items_from_viability(viability: Dict[str, Any] | None) -> List[Dict[str, str]]:
    if not viability or viability.get("ok"):
        return []
    stage = viability.get("stage", "")
    out: List[Dict[str, str]] = []
    if stage == "contracts_gate":
        out.append({"code": "CONTRACT_VIOLATION", "message": "Declared contracts do not match available endpoints."})
    elif stage == "policy_gate":
        out.append({"code": "POLICY_VIOLATION", "message": "Policy gate failed: auth/role/policy invariants are not satisfied."})
    elif stage == "compat_gate":
        out.append({"code": "COMPAT_BREAK", "message": "Compatibility gate failed due to breaking endpoint/type changes."})
    elif stage.startswith("endpoint_"):
        out.append({"code": "STRICT_VALIDATION", "message": "Runtime endpoint check failed shape/status constraints."})
    return out


def guidance_from_errors(errors: List[str]) -> List[str]:
    return [x["message"] for x in guidance_items_from_errors(errors)]


def ollama_generate(host: str, model: str, prompt: str, timeout_s: int = 120, extra_context: str = "") -> str:
    full_prompt = SYSTEM_PROMPT + "\n"
    if extra_context:
        full_prompt += "\nPlaybook guidance:\n" + extra_context.strip() + "\n"
    full_prompt += "\nTask:\n" + prompt + "\n"
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=f"{host.rstrip('/')}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return (body.get("response") or "").strip()


def load_prompts(path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            out.append(json.loads(ln))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate local Ollama model on AINL generation")
    ap.add_argument("--model", required=True, help="Ollama model name, e.g. qwen2.5:7b")
    ap.add_argument("--prompts", default="data/evals/ollama_prompts.jsonl", help="JSONL prompts file")
    ap.add_argument("--host", default="http://127.0.0.1:11434", help="Ollama host URL")
    ap.add_argument("--out", default="data/evals/ollama_eval_report.json", help="Output JSON report")
    ap.add_argument("--with-viability", action="store_true", help="Run end-to-end viability checks (server boot + endpoint)")
    ap.add_argument("--with-playbook", action="store_true", help="Use deterministic retrieval playbooks for prompt augmentation")
    ap.add_argument("--playbooks", default="data/evals/playbooks/default.jsonl", help="Playbook JSONL path")
    ap.add_argument("--playbook-top-k", type=int, default=2, help="Number of retrieved playbooks to inject")
    ap.add_argument("--max-retries", type=int, default=0, help="Retry failed generations with targeted feedback hints")
    args = ap.parse_args()

    prompts = load_prompts(args.prompts)
    playbooks = load_playbooks(args.playbooks) if args.with_playbook else []
    compiler = AICodeCompiler(strict_mode=True)
    rows: List[Dict[str, Any]] = []
    t0 = time.time()

    for i, item in enumerate(prompts, 1):
        pid = item.get("id", f"case_{i}")
        prompt = item.get("prompt", "")
        row: Dict[str, Any] = {"id": pid, "ok": False, "error_count": 0}
        try:
            pb_context = compose_playbook_context(prompt, playbooks, top_k=args.playbook_top_k) if args.with_playbook else ""
            best_ir: Dict[str, Any] = {}
            final_viability: Dict[str, Any] | None = None
            final_gen = ""
            final_errs: List[str] = []
            final_guidance: List[Dict[str, str]] = []
            retries_used = 0
            retry_context = ""
            for attempt in range(args.max_retries + 1):
                full_context = pb_context
                if retry_context:
                    full_context = (full_context + "\n\nRetry fixes:\n" + retry_context).strip()
                gen = ollama_generate(args.host, args.model, prompt, extra_context=full_context)
                ir = compiler.compile(gen)
                errs = ir.get("errors", [])
                viability = evaluate_viability(gen) if args.with_viability else {"ok": True}
                g_items = guidance_items_from_errors(errs[:5]) if errs else []
                g_items.extend(guidance_items_from_viability(viability))

                final_gen = gen
                best_ir = ir
                final_viability = viability
                final_errs = errs[:5]
                final_guidance = g_items
                if len(errs) == 0 and (not args.with_viability or viability.get("ok")):
                    break
                if attempt >= args.max_retries:
                    break
                retries_used += 1
                fb = collect_feedback(
                    {
                        "contracts": (viability or {}).get("contracts", {"ok": True}),
                        "policy": (viability or {}).get("policy", {"ok": True}),
                        "compat": (viability or {}).get("compat", {"ok": True}),
                    }
                )
                hints = [h.get("hint", "") for h in fb.get("hints", []) if h.get("hint")]
                if not hints:
                    hints = [g["message"] for g in g_items]
                retry_context = "\n".join(f"- {h}" for h in hints[:4])

            row.update(
                {
                    "ok": len(final_errs) == 0 and (not args.with_viability or (final_viability or {}).get("ok")),
                    "error_count": len(final_errs),
                    "errors": final_errs,
                    "guidance": [g["message"] for g in final_guidance],
                    "guidance_items": final_guidance,
                    "generated_chars": len(final_gen),
                    "stats": best_ir.get("stats", {}),
                    "viability": final_viability if args.with_viability else None,
                    "playbook_used": bool(pb_context),
                    "retries_used": retries_used,
                }
            )
        except Exception as e:
            e_msg = str(e)
            row.update(
                {
                    "ok": False,
                    "error_count": 1,
                    "errors": [e_msg],
                    "guidance": guidance_from_errors([e_msg]),
                    "guidance_items": guidance_items_from_errors([e_msg]),
                }
            )
        rows.append(row)

    elapsed = time.time() - t0
    passed = sum(1 for r in rows if r["ok"])
    viability_passed = sum(1 for r in rows if (r.get("viability") or {}).get("ok"))
    guidance_counts: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        for g in r.get("guidance_items", []) or []:
            code = g.get("code", "")
            msg = g.get("message", "")
            if not code:
                continue
            if code not in guidance_counts:
                guidance_counts[code] = {"code": code, "message": msg, "count": 0}
            guidance_counts[code]["count"] += 1
    top_guidance = [
        v
        for v in sorted(guidance_counts.values(), key=lambda x: x["count"], reverse=True)[:3]
    ]
    report = {
        "model": args.model,
        "host": args.host,
        "cases": len(rows),
        "passed": passed,
        "pass_rate": (passed / len(rows)) if rows else 0.0,
        "viability_passed": viability_passed if args.with_viability else None,
        "viability_pass_rate": (viability_passed / len(rows)) if (args.with_viability and rows) else None,
        "top_guidance": top_guidance,
        "elapsed_s": round(elapsed, 3),
        "results": rows,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
