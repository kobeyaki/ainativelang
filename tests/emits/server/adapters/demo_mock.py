"""Mock adapters plus email/calendar/social for demo runtime usage."""
from typing import Any, Dict, List, Optional
import time

from runtime.adapters.base import AdapterRegistry, RuntimeAdapter

from .mock import (
    MockAPIAdapter,
    MockAuthAdapter,
    MockCacheAdapter,
    MockDBAdapter,
    MockPayAdapter,
    MockQueueAdapter,
    MockTxnAdapter,
)


class _MockEmailAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if str(target or "").upper() != "G":
            return []
        now = int(time.time())
        return [
            {"id": "e1", "subject": "Update", "date": now - 300},
            {"id": "e2", "subject": "News", "date": now - 60},
        ]


class _MockCalendarAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if str(target or "").upper() != "G":
            return []
        now = int(time.time())
        return [
            {"id": "ev1", "title": "Meeting", "start": now + 3600},
            {"id": "ev2", "title": "Lunch", "start": now + 7200},
        ]


class _MockSocialAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if str(target or "").upper() != "G":
            return []
        now = int(time.time())
        return [
            {"id": "m1", "text": "Hello", "ts": now - 90},
            {"id": "m2", "text": "World", "ts": now - 30},
        ]


def mock_registry(types: Optional[Dict[str, Dict[str, Any]]] = None) -> AdapterRegistry:
    reg = AdapterRegistry(
        allowed=["core", "db", "api", "pay", "scrape", "cache", "queue", "txn", "auth", "email", "calendar", "social"]
    )
    reg.register("db", MockDBAdapter(types))
    reg.register("api", MockAPIAdapter())
    reg.register("cache", MockCacheAdapter())
    reg.register("queue", MockQueueAdapter())
    reg.register("auth", MockAuthAdapter())
    reg.register("pay", MockPayAdapter())
    reg.register("txn", MockTxnAdapter())
    reg.register("email", _MockEmailAdapter())
    reg.register("calendar", _MockCalendarAdapter())
    reg.register("social", _MockSocialAdapter())
    return reg