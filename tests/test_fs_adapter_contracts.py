import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.adapters.base import AdapterError
from runtime.adapters.fs import SandboxedFileSystemAdapter


def test_fs_adapter_write_read_list_in_sandbox():
    with tempfile.TemporaryDirectory() as td:
        adp = SandboxedFileSystemAdapter(td)
        w = adp.call("write", ["notes/a.txt", "hello"], {})
        assert w["ok"] is True
        txt = adp.call("read", ["notes/a.txt"], {})
        assert txt == "hello"
        entries = adp.call("list", ["notes"], {})
        assert "a.txt" in entries


def test_fs_adapter_blocks_path_escape():
    with tempfile.TemporaryDirectory() as td:
        adp = SandboxedFileSystemAdapter(td)
        try:
            adp.call("write", ["../escape.txt", "x"], {})
            assert False, "expected sandbox escape block"
        except Exception as e:
            assert isinstance(e, AdapterError)
            assert "sandbox" in str(e)


def test_fs_adapter_enforces_size_caps_and_policy():
    with tempfile.TemporaryDirectory() as td:
        adp = SandboxedFileSystemAdapter(td, max_write_bytes=4, allow_delete=False)
        try:
            adp.call("write", ["a.txt", "toolong"], {})
            assert False, "expected size cap block"
        except Exception as e:
            assert isinstance(e, AdapterError)
            assert "max_write_bytes" in str(e)
        adp.call("write", ["a.txt", "ok"], {})
        try:
            adp.call("delete", ["a.txt"], {})
            assert False, "expected delete policy block"
        except Exception as e:
            assert isinstance(e, AdapterError)
            assert "blocked by policy" in str(e)
