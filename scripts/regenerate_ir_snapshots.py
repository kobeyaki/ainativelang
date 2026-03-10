#!/usr/bin/env python3
"""Regenerate IR snapshot artifacts from current compiler output.

Policy:
- `corpus/example_*/ir.json` are canonical generated snapshots from each `program.ainl`.
- `demo/emit/ir.json` is a canonical generated snapshot from its embedded `source.text`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from compiler_v2 import AICodeCompiler


def _write_ir(code: str, out_path: Path) -> None:
    compiler = AICodeCompiler(strict_mode=False)
    ir = compiler.compile(code, emit_graph=True)
    out_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _regen_corpus_snapshots() -> List[Tuple[Path, Path]]:
    pairs: List[Tuple[Path, Path]] = []
    for example_dir in sorted((ROOT / "corpus").glob("example_*")):
        program = example_dir / "program.ainl"
        out_ir = example_dir / "ir.json"
        if program.exists():
            pairs.append((program, out_ir))
    return pairs


def _regen_demo_emit_snapshot() -> Tuple[str, Path]:
    out_ir = ROOT / "demo" / "emit" / "ir.json"
    existing = json.loads(out_ir.read_text(encoding="utf-8"))
    source_text = ((existing.get("source") or {}).get("text") or "").strip()
    if not source_text:
        raise RuntimeError("demo/emit/ir.json missing source.text; cannot regenerate safely")
    return source_text + "\n", out_ir


def main() -> int:
    changed = 0
    for program_path, out_ir in _regen_corpus_snapshots():
        code = program_path.read_text(encoding="utf-8")
        _write_ir(code, out_ir)
        print(f"regenerated: {out_ir.relative_to(ROOT)} from {program_path.relative_to(ROOT)}")
        changed += 1

    demo_code, demo_out = _regen_demo_emit_snapshot()
    _write_ir(demo_code, demo_out)
    print(f"regenerated: {demo_out.relative_to(ROOT)} from embedded demo source")
    changed += 1

    print(f"done: regenerated {changed} IR snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
