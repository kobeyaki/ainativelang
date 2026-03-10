from __future__ import annotations

from typing import Any, Dict, List, Optional

from runtime.adapters.base import RuntimeAdapter
from runtime.adapters.replay import RecordingAdapterRegistry, ReplayAdapterRegistry


class RecordingAdapter(RuntimeAdapter):
    def __init__(self, default_return: Any = None):
        self.default_return = default_return
        self.calls: List[Dict[str, Any]] = []

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        ret = self.default_return
        if target == "echo":
            ret = args[0] if args else None
        self.calls.append(
            {
                "target": target,
                "args": list(args),
                "result": ret,
            }
        )
        return ret


# Re-export concrete registries for tests, adding ext-friendly defaults where needed.
class TestRecordingAdapterRegistry(RecordingAdapterRegistry):
    def __init__(self, allowed: Optional[List[str]] = None):
        super().__init__(allowed=allowed or ["core", "ext"])


class TestReplayAdapterRegistry(ReplayAdapterRegistry):
    def __init__(self, replay_log: List[Dict[str, Any]], allowed: Optional[List[str]] = None):
        super().__init__(replay_log, allowed=allowed or ["core", "ext"])


# Backward-compatible test aliases.
RecordingAdapterRegistry = TestRecordingAdapterRegistry
ReplayAdapterRegistry = TestReplayAdapterRegistry
