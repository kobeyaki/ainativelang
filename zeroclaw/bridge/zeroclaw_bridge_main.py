#!/usr/bin/env python3
"""Git-style entrypoint for ZeroClaw bridge tools (delegates to scripts in this directory)."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_BRIDGE = Path(__file__).resolve().parent

_SKIP_DISCOVER = frozenset(
    {
        "zeroclaw_bridge_main.py",
        "__init__.py",
    }
)

_EXPLICIT_SCRIPT_STEMS = frozenset(
    {
        "run_wrapper_ainl",
        "cron_drift_check",
        "ainl_memory_append_cli",
    }
)

_EXPLICIT: dict[str, str] = {
    "run-wrapper": "run_wrapper_ainl.py",
    "drift-check": "cron_drift_check.py",
    "memory-append": "ainl_memory_append_cli.py",
}


def _discovered() -> dict[str, str]:
    """CLI name (hyphenated) -> bridge script basename."""
    out: dict[str, str] = {}
    for p in sorted(_BRIDGE.glob("*.py")):
        if p.name in _SKIP_DISCOVER:
            continue
        if p.stem.startswith("test_"):
            continue
        if p.stem in _EXPLICIT_SCRIPT_STEMS:
            continue
        rel = p.relative_to(_BRIDGE)
        if "tests" in rel.parts:
            continue
        cli = p.stem.replace("_", "-")
        if cli in _EXPLICIT or cli in out:
            continue
        out[cli] = p.name
    if out.get("token-usage-reporter") == "token_usage_reporter.py":
        out["token-usage"] = out.pop("token-usage-reporter")
    return out


def _all_commands() -> dict[str, str]:
    m = dict(_discovered())
    m.update(_EXPLICIT)
    return m


def _print_help() -> None:
    auto = _discovered()
    names = sorted(_all_commands().keys())
    print(
        "usage: python3 zeroclaw/bridge/zeroclaw_bridge_main.py <command> [args...]\n\n"
        "ZeroClaw bridge entrypoint: runs tools in zeroclaw/bridge/. "
        "Uses ~/.zeroclaw/ paths, ZEROCLAW_* env vars, and zeroclaw CLI where applicable.\n"
    )
    print("commands:\n  " + "\n  ".join(names))
    print(
        "\nAuto-discovered tools (subset): "
        + (", ".join(sorted(auto)) if auto else "(none)")
        + "\n\nArguments after <command> are forwarded verbatim (--dry-run, --json, etc.)."
    )


def _run_script(filename: str, forward: list[str]) -> None:
    sys.argv = [filename] + forward
    runpy.run_path(str(_BRIDGE / filename), run_name="__main__")


def main() -> None:
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        _print_help()
        sys.exit(0)
    cmd, *rest = argv
    cmap = _all_commands()
    if cmd not in cmap:
        print(f"zeroclaw_bridge_main.py: unknown command {cmd!r} (try --help)", file=sys.stderr)
        sys.exit(2)
    _run_script(cmap[cmd], rest)


if __name__ == "__main__":
    main()
