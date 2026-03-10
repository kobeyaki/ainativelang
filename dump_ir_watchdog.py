#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from compiler_v2 import AICodeCompiler
source = Path('examples/openclaw/infrastructure_watchdog.lang').read_text()
c = AICodeCompiler(strict_mode=False)
ir = c.compile(source, emit_graph=True)
# Dump IR nicely
import json
print(json.dumps(ir, indent=2))
