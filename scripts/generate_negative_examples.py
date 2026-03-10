#!/usr/bin/env python3
"""Generate deterministic, compiler-validated negative AINL examples."""

import json
import os
import random
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from compiler_v2 import AICodeCompiler

NEG_OUT = BASE / "corpus" / "raw_negatives.jsonl"
RNG = random.Random(42)


def error_category(err_msg: str) -> str:
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
    return "other"


def _mk(err_type: str, program: str) -> dict:
    return {
        "prompt": f"Write AINL program (invalid test case): {err_type}",
        "program": program,
        "ir": None,
        "errors": [f"Invalid: expected error category '{err_type}'"],
        "is_negative": True,
        "expected_error": err_type,
    }


def _candidate_examples() -> list[dict]:
    examples = []
    for i in range(120):
        examples.append(_mk("missing_args", f"S svc_only_{i}"))
        examples.append(_mk("missing_args", f"Rt route_only_{i}"))
        examples.append(_mk("scope_error", f"If (core.gt {i} 0) ->L1"))
        examples.append(_mk("scope_error", f"X v{i} 1"))
        examples.append(_mk("scope_error", "Err ->L1"))
        examples.append(_mk("endpoint_error", f"E /bad{i} G L{i}"))
    return examples


def _is_expected_negative(example: dict) -> bool:
    compiler = AICodeCompiler(strict_mode=True)
    ir = compiler.compile(example["program"], emit_graph=False)
    errs = ir.get("errors") or []
    if not errs:
        return False
    got = error_category(errs[0])
    return got == example["expected_error"]


def generate_negatives(count: int = 150) -> list[dict]:
    candidates = _candidate_examples()
    # Deduplicate by program before validation.
    uniq = {}
    for ex in candidates:
        uniq[ex["program"].strip()] = ex
    validated = [ex for ex in uniq.values() if _is_expected_negative(ex)]
    RNG.shuffle(validated)
    return validated[:count]


def main() -> None:
    NEG_OUT.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if os.environ.get("AINL_NEG_APPEND", "0") == "1" and NEG_OUT.exists():
        with open(NEG_OUT, encoding="utf-8") as f:
            for line in f:
                existing.append(json.loads(line))
    new_neg = generate_negatives(150)
    combined = existing + new_neg
    unique = []
    seen = set()
    for ex in combined:
        prog = ex["program"].strip()
        if prog in seen:
            continue
        seen.add(prog)
        unique.append(ex)
    with open(NEG_OUT, "w", encoding="utf-8") as f:
        for ex in unique:
            f.write(json.dumps(ex, ensure_ascii=True) + "\n")
    print(f"Negative examples: {len(unique)} total (added {len(new_neg)})")


if __name__ == "__main__":
    main()
