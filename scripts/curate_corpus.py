#!/usr/bin/env python3
"""
Curate the AINL training corpus for small models.

Outputs:
- corpus/curated/pos.jsonl
- corpus/curated/neg.jsonl
- corpus/curated/full_workflows.jsonl
"""

import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from compiler_v2 import AICodeCompiler

INPUT = BASE / "corpus" / "training_data.jsonl"
NEG_INPUT = BASE / "corpus" / "raw_negatives.jsonl"
NEG_CURATED = BASE / "corpus" / "curated" / "neg.jsonl"
OUT_DIR = BASE / "corpus" / "curated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

POS = OUT_DIR / "pos.jsonl"
NEG = OUT_DIR / "neg.jsonl"
FULL = OUT_DIR / "full_workflows.jsonl"

ALLOW_ADAPTERS = {
    "core",
    "cache",
    "fs",
    "sqlite",
    "email",
    "calendar",
    "db",
    "http",
    "queue",
    "social",
    "svc",
    "wasm",
}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _program_adapters(program: str) -> set[str]:
    adapters = set()
    for match in re.finditer(r"\b([A-Za-z_][\w]*)\.", program):
        adapters.add(match.group(1))
    return adapters


def _is_allowed_profile(program: str) -> bool:
    adapters = _program_adapters(program)
    return all(a in ALLOW_ADAPTERS for a in adapters)


def _is_full_workflow(program: str) -> bool:
    adapters = _program_adapters(program)
    has_control = any(tok in program for tok in ("Try", "Err", "If", "Cr ", "Cr\t"))
    has_multi_adapter = len(adapters) >= 2
    has_multi_label = len(re.findall(r"\bL[\w-]*\s*:", program)) >= 2
    return has_control or has_multi_adapter or has_multi_label


def _compile_ok(program: str) -> bool:
    compiler = AICodeCompiler(strict_mode=True)
    ir = compiler.compile(program, emit_graph=False)
    return not bool(ir.get("errors"))


def _error_category(err_msg: str) -> str:
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


def _negative_matches_expected(row: dict) -> bool:
    compiler = AICodeCompiler(strict_mode=True)
    ir = compiler.compile(row["program"], emit_graph=False)
    errors = ir.get("errors") or []
    if not errors:
        return False
    expected = row.get("expected_error")
    if not expected:
        return True
    return _error_category(errors[0]) == expected


def _dedupe_by_program(rows: list[dict]) -> list[dict]:
    out = []
    seen = set()
    for row in rows:
        program = (row.get("program") or "").strip()
        if not program or program in seen:
            continue
        seen.add(program)
        row["program"] = program
        out.append(row)
    return out


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")


def main() -> None:
    source = _dedupe_by_program(load_jsonl(INPUT))
    if not source:
        raise SystemExit(f"Missing or empty training data: {INPUT}")

    pos = []
    full = []
    for row in source:
        program = row["program"]
        if not _is_allowed_profile(program):
            continue
        if not _compile_ok(program):
            continue
        pos.append(row)
        if _is_full_workflow(program):
            full.append(row)

    # Negatives come from generated negatives and any already-curated negatives.
    neg_source = load_jsonl(NEG_INPUT)
    if os.environ.get("AINL_INCLUDE_EXISTING_CURATED_NEG", "0") == "1":
        neg_source += load_jsonl(NEG_CURATED)
    neg_rows = _dedupe_by_program(neg_source)
    neg = []
    skipped_neg = 0
    for row in neg_rows:
        if not _negative_matches_expected(row):
            skipped_neg += 1
            continue
        row["is_negative"] = True
        neg.append(row)

    _write_jsonl(POS, _dedupe_by_program(pos))
    _write_jsonl(NEG, _dedupe_by_program(neg))
    _write_jsonl(FULL, _dedupe_by_program(full))

    print("Curated corpus:")
    print(f"- Positives: {len(pos)}")
    print(f"- Negatives: {len(neg)}")
    print(f"- Negatives skipped (invalid label/no-fail mismatch): {skipped_neg}")
    print(f"- Full workflows: {len(full)}")
    print(f"- Output dir: {OUT_DIR}")


if __name__ == "__main__":
    main()
