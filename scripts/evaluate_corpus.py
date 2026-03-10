#!/usr/bin/env python3
"""Evaluate curated corpus in strict/runtime/dual modes."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from compiler_v2 import AICodeCompiler

POS = BASE / "corpus" / "curated" / "pos.jsonl"
NEG = BASE / "corpus" / "curated" / "neg.jsonl"
FULL = BASE / "corpus" / "curated" / "full_workflows.jsonl"
OUT = BASE / "corpus" / "curated" / "eval_results.json"

def load_jsonl(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def error_category(err_msg: str) -> str:
    # Map error message to coarse category for comparison
    err = str(err_msg).lower()
    if "unknown adapter" in err or "unknown module" in err:
        return "unknown_adapter"
    if "unknown op" in err:
        return "unknown_verb"
    if "label-only op" in err:
        return "scope_error"
    if "slot 3 must be ->l" in err:
        return "endpoint_error"
    if "missing" in err and "arg" in err:
        return "missing_args"
    if "requires at least" in err:
        return "missing_args"
    if "syntax" in err:
        return "syntax_error"
    if "label" in err and "undefined" in err:
        return "label_undefined"
    if "tier" in err or "policy" in err:
        return "tier_violation"
    # fallback
    return "other"

def _evaluate(*, strict_positive: bool, strict_negative: bool, strict_full: bool) -> dict:
    results = {
        "positive": {"total": 0, "compiled_ok": 0, "errors": []},
        "negative": {"total": 0, "failed_ok": 0, "error_categories": Counter(), "mismatches": []},
    }

    pos_examples = load_jsonl(POS)
    results["positive"]["total"] = len(pos_examples)
    for ex in pos_examples:
        prog = ex["program"]
        c = AICodeCompiler(strict_mode=strict_positive)
        ir = c.compile(prog, emit_graph=True)
        if not ir.get("errors"):
            results["positive"]["compiled_ok"] += 1
        else:
            results["positive"]["errors"].append({"program": prog, "errors": ir["errors"]})

    neg_examples = load_jsonl(NEG)
    results["negative"]["total"] = len(neg_examples)
    for ex in neg_examples:
        prog = ex["program"]
        expected = ex.get("expected_error")
        c = AICodeCompiler(strict_mode=strict_negative)
        ir = c.compile(prog, emit_graph=True)
        if ir.get("errors"):
            got = error_category(ir["errors"][0])
            results["negative"]["failed_ok"] += 1
            results["negative"]["error_categories"][got] += 1
            if expected and got != expected:
                results["negative"]["mismatches"].append({
                    "program": prog,
                    "expected": expected,
                    "got": got,
                    "errors": ir["errors"]
                })
        else:
            # It compiled but should have failed
            results["negative"]["mismatches"].append({
                "program": prog,
                "expected": expected,
                "got": "compiled_ok",
                "errors": []
            })

    full_examples = load_jsonl(FULL)
    full_ok = 0
    for ex in full_examples:
        c = AICodeCompiler(strict_mode=strict_full)
        ir = c.compile(ex["program"], emit_graph=True)
        if not ir.get("errors"):
            full_ok += 1
    results["full_workflows"] = {"total": len(full_examples), "compiled_ok": full_ok}
    return results


def _print_summary(title: str, results: dict) -> None:
    pos_acc = results["positive"]["compiled_ok"] / results["positive"]["total"] if results["positive"]["total"] else 0
    neg_acc = results["negative"]["failed_ok"] / results["negative"]["total"] if results["negative"]["total"] else 0
    print(f"AINL Corpus Evaluation ({title})")
    print(f"- Positives: {results['positive']['compiled_ok']}/{results['positive']['total']} compiled ({pos_acc:.1%})")
    print(f"- Negatives: {results['negative']['failed_ok']}/{results['negative']['total']} failed as expected ({neg_acc:.1%})")
    print(f"- Full workflows: {results['full_workflows']['compiled_ok']}/{results['full_workflows']['total']} compiled")
    if results["negative"]["mismatches"]:
        print(f"- Mismatches (negative category errors): {len(results['negative']['mismatches'])}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate curated AINL corpus.")
    parser.add_argument(
        "--mode",
        choices=["strict", "runtime", "dual"],
        default="dual",
        help="strict: strict compiler for all; runtime: non-strict for all; dual: report both.",
    )
    args = parser.parse_args()

    if args.mode == "strict":
        strict_results = _evaluate(strict_positive=True, strict_negative=True, strict_full=True)
        out = {"mode": "strict", "results": strict_results}
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        _print_summary("strict", strict_results)
    elif args.mode == "runtime":
        runtime_results = _evaluate(strict_positive=False, strict_negative=False, strict_full=False)
        out = {"mode": "runtime", "results": runtime_results}
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        _print_summary("runtime", runtime_results)
    else:
        strict_results = _evaluate(strict_positive=True, strict_negative=True, strict_full=True)
        runtime_results = _evaluate(strict_positive=False, strict_negative=False, strict_full=False)
        out = {
            "mode": "dual",
            "strict": strict_results,
            "runtime": runtime_results,
        }
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        _print_summary("strict", strict_results)
        _print_summary("runtime", runtime_results)

    print(f"Results written to: {OUT}")

if __name__ == "__main__":
    main()
