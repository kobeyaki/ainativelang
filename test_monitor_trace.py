#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang')
from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine
from adapters.openclaw_integration import openclaw_monitor_registry
import os
os.environ['MONITOR_CACHE_JSON'] = '/tmp/monitor_state_test.json'

source = open('/Users/clawdbot/.openclaw/workspace/AI_Native_Lang/demo/monitor_system.lang').read()
c = AICodeCompiler(strict_mode=False)
ir = c.compile(source, emit_graph=True)
engine = RuntimeEngine(ir, adapters=openclaw_monitor_registry())
engine.trace_enabled = True
result = engine.run_label('0')
print("Result:", result)
print("Trace events count:", len(engine.trace_events))
