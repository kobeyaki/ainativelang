#!/usr/bin/env python3
"""
Benchmark multiple local Ollama models on AINL generation quality.

Usage:
  ainl-ollama-benchmark --models qwen2.5:7b,llama3.1:8b --prompts data/evals/ollama_prompts.jsonl
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.eval_ollama import (
    guidance_from_errors,
    guidance_items_from_errors,
    guidance_items_from_viability,
    load_prompts,
    ollama_generate,
)
from scripts.feedback_loop import collect_feedback
from compiler_v2 import AICodeCompiler
from scripts.retrieval_playbook import compose_playbook_context, load_playbooks
from scripts.viability import evaluate_viability


def eval_model(
    model: str,
    host: str,
    prompts: List[Dict[str, Any]],
    timeout_s: int,
    with_viability: bool = False,
    playbooks: List[Dict[str, Any]] | None = None,
    playbook_top_k: int = 2,
    max_retries: int = 0,
) -> Dict[str, Any]:
    compiler = AICodeCompiler(strict_mode=True)
    t0 = time.time()
    rows: List[Dict[str, Any]] = []
    for i, item in enumerate(prompts, 1):
        pid = item.get("id", f"case_{i}")
        prompt = item.get("prompt", "")
        row: Dict[str, Any] = {"id": pid, "ok": False, "error_count": 0}
        try:
            pb_context = compose_playbook_context(prompt, playbooks or [], top_k=playbook_top_k) if playbooks else ""
            final_errs: List[str] = []
            final_guidance: List[Dict[str, str]] = []
            final_gen = ""
            final_ir: Dict[str, Any] = {}
            final_viability: Dict[str, Any] | None = None
            retries_used = 0
            retry_context = ""
            for attempt in range(max_retries + 1):
                full_context = pb_context
                if retry_context:
                    full_context = (full_context + "\n\nRetry fixes:\n" + retry_context).strip()
                gen = ollama_generate(host=host, model=model, prompt=prompt, timeout_s=timeout_s, extra_context=full_context)
                ir = compiler.compile(gen)
                errs = ir.get("errors", [])
                viability = evaluate_viability(gen) if with_viability else {"ok": True}
                g_items = guidance_items_from_errors(errs[:3]) if errs else []
                g_items.extend(guidance_items_from_viability(viability))

                final_errs = errs[:3]
                final_guidance = g_items
                final_gen = gen
                final_ir = ir
                final_viability = viability
                if len(errs) == 0 and (not with_viability or viability.get("ok")):
                    break
                if attempt >= max_retries:
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
                    "ok": len(final_errs) == 0 and (not with_viability or (final_viability or {}).get("ok")),
                    "error_count": len(final_errs),
                    "errors": final_errs,
                    "guidance": [g["message"] for g in final_guidance],
                    "guidance_items": final_guidance,
                    "generated_chars": len(final_gen),
                    "ops": final_ir.get("stats", {}).get("ops", 0),
                    "viability_ok": bool(final_viability and final_viability.get("ok")),
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
    viability_passed = sum(1 for r in rows if r.get("viability_ok"))
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
    avg_err = (sum(r.get("error_count", 0) for r in rows) / len(rows)) if rows else 0.0
    avg_chars = (sum(r.get("generated_chars", 0) for r in rows) / len(rows)) if rows else 0.0
    return {
        "model": model,
        "cases": len(rows),
        "passed": passed,
        "pass_rate": (passed / len(rows)) if rows else 0.0,
        "viability_passed": viability_passed if with_viability else None,
        "viability_pass_rate": (viability_passed / len(rows)) if (with_viability and rows) else None,
        "top_guidance": top_guidance,
        "avg_error_count": round(avg_err, 3),
        "avg_generated_chars": round(avg_chars, 1),
        "elapsed_s": round(elapsed, 3),
        "results": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Benchmark multiple Ollama models for AINL generation")
    ap.add_argument("--models", required=True, help="Comma-separated model names")
    ap.add_argument("--prompts", default="data/evals/ollama_prompts.jsonl", help="JSONL prompts file")
    ap.add_argument("--host", default="http://127.0.0.1:11434", help="Ollama host URL")
    ap.add_argument("--timeout", type=int, default=120, help="Per-request timeout seconds")
    ap.add_argument("--out", default="data/evals/ollama_benchmark_report.json", help="Output JSON report")
    ap.add_argument("--csv-out", default="", help="Optional output CSV path for flat model summary")
    ap.add_argument("--with-viability", action="store_true", help="Run end-to-end viability checks (slower)")
    ap.add_argument("--with-playbook", action="store_true", help="Use deterministic retrieval playbooks for prompt augmentation")
    ap.add_argument("--playbooks", default="data/evals/playbooks/default.jsonl", help="Playbook JSONL path")
    ap.add_argument("--playbook-top-k", type=int, default=2, help="Number of retrieved playbooks to inject")
    ap.add_argument("--max-retries", type=int, default=0, help="Retry failed generations with targeted feedback hints")
    args = ap.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    prompts = load_prompts(args.prompts)
    playbooks = load_playbooks(args.playbooks) if args.with_playbook else []

    summaries: List[Dict[str, Any]] = []
    for model in models:
        print(f"[bench] model={model} cases={len(prompts)}", file=sys.stderr)
        summaries.append(
            eval_model(
                model=model,
                host=args.host,
                prompts=prompts,
                timeout_s=args.timeout,
                with_viability=args.with_viability,
                playbooks=playbooks,
                playbook_top_k=args.playbook_top_k,
                max_retries=args.max_retries,
            )
        )

    ranked = sorted(
        summaries,
        key=lambda x: (-x["pass_rate"], x["avg_error_count"], x["elapsed_s"]),
    )
    report = {
        "host": args.host,
        "prompts": args.prompts,
        "ranked": ranked,
        "summary": [
            {
                "model": r["model"],
                "pass_rate": r["pass_rate"],
                "viability_pass_rate": r.get("viability_pass_rate"),
                "avg_error_count": r["avg_error_count"],
                "elapsed_s": r["elapsed_s"],
                "top_guidance": r.get("top_guidance", []),
            }
            for r in ranked
        ],
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if args.csv_out:
        csv_dir = os.path.dirname(args.csv_out)
        if csv_dir:
            os.makedirs(csv_dir, exist_ok=True)
        with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "model",
                    "pass_rate",
                    "viability_pass_rate",
                    "avg_error_count",
                    "elapsed_s",
                    "cases",
                    "passed",
                    "avg_generated_chars",
                ],
            )
            w.writeheader()
            for r in ranked:
                w.writerow(
                    {
                        "model": r["model"],
                        "pass_rate": r["pass_rate"],
                        "viability_pass_rate": r.get("viability_pass_rate"),
                        "avg_error_count": r["avg_error_count"],
                        "elapsed_s": r["elapsed_s"],
                        "cases": r["cases"],
                        "passed": r["passed"],
                        "avg_generated_chars": r["avg_generated_chars"],
                    }
                )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
