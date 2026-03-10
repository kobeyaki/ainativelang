#!/usr/bin/env python3
import sys, json
sys.path.insert(0, '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang')
from compiler_v2 import AICodeCompiler
source = open('/Users/clawdbot/.openclaw/workspace/AI_Native_Lang/examples/openclaw/infrastructure_watchdog.lang').read()
c = AICodeCompiler(strict_mode=False)
ir = c.compile(source, emit_graph=True)
print("Labels:", list(ir['labels'].keys()))
print("Label 0 nodes:", ir['labels']['0'].get('nodes'))
print("Label 0 edges:", ir['labels']['0'].get('edges'))
print("Label 0 entry:", ir['labels']['0'].get('entry'))
