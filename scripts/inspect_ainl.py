#!/usr/bin/env python3
"""
inspect_ainl.py

Tiny operator/agent helper to summarize an AINL program without reading full IR JSON.

For each input file it:
- compiles to graph IR (optionally strict),
- prints graph_semantic_checksum,
- counts labels and nodes (by effect class),
- lists adapters used,
- lists services/endpoints,
- reports diagnostics/warnings if present.

This script is a thin wrapper around compiler_v2.AICodeCompiler and does not
change any compiler or runtime semantics.
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from compiler_v2 import AICodeCompiler  # type: ignore
from tooling.ir_canonical import graph_semantic_checksum  # type: ignore


def _summarize_ir(ir: Dict[str, Any]) -> Dict[str, Any]:
    labels = ir.get("labels") or {}
    label_ids = sorted(labels.keys(), key=str)

    total_nodes = 0
    effect_counts: Counter[str] = Counter()
    adapters: Counter[str] = Counter()

    for lid in label_ids:
        body = labels.get(lid) or {}
        for node in body.get("nodes") or []:
            total_nodes += 1
            eff = node.get("effect") or "unknown"
            effect_counts[str(eff)] += 1
            data = node.get("data") or {}
            adapter = data.get("adapter")
            if isinstance(adapter, str) and adapter:
                # adapter may be "http.GET" -> take "http" as prefix
                prefix = adapter.split(".", 1)[0]
                adapters[prefix] += 1

    services = ir.get("services") or {}
    core = services.get("core") or {}
    eps = core.get("eps") or {}
    endpoints = []
    for path, methods in (eps or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, ep in methods.items():
            if isinstance(ep, dict):
                endpoints.append(f"{method.upper()} {path}")

    diagnostics = ir.get("diagnostics") or []
    warnings = [
        d
        for d in diagnostics
        if isinstance(d, dict) and d.get("severity") == "warning"
    ]

    return {
        "graph_semantic_checksum": graph_semantic_checksum(ir),
        "label_count": len(label_ids),
        "total_nodes": total_nodes,
        "effect_counts": dict(effect_counts),
        "adapters": dict(adapters),
        "endpoints": sorted(endpoints),
        "diagnostic_count": len(diagnostics),
        "warning_count": len(warnings),
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Summarize an AINL program (graph checksum, labels, adapters, effects)."
    )
    ap.add_argument(
        "files",
        nargs="+",
        help="Path(s) to .ainl/.lang files",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Compile with strict_mode=True",
    )
    args = ap.parse_args()

    for path in args.files:
        p = Path(path)
        if not p.is_file():
            print(f"{path}: [error] file not found")
            continue

        code = p.read_text(encoding="utf-8")
        compiler = AICodeCompiler(strict_mode=bool(args.strict))
        try:
            ir = compiler.compile(code, emit_graph=True)
        except Exception as e:  # pragma: no cover - defensive
            print(f"{path}: [error] compile failed: {e}")
            continue

        if ir.get("errors"):
            print(f"{path}: [error] IR contains errors:")
            for err in ir.get("errors", []):
                print(f"  - {err}")
            continue

        summary = _summarize_ir(ir)

        print(f"{path}:")
        print(f"  strict_mode: {bool(args.strict)}")
        print(f"  graph_semantic_checksum: {summary['graph_semantic_checksum']}")
        print(
            f"  labels: {summary['label_count']}, "
            f"nodes: {summary['total_nodes']} "
            f"(effects: {summary['effect_counts']})"
        )
        adapters = summary["adapters"]
        if adapters:
            adapter_str = ", ".join(f"{k}={v}" for k, v in sorted(adapters.items()))
        else:
            adapter_str = "none"
        print(f"  adapters: {adapter_str}")

        endpoints = summary["endpoints"]
        if endpoints:
            print(f"  endpoints:")
            for ep in endpoints:
                print(f"    - {ep}")
        else:
            print("  endpoints: none")

        print(
            f"  diagnostics: {summary['diagnostic_count']} "
            f"(warnings: {summary['warning_count']})"
        )
        print()


if __name__ == "__main__":
    main()
