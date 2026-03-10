"""Runtime-oriented mock adapters used by RuntimeEngine and emitted server."""
from typing import Any, Dict, List, Optional

from runtime.adapters.base import AdapterError, AdapterRegistry, RuntimeAdapter


class MockDBAdapter(RuntimeAdapter):
    """Entity-aware in-memory DB mock for db.F/G/C/P/U/D calls."""

    def __init__(self, types: Optional[Dict[str, Dict[str, Any]]] = None):
        self.types = types or {}
        self._store: Dict[str, List[Dict[str, Any]]] = {}
        self._seq = 0

    def _sample_row(self, entity: str) -> Dict[str, Any]:
        fields = (self.types.get(entity) or {}).get("fields", {})
        row: Dict[str, Any] = {}
        for key, value in (list(fields.items())[:8] if fields else [("id", "I"), ("name", "S")]):
            if value and ("I" in value or "F" in value):
                row[key] = 1
            else:
                row[key] = "sample"
        return row

    def _entity_rows(self, entity: str) -> List[Dict[str, Any]]:
        rows = self._store.get(entity)
        if rows is None:
            rows = [self._sample_row(entity), self._sample_row(entity)]
            self._store[entity] = rows
        return rows

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        verb = str(target or "").upper()
        entity = str(args[0]) if len(args) > 0 else ""
        payload = args[1] if len(args) > 1 else None
        rows = self._entity_rows(entity)

        if verb == "F":
            return list(rows)
        if verb == "G":
            if payload is None:
                return rows[0] if rows else None
            for row in rows:
                if row.get("id") == payload:
                    return row
            return None
        if verb in {"C", "P"}:
            self._seq += 1
            new_row = self._sample_row(entity)
            if isinstance(payload, dict):
                new_row.update(payload)
            elif payload is not None:
                new_row["value"] = payload
            new_row.setdefault("id", self._seq)
            rows.append(new_row)
            return new_row
        if verb == "U":
            if isinstance(payload, dict) and rows:
                rows[0].update(payload)
                return rows[0]
            return rows[0] if rows else None
        if verb == "D":
            if not rows:
                return False
            if payload is None:
                rows.pop(0)
                return True
            for i, row in enumerate(rows):
                if row.get("id") == payload:
                    rows.pop(i)
                    return True
            return False
        raise AdapterError(f"db verb not supported: {verb}")


class MockAPIAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        verb = str(target or "").upper()
        path = str(args[0]) if args else "/"
        body = args[1] if len(args) > 1 else None
        if verb in {"G", "GET"}:
            return {"ok": True, "path": path, "method": "GET", "data": []}
        if verb in {"P", "POST"}:
            return {"ok": True, "path": path, "method": "POST", "body": body}
        raise AdapterError(f"api verb not supported: {verb}")


class MockPayAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        return {"id": "mock_pi", "client_secret": "mock_secret"}


class MockScrapeAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        return {"ok": True, "target": target}


class MockCacheAdapter(RuntimeAdapter):
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, namespace: str, key: str) -> Any:
        return self._store.get(namespace, {}).get(key)

    def set(self, namespace: str, key: str, value: Any, ttl_s: int = 0) -> None:
        self._store.setdefault(namespace, {})[key] = value

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        verb = str(target or "").lower()
        if verb == "get":
            if len(args) < 2:
                raise AdapterError("cache.get requires namespace and key")
            return self.get(str(args[0]), str(args[1]))
        if verb == "set":
            if len(args) < 3:
                raise AdapterError("cache.set requires namespace, key, value")
            self.set(str(args[0]), str(args[1]), args[2], ttl_s=int(args[3]) if len(args) > 3 else 0)
            return None
        raise AdapterError(f"cache target not supported: {target}")


class MockQueueAdapter(RuntimeAdapter):
    def __init__(self):
        self._queues: Dict[str, List[Any]] = {}
        self._seq = 0

    def push(self, queue: str, value: Any) -> str:
        self._seq += 1
        self._queues.setdefault(queue, []).append(value)
        return f"{queue}:{self._seq}"

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if str(target or "").lower() != "put":
            raise AdapterError(f"queue target not supported: {target}")
        if len(args) < 2:
            raise AdapterError("queue.Put requires queue and payload")
        return self.push(str(args[0]), args[1])


class MockTxnAdapter(RuntimeAdapter):
    def __init__(self):
        self._active: Dict[str, str] = {}
        self._seq = 0

    def begin(self, name: str) -> str:
        self._seq += 1
        txid = f"tx-{name}-{self._seq}"
        self._active[name] = txid
        return txid

    def commit(self, name: str) -> None:
        self._active.pop(name, None)

    def rollback(self, name: str) -> None:
        self._active.pop(name, None)

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        action = str(target or "").lower()
        name = str(args[0]) if args else "default"
        if action == "begin":
            return self.begin(name)
        if action == "commit":
            self.commit(name)
            return None
        if action == "rollback":
            self.rollback(name)
            return None
        raise AdapterError(f"txn target not supported: {target}")


class MockAuthAdapter(RuntimeAdapter):
    def validate(self, token_or_value: str) -> bool:
        value = (token_or_value or "").strip()
        return bool(value) and value.lower() not in {"invalid", "none", "null"}

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if str(target or "").lower() != "validate":
            raise AdapterError(f"auth target not supported: {target}")
        return self.validate(str(args[0]) if args else "")


def mock_registry(types: Optional[Dict[str, Dict[str, Any]]] = None) -> AdapterRegistry:
    """Default runtime adapter registry with permissive mock backends."""
    reg = AdapterRegistry(allowed=["core", "db", "api", "pay", "scrape", "cache", "queue", "txn", "auth", "ext"])
    reg.register("db", MockDBAdapter(types))
    reg.register("api", MockAPIAdapter())
    reg.register("pay", MockPayAdapter())
    reg.register("scrape", MockScrapeAdapter())
    reg.register("cache", MockCacheAdapter())
    reg.register("queue", MockQueueAdapter())
    reg.register("txn", MockTxnAdapter())
    reg.register("auth", MockAuthAdapter())
    return reg
