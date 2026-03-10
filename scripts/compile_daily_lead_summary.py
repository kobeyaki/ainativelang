#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang')

from compiler_v2 import AICodeCompiler
from adapters.openclaw_integration import openclaw_monitor_registry
from runtime.engine import RuntimeEngine

ainl_path = '/Users/clawdbot/.openclaw/workspace/AI_Native_Lang/examples/openclaw/daily_lead_summary.lang'

# Compile (non-strict, like production)
compiler = AICodeCompiler(strict_mode=False, strict_reachability=False)
with open(ainl_path, 'r') as f:
    src = f.read()
ir = compiler.compile(src)

print(f'✅ Compilation succeeded. Labels: {list(ir.get("labels", {}).keys())}')

# Build runtime with OpenClaw adapters
registry = openclaw_monitor_registry()
engine = RuntimeEngine(ir, adapters=registry, execution_mode='graph-preferred')
# Ensure core capability is allowed (mirror run_ainl_monitor.py)
if not hasattr(engine, 'caps'):
    engine.caps = set()
if isinstance(engine.caps, list):
    engine.caps = set(engine.caps)
engine.caps.add('core')
print('✅ RuntimeEngine constructed successfully with core capability.')
print('All checks passed.')