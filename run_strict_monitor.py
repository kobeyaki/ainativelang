#!/usr/bin/env python3
import sys, os
sys.path.insert(0, '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang')
os.environ['MONITOR_CACHE_JSON'] = '/tmp/strict_monitor_cache.json'
from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine
from adapters.openclaw_integration import openclaw_monitor_registry

source = open('/Users/clawdbot/.openclaw/workspace/AI_Native_Lang/demo/monitor_system.strict.lang').read()
c = AICodeCompiler(strict_mode=True, strict_reachability=True)
ir = c.compile(source, emit_graph=True)
engine = RuntimeEngine(ir, adapters=openclaw_monitor_registry())
result = engine.run_label('0')
print("Strict monitor run result:", result)
