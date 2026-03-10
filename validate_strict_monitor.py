#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang')
from compiler_v2 import AICodeCompiler
from adapters.openclaw_integration import openclaw_monitor_registry

source = open('/Users/clawdbot/.openclaw/workspace/AI_Native_Lang/demo/monitor_system.strict.lang').read()
c = AICodeCompiler(strict_mode=True, strict_reachability=True)
try:
    ir = c.compile(source, emit_graph=True)
    print("Strict compilation succeeded. Labels:", list(ir.get('labels', {}).keys()))
except Exception as e:
    print("Strict compilation FAILED:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
