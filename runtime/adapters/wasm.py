from __future__ import annotations

"""
WASM compute adapter for AI-Native Lang.

This adapter lets AINL R steps call WebAssembly modules in a sandboxed runtime.

Contract (surface AINL form):

    L1: R wasm.CALL metrics.add ->module_args ->out

Where the lowered step has:
    adapter = "wasm.CALL"
    target  = "metrics.add"              # "<module_name>.<export_name>"
    args    = [...]                      # positional args to the wasm function

Runtime wiring:
- The WasmAdapter is registered under the name "wasm" in AdapterRegistry.
- The verb is taken from adapter ("CALL"); the function/module come from target.

Implementation:
- Uses the `wasmtime` Python bindings, if installed.
- Loads modules from a name -> path mapping passed at construction.
- Caches Module/Instance per module name for efficiency.
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

from runtime.adapters.base import AdapterError, RuntimeAdapter

try:
    import wasmtime  # type: ignore[import]
except Exception:  # pragma: no cover - optional dependency
    wasmtime = None  # type: ignore[assignment]


class WasmAdapter(RuntimeAdapter):
    def __init__(self, modules: Dict[str, str], allowed_modules: Optional[Iterable[str]] = None) -> None:
        """
        modules: mapping of module_name -> filesystem path to .wasm/.wat file.
        allowed_modules: optional subset of module names that are permitted.
        """
        if wasmtime is None:
            raise AdapterError("wasmtime is not installed; install the 'wasmtime' package to use WasmAdapter")
        self._modules: Dict[str, str] = dict(modules or {})
        self._allowed: set[str] = set(allowed_modules or self._modules.keys())
        if not self._modules:
            raise AdapterError("WasmAdapter requires at least one module mapping (module_name -> path)")

        # Engine/Store are cheap; cache per adapter.
        self._engine = wasmtime.Engine()  # type: ignore[attr-defined]
        self._instances: Dict[str, Tuple[Any, Any]] = {}  # module_name -> (store, instance)

    def _load_instance(self, module_name: str) -> Tuple[Any, Any]:
        if module_name not in self._allowed:
            raise AdapterError(f"wasm module blocked by allowlist: {module_name}")
        if module_name in self._instances:
            return self._instances[module_name]
        path = self._modules.get(module_name)
        if not path:
            raise AdapterError(f"wasm module not configured: {module_name}")
        try:
            module = wasmtime.Module.from_file(self._engine, path)  # type: ignore[attr-defined]
        except Exception as e:  # pragma: no cover - depends on local files
            raise AdapterError(f"failed to load wasm module {module_name!r} from {path!r}: {e}") from e
        store = wasmtime.Store(self._engine)  # type: ignore[attr-defined]
        try:
            instance = wasmtime.Instance(store, module, [])  # type: ignore[attr-defined]
        except Exception as e:  # pragma: no cover
            raise AdapterError(f"failed to instantiate wasm module {module_name!r}: {e}") from e
        self._instances[module_name] = (store, instance)
        return store, instance

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        """
        target: verb string from adapter (e.g., "CALL").
        args: [module_name, export_name, *fn_args].
        """
        verb = (target or "").strip().upper()
        if verb not in ("CALL", "APPLY"):
            raise AdapterError(f"unsupported wasm verb: {verb!r} (expected CALL/APPLY)")
        if len(args) < 2:
            raise AdapterError("wasm.CALL requires at least module_name and export_name arguments")
        module_name = str(args[0])
        export = str(args[1])
        fn_args = list(args[2:])

        store, instance = self._load_instance(module_name)
        try:
            exports = instance.exports(store)  # type: ignore[attr-defined]
            func = exports[export]
        except Exception as e:
            raise AdapterError(f"wasm export {export!r} not found in module {module_name!r}: {e}") from e

        # wasmtime functions are callable with (store, *args).
        try:
            result = func(store, *fn_args)
        except TypeError as e:
            raise AdapterError(f"wasm call type error for {module_name}.{export}: {e}") from e
        except Exception as e:  # pragma: no cover - runtime traps
            raise AdapterError(f"wasm call failed for {module_name}.{export}: {e}") from e
        return result


__all__ = ["WasmAdapter"]
