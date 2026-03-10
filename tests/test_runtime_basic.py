import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runtime.engine import RuntimeEngine
from runtime.adapters.base import AdapterRegistry, RuntimeAdapter
from compiler_v2 import AICodeCompiler


def test_runtime_core_add():
    code = """
L1: R core.add 2 3 ->x J x
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == 5


def test_runtime_if_branch():
    code = """
L1: Set flag true If flag ->L2 ->L3
L2: Set out "ok" J out
L3: Set out "bad" J out
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == "ok"


def test_runtime_call_helper():
    code = """
L1: Call L9 J _call_result
L9: R core.add 40 2 ->v J v
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == 42


def test_runtime_call_helper_with_explicit_out():
    code = """
L1: Call L9 ->res J res
L9: R core.add 10 5 ->v J v
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == 15


def test_runtime_x_op_math():
    code = """
L1: X x add 2 3 J x
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == 5


def test_runtime_resolve_negative_float():
    code = """
L1: X x add -1.5 0.5 J x
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == -1.0


def test_runtime_loop_accumulate_updates_parent_frame():
    code = """
L1: X arr arr 1 2 3 Set sum 0 Loop arr item ->L2 ->L3
L2: X sum add sum item J sum
L3: J sum
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == 6


def test_runtime_x_comparisons_for_branching():
    code = """
L1: X c lt 1 2 If c ->L2 ->L3
L2: Set out "ok" J out
L3: Set out "bad" J out
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    out = eng.run_label("1")
    assert out == "ok"


def test_runtime_while_limit_parsed_from_source():
    code = """
L1: Set cond true While cond ->L2 ->L3 limit=2
L2: J "again"
L3: J "done"
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False)
    try:
        eng.run_label("1")
        assert False, "expected while limit error"
    except Exception as e:
        assert "while loop iteration limit exceeded" in str(e)


def test_runtime_error_contains_source_context():
    code = """
L1: R api.G /x ->out J out
"""
    eng = RuntimeEngine.from_code(code, strict=True, trace=False)
    try:
        eng.run_label("1")
        assert False, "expected runtime error"
    except Exception as e:
        msg = str(e)
        assert "line=2" in msg
        assert "R api.G /x ->out J out" in msg


class _AlwaysFail(RuntimeAdapter):
    def call(self, target, args, context):
        raise RuntimeError("always-fail")


class _FailOnce(RuntimeAdapter):
    def __init__(self):
        self.calls = 0

    def call(self, target, args, context):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("boom-once")
        return 7


class _MemCache(RuntimeAdapter):
    def __init__(self):
        self.store = {}

    def get(self, name, key):
        return self.store.get((name, key))

    def set(self, name, key, value, ttl_s=0):
        self.store[(name, key)] = value


class _MemQueue(RuntimeAdapter):
    def __init__(self):
        self.items = []

    def push(self, queue, value):
        self.items.append((queue, value))
        return f"msg-{len(self.items)}"


class _MemTxn(RuntimeAdapter):
    def __init__(self):
        self.actions = []

    def begin(self, name):
        self.actions.append(("begin", name))
        return f"tx-{name}"

    def commit(self, name):
        self.actions.append(("commit", name))

    def rollback(self, name):
        self.actions.append(("rollback", name))


def test_step_mode_err_catches_when_err_after_failing_r():
    code = """
L1: R ext.G /x ->out Err ->L9 J out
L9: Set handled _error J handled
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", _AlwaysFail())
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=True)
    out = eng._run_label("1", {}, [], force_steps=True)
    assert "always-fail" in str(out)


def test_shared_frame_call_semantics():
    code = """
L1: Set x 0 Call L2 J x
L2: Set x 9 J "null"
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False)
    out = eng.run_label("1")
    assert out == 9


def test_step_mode_err_routes_by_explicit_at_node():
    code = """
L1: R core.add 1 2 ->ok R ext.G /x ->out Err @n2 ->L8 J out
L8: Set handled "routed" J handled
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", _AlwaysFail())
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=True)
    out = eng._run_label("1", {}, [], force_steps=True)
    assert out == "routed"


