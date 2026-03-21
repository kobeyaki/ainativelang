#!/usr/bin/env python3
"""# Shim: delegates to openclaw/bridge/ainl_memory_append_cli.py — do NOT edit logic here; edit in bridge/.

``scripts/`` is not a Python package; this file loads ``openclaw/bridge/_shim_delegate.py`` via
importlib. Respects ``AINL_DRY_RUN`` the same as the bridge script.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TARGET = "ainl_memory_append_cli.py"
_HELP = f"""{_TARGET} shim — delegates to openclaw/bridge/{_TARGET} (via openclaw/bridge/_shim_delegate.py).

Implementation is defined in openclaw/bridge/ only.
"""


def main() -> None:
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print(_HELP, end="")
        sys.exit(0)
    root = Path(__file__).resolve().parent.parent
    delegate_path = root / "openclaw" / "bridge" / "_shim_delegate.py"
    if not delegate_path.is_file():
        print(
            f"ainl shim: missing {delegate_path}\n"
            "  Clone or restore the repo so openclaw/bridge/ is present.",
            file=sys.stderr,
        )
        sys.exit(127)
    try:
        spec = importlib.util.spec_from_file_location("ainl_openclaw_shim_delegate", delegate_path)
        if spec is None or spec.loader is None:
            raise ImportError("invalid spec for _shim_delegate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except ImportError as e:
        print(
            f"ainl shim: ImportError loading bridge delegate ({e}).\n"
            "  Check that openclaw/bridge/_shim_delegate.py exists and is readable.",
            file=sys.stderr,
        )
        sys.exit(127)
    try:
        mod.run_bridge_script(_TARGET)
    except SystemExit:
        raise
    except Exception as e:
        print(f"ainl shim: delegation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
