#!/usr/bin/env python3
import sys
print("1-start")
sys.path.insert(0, '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang')
print("2-path")
from compiler_v2 import AICodeCompiler
print("3-compiler imported")
from runtime.engine import RuntimeEngine
print("4-engine imported")
from adapters.openclaw_integration import openclaw_monitor_registry
print("5-registry imported")
source = open('/Users/clawdbot/.openclaw/workspace/AI_Native_Lang/demo/monitor_system.lang').read()
print("6-source read, len", len(source))
c = AICodeCompiler(strict_mode=False)
print("7-compiler created")
ir = c.compile(source, emit_graph=True)
print("8-compiled")
engine = RuntimeEngine(ir, adapters=openclaw_monitor_registry())
print("9-engine created")
engine.trace_enabled = True
print("10-trace enabled")
result = engine.run_label('0')
print("11-run completed:", result)