#!/usr/bin/env python3
"""
Run focused runtime test subset (independent from broader suite).
Usage: python scripts/run_runtime_tests.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import List


RUNTIME_TESTS: List[str] = [
    "tests/property/test_ir_fuzz_safety.py",
    "tests/property/test_runtime_equivalence.py",
    "tests/test_runtime_basic.py",
    "tests/test_runtime_graph_only.py",
    "tests/test_runtime_graph_only_negative.py",
    "tests/test_runtime_parity.py",
    "tests/test_runtime_limits.py",
    "tests/test_runtime_api_compat.py",
    "tests/test_runtime_conformance_fixtures.py",
    "tests/test_replay_determinism.py",
    "tests/test_http_adapter_contracts.py",
]


def main() -> None:
    cmd = [sys.executable, "-m", "pytest", "-q"] + RUNTIME_TESTS
    proc = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
