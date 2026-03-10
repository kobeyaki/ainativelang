import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler
from runtime import ExecutionEngine
from runtime.adapters.base import AdapterRegistry, RuntimeAdapter
from runtime.engine import RuntimeEngine
from adapters.base import AdapterRegistry as LegacyAdapterRegistry
from adapters.base import APIAdapter, CacheAdapter, DBAdapter


class _MemDB(RuntimeAdapter):
    def __init__(self):
        self.rows: Dict[str, List[Dict[str, Any]]] = {}

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        verb = str(target or "").upper()
        entity = str(args[0]) if len(args) > 0 else ""
        if verb == "P":
            payload = args[1] if len(args) > 1 and isinstance(args[1], dict) else {}
            rows = self.rows.setdefault(entity, [])
            rid = len(rows) + 1
            row = {"id": rid, **payload}
            rows.append(row)
            return row
        if verb == "F":
            return list(self.rows.get(entity, []))
        if verb == "G":
            rid = args[1] if len(args) > 1 else None
            for row in self.rows.get(entity, []):
                if row.get("id") == rid:
                    return dict(row)
            return None
        if verb == "D":
            rid = args[1] if len(args) > 1 else None
            rows = self.rows.get(entity, [])
            before = len(rows)
            self.rows[entity] = [r for r in rows if r.get("id") != rid]
            return before != len(self.rows[entity])
        raise RuntimeError(f"unsupported db verb: {verb}")


class _MemAPI(RuntimeAdapter):
    def __init__(self):
        self.store: Dict[str, Any] = {}

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        verb = str(target or "").upper()
        path = str(args[0]) if len(args) > 0 else "/"
        if verb == "P":
            body = args[1] if len(args) > 1 else None
            self.store[path] = body
            return {"ok": True, "path": path, "body": body}
        if verb == "G":
            return {"path": path, "body": self.store.get(path)}
        raise RuntimeError(f"unsupported api verb: {verb}")


class _MemCache(RuntimeAdapter):
    def __init__(self):
        self.ns: Dict[str, Dict[str, Any]] = {}

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        raise RuntimeError("unused")

    def get(self, namespace: str, key: str) -> Any:
        return self.ns.get(namespace, {}).get(key)

    def set(self, namespace: str, key: str, value: Any, ttl_s: int = 0) -> None:
        self.ns.setdefault(namespace, {})[key] = value


class _MemQueue(RuntimeAdapter):
    def __init__(self):
        self.seq = 0

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        raise RuntimeError("unused")

    def push(self, queue: str, value: Any) -> str:
        self.seq += 1
        return f"{queue}:{self.seq}"


class _MemTxn(RuntimeAdapter):
    def __init__(self):
        self.seq = 0
        self.active: Dict[str, str] = {}

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        raise RuntimeError("unused")

    def begin(self, name: str) -> str:
        self.seq += 1
        txid = f"{name}:{self.seq}"
        self.active[name] = txid
        return txid

    def commit(self, name: str) -> None:
        self.active.pop(name, None)

    def rollback(self, name: str) -> None:
        self.active.pop(name, None)


class _FailOnce(RuntimeAdapter):
    def __init__(self):
        self.calls = 0

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("boom-once")
        return {"ok": True}


def _registry() -> AdapterRegistry:
    reg = AdapterRegistry(allowed=["core", "db", "api", "cache", "queue", "txn", "ext"])
    reg.register("db", _MemDB())
    reg.register("api", _MemAPI())
    reg.register("cache", _MemCache())
    reg.register("queue", _MemQueue())
    reg.register("txn", _MemTxn())
    return reg


def _strict_errors(code: str) -> List[str]:
    return list(AICodeCompiler(strict_mode=True).compile(code, emit_graph=True).get("errors", []))


def _assert_strict_ok(code: str) -> None:
    errs = _strict_errors(code)
    assert not errs, errs


def _assert_strict_needs_quote(code: str, token: str) -> None:
    errs = _strict_errors(code)
    assert any(f"reads '{token}'" in e for e in errs), errs
    assert any("quote it explicitly" in e for e in errs), errs


def test_runtime_compiler_r_shape_db_and_api_verbs():
    code = """
L1: R db.P User payload ->created R db.G User 1 ->one R db.F User * ->all R db.D User 1 ->deleted R api.P /users payload ->posted R api.G /users ->fetched J fetched
"""
    ir = AICodeCompiler(strict_mode=False).compile(code, emit_graph=True)
    steps = ir["labels"]["1"]["legacy"]["steps"]
    assert all(s.get("op") in {"R", "J"} for s in steps)
    assert steps[0].get("adapter") == "db.P"
    assert any(s.get("adapter") == "api.P" for s in steps)

    out = RuntimeEngine(ir=ir, adapters=_registry(), trace=False, step_fallback=False).run_label("1", {"payload": {"name": "n"}})
    assert isinstance(out, dict)
    assert out.get("path") == "/users"


def test_runtime_compiler_if_and_call_out_binding():
    code = """
L1: Set cond true If cond ->L2 ->L3
L2: Call L9 ->ans J ans
L3: Set bad nope J bad
L9: R core.add 20 22 ->v J v
"""
    out = RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False).run_label("1")
    assert out == 42


def test_runtime_compiler_err_retry_explicit_and_implicit_targeting():
    code = """
L1: R ext.G /x ->a R ext.G /y ->b Retry @n2 2 0 Err @n2 ->L9 J b
L9: Set handled _error J handled
"""
    reg = _registry()
    class _FailOnSecond(RuntimeAdapter):
        def __init__(self):
            self.calls = 0

        def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("boom-on-second")
            return {"ok": True}

    flaky = _FailOnSecond()
    reg.register("ext", flaky)
    out = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=True).run_label("1")
    assert out == {"ok": True}


