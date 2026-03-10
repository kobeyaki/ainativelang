#!/usr/bin/env python3
import sys, json
sys.path.insert(0, '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang')
from compiler_v2 import AICodeCompiler
source = open('/Users/clawdbot/.openclaw/workspace/AI_Native_Lang/examples/openclaw/infrastructure_watchdog.lang').read()
c = AICodeCompiler(strict_mode=False)
ir = c.compile(source, emit_graph=True)
print(json.dumps(ir['labels']['0'], indent=2))
