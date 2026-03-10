#!/usr/bin/env python3
"""Validate .ainl and corpus JSONL with positive/negative expectations."""

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from compiler_v2 import AICodeCompiler


PROFILE_PATH = BASE / "tooling" / "artifact_profiles.json"


def _default_profile_paths(strict_mode: bool):
    if not PROFILE_PATH.exists():
        return []
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if strict_mode:
        rels = (
            data.get("examples", {}).get("strict-valid", [])
            + data.get("corpus_examples", {}).get("strict-valid", [])
        )
    else:
        rels = (
            data.get("examples", {}).get("strict-valid", [])
            + data.get("examples", {}).get("non-strict-only", [])
            + data.get("corpus_examples", {}).get("strict-valid", [])
            + data.get("corpus_examples", {}).get("non-strict-only", [])
        )
    return [BASE / rel for rel in rels]

def check_program(prog: str, source: str, *, expect_failure: bool = False, strict_mode: bool = True):
    c = AICodeCompiler(strict_mode=strict_mode)
    ir = c.compile(prog, emit_graph=False)
    errors = ir.get("errors") or []
    if expect_failure:
        if errors:
            return True
        print(f"❌ {source}: expected failure, but program compiled")
        return False
    if errors:
        print(f"❌ {source}:")
        for e in errors:
            print(f"   {e}")
        return False
    return True

def main(paths, *, include_negatives: bool = False, strict_mode: bool = True):
    ok = True
    checked = 0
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        if path.suffix == ".jsonl":
            with open(path, encoding="utf-8") as f:
                for idx, line in enumerate(f, start=1):
                    try:
                        obj = json.loads(line)
                        prog = obj.get("program")
                        if prog:
                            is_negative = bool(obj.get("is_negative")) or path.name.startswith("neg")
                            if is_negative and not include_negatives:
                                continue
                            checked += 1
                            if not check_program(
                                prog,
                                f"{path}:{idx}",
                                expect_failure=is_negative,
                                strict_mode=strict_mode,
                            ):
                                ok = False
                    except Exception as e:
                        print(f"Error parsing {path}: {e}")
                        ok = False
        elif path.suffix == ".ainl":
            prog = path.read_text(encoding="utf-8")
            checked += 1
            if not check_program(prog, str(path), expect_failure=False, strict_mode=strict_mode):
                ok = False
    if ok:
        print(f"Validation passed ({checked} programs checked).")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate AINL corpus/examples.")
    parser.add_argument("paths", nargs="*", help="Paths to .jsonl/.ainl files.")
    parser.add_argument(
        "--include-negatives",
        action="store_true",
        help="Validate negative corpus rows as expected failures.",
    )
    parser.add_argument(
        "--strict-mode",
        action="store_true",
        default=False,
        help="Validate using strict compiler mode (recommended for strict-profile checks).",
    )
    args = parser.parse_args()
    if args.paths:
        main(args.paths, include_negatives=args.include_negatives, strict_mode=args.strict_mode)
    else:
        default_paths = _default_profile_paths(args.strict_mode)
        if not default_paths:
            default_paths = list((BASE / "corpus" / "curated").glob("*.jsonl")) + list((BASE / "examples").rglob("*.ainl"))
        main(default_paths, include_negatives=args.include_negatives, strict_mode=args.strict_mode)
