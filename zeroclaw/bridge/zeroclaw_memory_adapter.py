"""ZeroClaw daily markdown memory: ~/.zeroclaw/workspace/memory/, optional zeroclaw memory CLI search.

``append_today`` / ``read_today`` use direct writes and reads on the daily ``.md`` files (same
stable contract as the OpenClaw bridge). ``search`` tries the ``zeroclaw memory search`` CLI first,
then falls back to scanning ``*.md`` under the memory dir—see comment on ``search`` below for why
we avoid parsing ZeroClaw-internal TOML or DB from Python here.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from runtime.adapters.base import RuntimeAdapter, AdapterError

logger = logging.getLogger(__name__)


def _zeroclaw_bin() -> str:
    return (os.getenv("ZEROCLAW_BIN") or "").strip() or "zeroclaw"


def _dry_run(context: Dict[str, Any]) -> bool:
    v = context.get("dry_run")
    if v in (True, 1, "1", "true", "True", "yes"):
        return True
    return os.environ.get("AINL_DRY_RUN", "").strip().lower() in ("1", "true", "yes")


def zeroclaw_memory_dir() -> Path:
    """Directory for daily `YYYY-MM-DD.md` (ZeroClaw workspace layout)."""
    override = os.getenv("ZEROCLAW_MEMORY_DIR") or os.getenv("ZEROCLAW_DAILY_MEMORY_DIR")
    if override:
        return Path(override).expanduser()
    ws = os.getenv("ZEROCLAW_WORKSPACE", str(Path.home() / ".zeroclaw" / "workspace"))
    return Path(ws).expanduser() / "memory"


def _daily_path() -> Path:
    day = datetime.now().strftime("%Y-%m-%d")
    return zeroclaw_memory_dir() / f"{day}.md"


class _JsonFileCache:
    """Same backing file as monitor CacheAdapter (`MONITOR_CACHE_JSON`)."""

    def __init__(self) -> None:
        self.path = Path(os.getenv("MONITOR_CACHE_JSON", "/tmp/monitor_state.json")).expanduser()

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, data: Dict[str, Any]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError as e:
            logger.warning("zeroclaw_memory cache save failed: %s", e)

    def get(self, namespace: str, key: str) -> Any:
        return self._load().get(namespace, {}).get(key)

    def set(self, namespace: str, key: str, value: Any) -> None:
        data = self._load()
        data.setdefault(namespace, {})[key] = value
        self._save(data)


def _search_files_fallback(query: str, max_results: int) -> List[Dict[str, Any]]:
    mem = zeroclaw_memory_dir()
    if not mem.is_dir():
        return []
    q = query.lower()
    out: List[Dict[str, Any]] = []
    for p in sorted(mem.glob("*.md"), key=lambda x: x.name, reverse=True):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if q not in text.lower():
            continue
        idx = text.lower().find(q)
        snip = text[max(0, idx - 40) : idx + len(query) + 80].replace("\n", " ")
        out.append({"path": str(p), "snippet": snip, "score": 1.0, "source": "file_scan"})
        if len(out) >= max_results:
            break
    return out


class ZeroclawMemoryAdapter(RuntimeAdapter):
    """
    Adapter groups: ``zeroclaw_memory`` (preferred) and compatible registration as ``openclaw_memory``
    so shared wrapper graphs append to ZeroClaw workspace memory paths.
    Verbs: append_today, read_today, search
    """

    _SEARCH_CACHE_TTL_S = 90

    def __init__(self) -> None:
        self._cache = _JsonFileCache()

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        verb = str(target or "").strip().lower()
        dry = _dry_run(context)

        if verb == "append_today":
            if len(args) < 1:
                raise AdapterError("append_today requires text: str")
            text = str(args[0])
            if dry:
                logger.info("[dry_run] zeroclaw_memory.append_today — no write")
                return 1
            path = _daily_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            line = f"- {iso} — {text}\n"
            day = path.stem
            if not path.exists():
                header = f"# Memory Log - {day}\n\n## AINL · ZeroClaw bridge\n\n"
                path.write_text(header + line, encoding="utf-8")
            else:
                body = path.read_text(encoding="utf-8")
                if "## AINL · ZeroClaw bridge" not in body:
                    body = body.rstrip() + "\n\n## AINL · ZeroClaw bridge\n\n"
                body = body.rstrip() + "\n" + line
                path.write_text(body + "\n", encoding="utf-8")
            return 1

        if verb == "read_today":
            path = _daily_path()
            if not path.exists():
                return ""
            return path.read_text(encoding="utf-8")

        # Search: prefer `zeroclaw memory search` when available. We do not read or rewrite
        # ZeroClaw's internal TOML/DB from this adapter—those layouts and Rust-side traits can
        # change release to release. The CLI is the stable, version-agnostic contract; if it is
        # missing or fails, we fall back to scanning daily `*.md` under zeroclaw_memory_dir() so
        # bridge graphs still behave without coupling AINL to future storage details.
        if verb == "search":
            if len(args) < 1:
                raise AdapterError("search requires query: str")
            query = str(args[0])
            ck = hashlib.sha256(query.encode("utf-8")).hexdigest()[:24]
            cached = self._cache.get("zeroclaw_memory_search", ck)
            if isinstance(cached, dict):
                ts = float(cached.get("ts", 0))
                if time.time() - ts < self._SEARCH_CACHE_TTL_S:
                    return cached.get("results", [])
            if dry:
                logger.info("[dry_run] zeroclaw_memory.search — no CLI")
                return []
            bin_path = _zeroclaw_bin()
            try:
                proc = subprocess.run(
                    [
                        bin_path,
                        "memory",
                        "search",
                        "--query",
                        query,
                        "--max-results",
                        "20",
                        "--json",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except FileNotFoundError:
                logger.warning("zeroclaw binary not found: %s", bin_path)
                return _search_files_fallback(query, 20)
            except subprocess.TimeoutExpired:
                logger.warning("zeroclaw memory search timed out")
                return _search_files_fallback(query, 20)
            if proc.returncode != 0:
                return _search_files_fallback(query, 20)
            try:
                data = json.loads(proc.stdout)
            except json.JSONDecodeError as e:
                logger.warning("zeroclaw memory search JSON error: %s", e)
                return _search_files_fallback(query, 20)
            raw = data.get("results") if isinstance(data, dict) else None
            if not isinstance(raw, list) or not raw:
                normalized = _search_files_fallback(query, 20)
            else:
                normalized = []
                for r in raw:
                    if isinstance(r, dict):
                        normalized.append(
                            {
                                "path": r.get("path"),
                                "snippet": r.get("snippet"),
                                "score": r.get("score"),
                                "startLine": r.get("startLine"),
                                "endLine": r.get("endLine"),
                                "source": r.get("source"),
                            }
                        )
            self._cache.set("zeroclaw_memory_search", ck, {"ts": time.time(), "results": normalized})
            return normalized

        raise AdapterError(f"zeroclaw_memory unknown target: {target}")
