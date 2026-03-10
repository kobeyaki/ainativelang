#!/usr/bin/env python3
import sys, json
sys.path.insert(0, '.')
from compiler_v2 import AICodeCompiler
c = AICodeCompiler()
code = open('demo/monitor_system.lang').read()
ir = c.compile(code)
if ir is None:
    print("Compile returned None")
else:
    graph = ir.get('graph', {})
    if not graph:
        print("No graph")
    else:
        first_lid = next(iter(graph))
        first_step = graph[first_lid][0]
        with open('scripts/first_step.json', 'w') as f:
            json.dump(first_step, f)
        print("Wrote first_step.json")
