import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from tooling.ir_canonical import graph_semantic_checksum


ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = ROOT / "tests" / "fixtures" / "snapshots" / "compile_outputs.json"


def _load_snapshot() -> dict:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_compile_snapshots_match_current_canonical_and_selected_compat_examples():
    snapshot = _load_snapshot()
    for case in snapshot["cases"]:
        code = (ROOT / case["path"]).read_text(encoding="utf-8")
        compiler = AICodeCompiler(strict_mode=bool(case.get("strict", True)))
        ir = compiler.compile(code, emit_graph=True)
        assert not ir.get("errors"), f"{case['path']} compile errors: {ir.get('errors')}"
        assert graph_semantic_checksum(ir) == case["graph_semantic_checksum"], case["path"]
        assert sorted((ir.get("labels") or {}).keys(), key=str) == case["labels"], case["path"]
        assert sorted((ir.get("services") or {}).keys(), key=str) == case["services"], case["path"]
        enabled_caps = sorted(k for k, v in (ir.get("emit_capabilities") or {}).items() if v)
        assert enabled_caps == case["emit_capabilities"], case["path"]
