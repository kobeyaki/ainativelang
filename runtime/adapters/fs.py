from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from runtime.adapters.base import AdapterError, FileSystemAdapter


class SandboxedFileSystemAdapter(FileSystemAdapter):
    def __init__(
        self,
        sandbox_root: str,
        *,
        max_read_bytes: int = 1_000_000,
        max_write_bytes: int = 1_000_000,
        allow_extensions: Optional[Iterable[str]] = None,
        allow_delete: bool = False,
    ):
        self.root = Path(sandbox_root).resolve()
        self.max_read_bytes = int(max_read_bytes)
        self.max_write_bytes = int(max_write_bytes)
        self.allow_extensions = set(allow_extensions or [])
        self.allow_delete = bool(allow_delete)
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, rel: str) -> Path:
        p = (self.root / str(rel)).resolve()
        if p != self.root and self.root not in p.parents:
            raise AdapterError("fs path escapes sandbox root")
        if self.allow_extensions and p.suffix and p.suffix not in self.allow_extensions:
            raise AdapterError(f"fs extension blocked: {p.suffix}")
        return p

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        t = (target or "").strip().lower()
        if t not in {"read", "readlines", "write", "list", "delete", "exists", "mkdir"}:
            raise AdapterError(f"unsupported fs target: {target}")
        if not args:
            raise AdapterError("fs adapter missing path argument")
        p = self._safe_path(str(args[0]))

        if t == "read":
            if not p.exists() or not p.is_file():
                raise AdapterError("fs read target does not exist")
            data = p.read_bytes()
            if len(data) > self.max_read_bytes:
                raise AdapterError("fs read exceeds max_read_bytes")
            return data.decode("utf-8", errors="replace")

        if t == "readlines":
            if not p.exists() or not p.is_file():
                raise AdapterError("fs readlines target does not exist")
            data = p.read_bytes()
            if len(data) > self.max_read_bytes:
                raise AdapterError("fs readlines exceeds max_read_bytes")
            return data.decode("utf-8", errors="replace").splitlines()

        if t == "exists":
            return p.exists()

        if t == "mkdir":
            p.mkdir(parents=True, exist_ok=True)
            return {"ok": True}

        if t == "write":
            content = args[1] if len(args) > 1 else ""
            text = content if isinstance(content, str) else str(content)
            raw = text.encode("utf-8")
            if len(raw) > self.max_write_bytes:
                raise AdapterError("fs write exceeds max_write_bytes")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
            return {"ok": True, "bytes": len(raw)}

        if t == "list":
            if not p.exists():
                return []
            if not p.is_dir():
                raise AdapterError("fs list target must be a directory")
            return sorted([x.name for x in p.iterdir()])

        if not self.allow_delete:
            raise AdapterError("fs delete blocked by policy")
        if p.exists():
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                for ch in p.iterdir():
                    if ch.is_file():
                        ch.unlink()
        return {"ok": True}
