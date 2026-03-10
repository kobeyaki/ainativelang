import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.adapters.base import AdapterError
from runtime.adapters.sqlite import SimpleSqliteAdapter


def test_sqlite_adapter_query_and_execute_contract():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "t.db")
        adp = SimpleSqliteAdapter(db, allow_write=True)
        adp.call("execute", ["CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)"], {})
        adp.call("execute", ["INSERT INTO items(name) VALUES (?)", ["a"]], {})
        rows = adp.call("query", ["SELECT id, name FROM items ORDER BY id"], {})
        assert isinstance(rows, list)
        assert rows[0]["name"] == "a"


def test_sqlite_adapter_blocks_write_when_not_allowed():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "t.db")
        adp = SimpleSqliteAdapter(db, allow_write=False)
        try:
            adp.call("execute", ["CREATE TABLE x (id INTEGER)"], {})
            assert False, "expected write block"
        except Exception as e:
            assert isinstance(e, AdapterError)
            assert "allow_write" in str(e)


def test_sqlite_adapter_table_allowlist():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "t.db")
        adp = SimpleSqliteAdapter(db, allow_write=True, allow_tables=["allowed"])
        adp.call("execute", ["CREATE TABLE allowed (id INTEGER PRIMARY KEY, n TEXT)"], {})
        adp.call("execute", ["INSERT INTO allowed(n) VALUES ('x')"], {})
        ok = adp.call("query", ["SELECT id, n FROM allowed"], {})
        assert ok and ok[0]["n"] == "x"
        try:
            adp.call("query", ["SELECT * FROM blocked"], {})
            assert False, "expected table allowlist block"
        except Exception as e:
            assert isinstance(e, AdapterError)
            assert "allowlist" in str(e)