def test_step_mode_err_handler_recursion_is_rejected():
    code = """
L1: R ext.G /x ->out Err ->L1 J out
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    reg.register("ext", _AlwaysFail())
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=True)
    try:
        eng._run_label("1", {}, [], force_steps=True)
        assert False, "expected recursion guard error"
    except Exception as e:
        msg = str(e)
        assert "error handler recursion detected" in msg
        assert "handler=1" in msg
        assert "failing_op=R" in msg


def test_runtime_label_normalization_equivalence_for_run_label():
    code = """
L1: R core.add 1 1 ->x J x
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    assert eng.run_label("1") == 2
    assert eng.run_label("L1") == 2
    assert eng.run_label("->L1") == 2
    assert eng.run_label("L1:entry") == 2


def test_runtime_if_cond_forms_align_with_compiler_tokens():
    code = """
L1: Set status ok Set present 1 If status=ok ->L2 ->L3
L2: If present? ->L4 ->L3
L3: Set out bad J out
L4: Set out good J out
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False)
    assert eng.run_label("1") == "good"


def test_step_mode_retry_targets_at_node_id():
    code = """
L1: R ext.op x ->out Retry @n1 2 0 J out
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    flaky = _FailOnce()
    reg.register("ext", flaky)
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=True)
    out = eng._run_label("1", {}, [], force_steps=True)
    assert out == 7
    assert flaky.calls == 2


def test_step_mode_retry_replays_failing_call():
    code = """
L1: Call L2 ->res Retry @n1 2 0 J res
L2: R ext.op x ->v J v
"""
    reg = AdapterRegistry(allowed=["core", "ext"])
    flaky = _FailOnce()
    reg.register("ext", flaky)
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=True)
    out = eng._run_label("1", {}, [], force_steps=True)
    assert out == 7
    assert flaky.calls == 2


def test_runtime_no_j_returns_none_even_when_data_exists():
    code = """
L1: Set x true
"""
    eng = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False)
    out = eng.run_label("1", {"data": {"legacy": True}})
    assert out is None


def test_compiler_emits_call_out_and_runtime_stores_result_at_out_var():
    code = """
L1: Call L9 ->res J res
L9: R core.add 40 2 ->v J v
"""
    ir = AICodeCompiler(strict_mode=False).compile(code)
    assert not ir.get("errors"), ir.get("errors")
    steps = ir["labels"]["1"]["legacy"]["steps"]
    assert steps[0]["op"] == "Call"
    assert steps[0]["label"] == "9"
    assert steps[0]["out"] == "res"

    eng = RuntimeEngine(ir, AdapterRegistry(allowed=["core"]), trace=False, step_fallback=True)
    out = eng._run_label("1", {}, [], force_steps=True)
    assert out == 42


def test_runtime_executes_canonical_emitted_step_fields_for_control_and_capability_ops():
    code = """
L1:
Set flag true
If flag ->L2 ->L3
Err @n2 ->L9
Retry @n2 2 0
CacheSet memo user:1 7 30
CacheGet memo user:1 ->cached miss
QueuePut jobs cached ->qid
Tx begin default
Enf allow
Call L4 ->res
J res
L2: J ok
L3: J bad
L4: J cached
L9: J _error
"""
    ir = AICodeCompiler(strict_mode=False).compile(code)
    assert not ir.get("errors"), ir.get("errors")
    steps = ir["labels"]["1"]["legacy"]["steps"]
    ops = [s["op"] for s in steps]
    for required in ("If", "Err", "Retry", "CacheSet", "CacheGet", "QueuePut", "Tx", "Enf", "Call"):
        assert required in ops

    reg = AdapterRegistry(allowed=["core", "cache", "queue", "txn"])
    cache = _MemCache()
    queue = _MemQueue()
    txn = _MemTxn()
    reg.register("cache", cache)
    reg.register("queue", queue)
    reg.register("txn", txn)

    # Execute a capability-focused program to assert canonical field handling
    # without early-return control-flow branches short-circuiting execution.
    exec_code = """
L1: CacheSet memo user:1 7 30 CacheGet memo user:1 ->cached miss QueuePut jobs cached ->qid Tx begin default Call L4 ->res J res
L4: J cached
"""
    exec_ir = AICodeCompiler(strict_mode=False).compile(exec_code)
    eng = RuntimeEngine(exec_ir, reg, trace=False, step_fallback=True)
    out = eng._run_label("1", {}, [], force_steps=True)
    assert out == 7
    assert cache.get("memo", "user:1") == 7
    assert queue.items == [("jobs", 7)]
    assert txn.actions == [("begin", "default")]
