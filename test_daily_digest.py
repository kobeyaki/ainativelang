#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine
from adapters.openclaw_integration import openclaw_monitor_registry

source_path = Path(__file__).parent / "examples/openclaw/daily_digest.lang"
with open(source_path) as f:
    source = f.read()

registry = openclaw_monitor_registry()
compiler = AICodeCompiler(strict_mode=False, strict_reachability=False)
ir = compiler.compile(source)
print("Compilation succeeded. IR labels:", ir.get("labels", []))

engine = RuntimeEngine(ir, adapters=registry)
result = engine.run_label('0')
print("Run completed. Result:", result)
print("Status: OK")