def test_compiler_strict_allows_retry_port_on_call_source():
    code = """
L1: Call L2 ->res Retry @n1 2 0 J res
L2: R ext.G /x ->v J v
"""
    _assert_strict_ok(code)


def test_compiler_strict_requires_quotes_for_string_literals():
    _assert_strict_ok('L1: Set out "ok" J out\n')
    _assert_strict_needs_quote("L1: Set out ok J out\n", "ok")


def test_compiler_strict_requires_quotes_for_filt_cache_queue_value_fields():
    _assert_strict_ok('L1: Set src "arr" Filt out src field = "v" J out\n')
    _assert_strict_needs_quote('L1: Set src "arr" Filt out src field = v J out\n', "v")

    _assert_strict_ok('C ns k 60\nL1: CacheSet ns "k" "v" 0 CacheGet ns "k" ->out J out\n')
    _assert_strict_needs_quote('C ns k 60\nL1: CacheSet ns "k" v 0 CacheGet ns "k" ->out J out\n', "v")

    _assert_strict_ok('Q jobs 100 3\nL1: QueuePut jobs "payload" ->msg J msg\n')
    _assert_strict_needs_quote("Q jobs 100 3\nL1: QueuePut jobs payload ->msg J msg\n", "payload")


def test_compiler_strict_quoted_literal_matrix_set_and_cacheget():
    _assert_strict_ok('L1: Set out "ok" J out\n')
    _assert_strict_needs_quote("L1: Set out ok J out\n", "ok")

    _assert_strict_ok('C ns k 60\nL1: CacheGet ns "k" ->out J out\n')
    _assert_strict_needs_quote("C ns k 60\nL1: CacheGet ns k ->out J out\n", "k")

    _assert_strict_ok('C ns k 60\nL1: CacheGet ns "missing" ->out "fallback" J out\n')
    _assert_strict_needs_quote('C ns k 60\nL1: CacheGet ns "missing" ->out fallback J out\n', "fallback")


def test_compiler_diagnostics_emit_structured_location_metadata_when_available() -> None:
    code = "S core web /api\nE /users G ->1\n"
    ir = AICodeCompiler(strict_mode=True).compile(code, emit_graph=True)
    diags = list(ir.get("diagnostics", []) or [])
    assert diags, ir
    errs = [d for d in diags if d.get("severity") == "error"]
    assert errs, diags
    assert all("code" in d and "message" in d and "severity" in d for d in errs), errs
    # At least one strict compiler error in this case should carry structured location.
    assert any(("lineno" in d) or isinstance(d.get("span"), dict) for d in errs), errs


def test_runtime_compiler_loop_and_while_contract():
    code = """
L1: X arr arr 1 2 3 Set sum 0 Loop arr item ->L2 ->L3
L2: X sum add sum item J sum
L3: J sum
"""
    assert RuntimeEngine.from_code(code, strict=False, trace=False, step_fallback=False).run_label("1") == 6

    code_while = """
L1: Set cond true While cond ->L2 ->L3 limit=2
L2: J keep
L3: J done
"""
    try:
        RuntimeEngine.from_code(code_while, strict=False, trace=False, step_fallback=False).run_label("1")
        assert False, "expected while limit error"
    except Exception as e:
        assert "while loop iteration limit exceeded" in str(e)


def test_runtime_compiler_capability_ops_and_policy_enforcement():
    code = """
Pol adminOnly role=admin auth=true
L1: CacheSet ns k payload 0 CacheGet ns k ->c QueuePut jobs c ->msg Tx begin tx1 Enf adminOnly Tx commit tx1 J c
"""
    reg = _registry()
    out = RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=False).run_label(
        "1",
        {"payload": {"id": 1}, "_auth_present": True, "_role": "admin"},
    )
    assert out == {"id": 1}

    try:
        RuntimeEngine.from_code(code, strict=False, trace=False, adapters=reg, step_fallback=False).run_label(
            "1",
            {"payload": {"id": 1}, "_auth_present": False, "_role": "user"},
        )
        assert False, "expected enforcement failure"
    except Exception as e:
        assert "POLICY_VIOLATION" in str(e)


def test_runtime_compat_execution_engine_is_thin_wrapper():
    class _LegacyDb(DBAdapter):
        def find(self, entity: str, fields: str = "*") -> List[Dict[str, Any]]:
            return [{"id": 1, "name": "sample"}]

    class _LegacyApi(APIAdapter):
        def get(self, path: str) -> Any:
            return {"path": path}

    class _LegacyCache(CacheAdapter):
        def __init__(self):
            self.ns: Dict[str, Dict[str, Any]] = {}

        def get(self, namespace: str, key: str) -> Any:
            return self.ns.get(namespace, {}).get(key)

        def set(self, namespace: str, key: str, value: Any, ttl_s: int = 0) -> None:
            self.ns.setdefault(namespace, {})[key] = value

    code = """
L1: R db.F User * ->users J users
"""
    ir = AICodeCompiler(strict_mode=False).compile(code, emit_graph=True)
    legacy = LegacyAdapterRegistry(db=_LegacyDb(), api=_LegacyApi(), cache=_LegacyCache())
    eng = ExecutionEngine(ir, legacy)
    out = eng.run("1")
    assert isinstance(out, list)
