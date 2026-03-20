#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler


ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "tooling" / "artifact_profiles.json"


def main() -> int:
    data = json.loads(PROFILE.read_text(encoding="utf-8"))
    non_strict_paths = (
        data.get("examples", {}).get("non-strict-only", [])
        + data.get("corpus_examples", {}).get("non-strict-only", [])
    )
    non_strict_fx = data.get("runtime_fixtures", {}).get("non-strict-only", [])
    c = AICodeCompiler(strict_mode=False)
    strict_c = AICodeCompiler(strict_mode=True)
    failed = 0
    for rel in non_strict_paths:
        p = ROOT / rel
        print(f"\n=== {rel} ===")
        ir = c.compile(p.read_text(encoding="utf-8"), emit_graph=True)
        errs = ir.get("errors") or []
        if errs:
            failed += 1
            print("COMPILE ERRORS:", errs[:5], "... total", len(errs))
        else:
            print("COMPILE OK")
    for rel in non_strict_fx:
        p = ROOT / rel
        print(f"\n=== {rel} ===")
        fx = json.loads(p.read_text(encoding="utf-8"))
        code = fx.get("code") or ""
        ir = c.compile(code, emit_graph=True)
        errs = ir.get("errors") or []
        if errs:
            failed += 1
            print("COMPILE ERRORS:", errs[:5], "... total", len(errs))
            continue
        strict_ir = strict_c.compile(code, emit_graph=True)
        strict_errs = strict_ir.get("errors") or []
        if not strict_errs:
            failed += 1
            print("EXPECTED strict failure but strict compile passed")
        else:
            print("COMPILE OK (non-strict) and strict failure confirmed")
    total = len(non_strict_paths) + len(non_strict_fx)
    print(f"\nnon-strict profile: {total - failed}/{total} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
