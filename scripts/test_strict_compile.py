#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    target = root / "examples" / "hello.ainl"
    code = target.read_text(encoding="utf-8")
    c = AICodeCompiler(strict_mode=True, strict_reachability=True)
    try:
        ir = c.compile(code)
    except Exception as e:
        print("EXCEPTION:", e)
        return 1

    if ir.get("errors"):
        print("ERRORS:", ir["errors"])
        return 1
    print(f"COMPILE OK: {target}")
    print("Strict validation: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
