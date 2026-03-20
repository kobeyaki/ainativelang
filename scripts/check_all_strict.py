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
    strict_paths = (
        data.get("examples", {}).get("strict-valid", [])
        + data.get("corpus_examples", {}).get("strict-valid", [])
    )
    strict_fx = data.get("runtime_fixtures", {}).get("strict-valid", [])
    c = AICodeCompiler(strict_mode=True)
    failed = 0
    for rel in strict_paths:
        p = ROOT / rel
        print(f"\n=== {rel} ===")
        ir = c.compile(p.read_text(encoding="utf-8"), emit_graph=True)
        errs = ir.get("errors") or []
        if errs:
            failed += 1
            print("ERRORS:", errs[:5])
        else:
            print("COMPILE OK")
    for rel in strict_fx:
        p = ROOT / rel
        print(f"\n=== {rel} ===")
        fx = json.loads(p.read_text(encoding="utf-8"))
        code = fx.get("code") or ""
        ir = c.compile(code, emit_graph=True)
        errs = ir.get("errors") or []
        if errs:
            failed += 1
            print("ERRORS:", errs[:5])
        else:
            print("COMPILE OK")
    total = len(strict_paths) + len(strict_fx)
    print(f"\nstrict profile: {total - failed}/{total} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
