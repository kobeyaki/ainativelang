#!/usr/bin/env python3
"""Refresh snapshot fixtures used by parity tests.

Policy:
- Preserve the curated case list already checked into `tests/fixtures/snapshots/`.
- Recompute only the dynamic baseline fields locked by tests today.
- Keep emitter string-marker snapshots intentionally loose; structured OpenAPI
  fields are refreshed from current compiler output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine
from tooling.ir_canonical import graph_semantic_checksum


SNAPSHOT_DIR = ROOT / "tests" / "fixtures" / "snapshots"
COMPILE_SNAPSHOT = SNAPSHOT_DIR / "compile_outputs.json"
EMITTER_SNAPSHOT = SNAPSHOT_DIR / "emitter_outputs.json"
RUNTIME_SNAPSHOT = SNAPSHOT_DIR / "runtime_paths.json"


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _compile_ir(rel_path: str, *, strict: bool) -> Dict[str, Any]:
    code = (ROOT / rel_path).read_text(encoding="utf-8")
    compiler = AICodeCompiler(strict_mode=bool(strict))
    ir = compiler.compile(code, emit_graph=True)
    if ir.get("errors"):
        raise RuntimeError(f"{rel_path} compile errors: {ir.get('errors')}")
    return ir


def refresh_compile_snapshot() -> None:
    payload = _load_json(COMPILE_SNAPSHOT)
    refreshed: List[Dict[str, Any]] = []
    for case in payload.get("cases", []):
        ir = _compile_ir(case["path"], strict=bool(case.get("strict", True)))
        refreshed.append(
            {
                **case,
                "graph_semantic_checksum": graph_semantic_checksum(ir),
                "labels": sorted((ir.get("labels") or {}).keys(), key=str),
                "services": sorted((ir.get("services") or {}).keys(), key=str),
                "emit_capabilities": sorted(k for k, v in (ir.get("emit_capabilities") or {}).items() if v),
            }
        )
    payload["cases"] = refreshed
    _write_json(COMPILE_SNAPSHOT, payload)


def refresh_emitter_snapshot() -> None:
    payload = _load_json(EMITTER_SNAPSHOT)
    refreshed: List[Dict[str, Any]] = []
    for case in payload.get("cases", []):
        ir = _compile_ir(case["path"], strict=bool(case.get("strict", True)))
        emitter = case.get("emitter")
        updated = dict(case)
        compiler = AICodeCompiler(strict_mode=bool(case.get("strict", True)))
        if emitter == "openapi_json":
            doc = json.loads(compiler.emit_openapi(ir))
            updated["paths"] = sorted(doc.get("paths", {}).keys())
            updated["path_methods"] = {
                path: sorted(doc.get("paths", {}).get(path, {}).keys())
                for path in sorted((case.get("path_methods") or {}).keys())
            }
            updated["provenance_initiator"] = (
                (doc.get("info") or {}).get("x-ainl-provenance") or {}
            ).get("initiator")
        refreshed.append(updated)
    payload["cases"] = refreshed
    _write_json(EMITTER_SNAPSHOT, payload)


def refresh_runtime_snapshot() -> None:
    payload = _load_json(RUNTIME_SNAPSHOT)
    refreshed: List[Dict[str, Any]] = []
    for case in payload.get("cases", []):
        fixture = _load_json(ROOT / case["fixture"])
        run_payload = RuntimeEngine.run(
            fixture["code"],
            frame=fixture.get("input_frame", {}),
            trace=True,
            strict=bool(fixture.get("strict", True)),
            execution_mode="graph-preferred",
        )
        refreshed.append(
            {
                **case,
                "expected_result": run_payload["result"],
                "expected_trace_ops": [event.get("op") for event in run_payload.get("trace", [])],
            }
        )
    payload["cases"] = refreshed
    _write_json(RUNTIME_SNAPSHOT, payload)


def main() -> int:
    ap = argparse.ArgumentParser(description="Refresh parity snapshot fixtures from current compiler/runtime behavior")
    ap.add_argument("--compile", action="store_true", help="Refresh compile output snapshots only")
    ap.add_argument("--emitters", action="store_true", help="Refresh emitter snapshots only")
    ap.add_argument("--runtime", action="store_true", help="Refresh runtime path snapshots only")
    args = ap.parse_args()

    refresh_all = not (args.compile or args.emitters or args.runtime)
    changed: List[str] = []

    if args.compile or refresh_all:
        refresh_compile_snapshot()
        changed.append(str(COMPILE_SNAPSHOT.relative_to(ROOT)))
    if args.emitters or refresh_all:
        refresh_emitter_snapshot()
        changed.append(str(EMITTER_SNAPSHOT.relative_to(ROOT)))
    if args.runtime or refresh_all:
        refresh_runtime_snapshot()
        changed.append(str(RUNTIME_SNAPSHOT.relative_to(ROOT)))

    for rel in changed:
        print(f"refreshed: {rel}")
    print(f"done: refreshed {len(changed)} snapshot fixture file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
