import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.adapters.base import AdapterRegistry, RuntimeAdapter
from runtime.engine import RuntimeEngine


class _EchoAdapter(RuntimeAdapter):
    def call(self, target, args, context):
        return args[0] if args else None


def test_runtime_limit_max_steps():
    code = "L1: Set a 1 Set b 2 Set c 3 J c\n"
    eng = RuntimeEngine.from_code(code, strict=True, limits={"max_steps": 2})
    try:
        eng.run_label("1")
        assert False, "expected max_steps failure"
    except Exception as e:
        assert "max_steps exceeded" in str(e)


def test_runtime_limit_max_depth():
    code = "L1: Call L1 J _call_result\n"
    eng = RuntimeEngine.from_code(code, strict=True, limits={"max_depth": 4})
    try:
        eng.run_label("1")
        assert False, "expected max_depth failure"
    except Exception as e:
        assert "max_depth exceeded" in str(e)


def test_runtime_limit_max_adapter_calls():
    code = "L1: R ext.echo 1 ->a\nR ext.echo 2 ->b\nJ b\n"
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", _EchoAdapter())
    eng = RuntimeEngine.from_code(code, strict=True, adapters=reg, limits={"max_adapter_calls": 1})
    try:
        eng.run_label("1")
        assert False, "expected max_adapter_calls failure"
    except Exception as e:
        assert "max_adapter_calls exceeded" in str(e)


def test_runtime_limit_max_loop_iters():
    code = "L1: X arr arr 1 2 3 Loop arr it ->L2 ->L3\nL2: J null\nL3: J done\n"
    eng = RuntimeEngine.from_code(code, strict=False, limits={"max_loop_iters": 2})
    try:
        eng.run_label("1")
        assert False, "expected max_loop_iters failure"
    except Exception as e:
        assert "max_loop_iters exceeded" in str(e)


def test_runtime_limit_max_time_ms():
    code = "L1: R core.sleep 50 ->x J x\n"
    eng = RuntimeEngine.from_code(code, strict=True, limits={"max_time_ms": 5})
    try:
        eng.run_label("1")
        assert False, "expected max_time_ms failure"
    except Exception as e:
        assert "max_time_ms exceeded" in str(e)
