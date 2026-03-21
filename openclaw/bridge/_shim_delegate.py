"""Shared loader for `scripts/*` shims. All bridge logic lives in sibling `.py` files."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_BRIDGE_DIR = Path(__file__).resolve().parent


def run_bridge_script(script_basename: str) -> None:
    """Execute ``openclaw/bridge/<script_basename>`` as __main__ (preserves sys.argv)."""
    target = _BRIDGE_DIR / script_basename
    if not target.is_file():
        print(
            f"ainl bridge: missing {target}\n"
            "  Check that the repo checkout is complete and openclaw/bridge/ exists.",
            file=sys.stderr,
        )
        sys.exit(127)
    runpy.run_path(str(target), run_name="__main__")
