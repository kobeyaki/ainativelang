"""Loader for the adapter manifest JSON.

Provides ``ADAPTER_MANIFEST`` as a module-level dict so other tooling
modules can ``from tooling.adapter_manifest import ADAPTER_MANIFEST``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

_PATH = Path(__file__).resolve().parent / "adapter_manifest.json"

ADAPTER_MANIFEST: Dict[str, Any] = {}

try:
    ADAPTER_MANIFEST = json.loads(_PATH.read_text(encoding="utf-8"))
except (FileNotFoundError, json.JSONDecodeError):
    pass
