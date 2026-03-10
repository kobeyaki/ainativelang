from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional

from runtime.adapters.base import AdapterError, ToolsAdapter


class ToolBridgeAdapter(ToolsAdapter):
    def __init__(self, tools: Dict[str, Callable[..., Any]], *, allow_tools: Optional[Iterable[str]] = None):
        self.tools = dict(tools or {})
        self.allow_tools = set(allow_tools or self.tools.keys())

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        name = str(target or "").strip()
        if not name:
            raise AdapterError("tools target missing")
        if name not in self.allow_tools:
            raise AdapterError(f"tool blocked by allowlist: {name}")
        fn = self.tools.get(name)
        if fn is None:
            raise AdapterError(f"tool not registered: {name}")
        try:
            return fn(*(args or []), context=context)
        except TypeError:
            try:
                return fn(*(args or []))
            except Exception as e:
                raise AdapterError(f"tool execution error: {e}") from e
        except Exception as e:
            raise AdapterError(f"tool execution error: {e}") from e
