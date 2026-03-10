#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ensure cache goes to a local file for inspection
os.environ.setdefault('MONITOR_CACHE_JSON', 'test_watchdog_cache.json')

sys.path.insert(0, str(Path(__file__).parent))

from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine
from adapters.openclaw_integration import openclaw_monitor_registry

source_path = Path(__file__).parent / "examples/openclaw/infrastructure_watchdog.lang"
with open(source_path) as f:
    source = f.read()

registry = openclaw_monitor_registry()
compiler = AICodeCompiler(strict_mode=False, strict_reachability=False)
ir = compiler.compile(source)
print("Compilation succeeded. IR labels:", list(ir.get("labels", {}).keys()))

engine = RuntimeEngine(ir, adapters=registry)
print("Trace enabled before:", engine.trace_enabled)
engine.trace_enabled = True  # enable tracing
print("Trace enabled after:", engine.trace_enabled)
result = engine.run_label('0')
print("Run completed. Result:", result)
print("Status: OK")

# Print trace summary
if engine.trace_events:
    print("Trace events (first few):")
    for ev in engine.trace_events[:10]:
        print(ev.get('label'), ev.get('op'), ev.get('out'))

# Check cache adapter state
cache_adapter = registry.get_cache()
print("Cache adapter store:", getattr(cache_adapter, 'store', 'no store attr'))

# Check if cache file was created
cache_path = Path('test_watchdog_cache.json')
if cache_path.exists():
    print("Cache file created:")
    print(cache_path.read_text())
else:
    print("No cache file found after run.")
