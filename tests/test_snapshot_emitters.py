import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler


ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = ROOT / "tests" / "fixtures" / "snapshots" / "emitter_outputs.json"


def _load_snapshot() -> dict:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_emitter_snapshots_match_selected_public_and_compat_lanes():
    snapshot = _load_snapshot()
    for case in snapshot["cases"]:
        code = (ROOT / case["path"]).read_text(encoding="utf-8")
        compiler = AICodeCompiler(strict_mode=bool(case.get("strict", True)))
        ir = compiler.compile(code, emit_graph=True)
        assert not ir.get("errors"), f"{case['path']} compile errors: {ir.get('errors')}"

        emitter = case["emitter"]
        if emitter == "server":
            artifact = compiler.emit_server(ir)
            for needle in case["contains"]:
                assert needle in artifact, f"{case['name']} missing {needle!r}"
        elif emitter == "openapi_json":
            artifact = json.loads(compiler.emit_openapi(ir))
            assert sorted(artifact.get("paths", {}).keys()) == case["paths"], case["name"]
            for path, methods in case.get("path_methods", {}).items():
                path_obj = artifact["paths"].get(path, {})
                for method in methods:
                    assert method in path_obj, f"{case['name']} missing {method} for {path}"
            prov = artifact.get("info", {}).get("x-ainl-provenance", {})
            assert prov.get("initiator") == case["provenance_initiator"], case["name"]
        elif emitter == "prisma":
            artifact = compiler.emit_prisma_schema(ir)
            for needle in case["contains"]:
                assert needle in artifact, f"{case['name']} missing {needle!r}"
        elif emitter == "sql":
            artifact = compiler.emit_sql_migrations(ir, dialect="postgres")
            for needle in case["contains"]:
                assert needle in artifact, f"{case['name']} missing {needle!r}"
        else:
            raise AssertionError(f"unknown emitter snapshot type: {emitter}")
