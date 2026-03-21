#!/usr/bin/env python3
"""Run orchestration wrappers with ZeroClaw-local memory, queue, and token bridge.

Official location: ``zeroclaw/bridge/`` (ZeroClaw integration layer; not AINL core).

Execution model
---------------
By default this embeds ``RuntimeEngine`` (same pattern as ``openclaw/bridge/run_wrapper_ainl.py``)
with a registry tuned for ``~/.zeroclaw/``. Bare ``ainl run`` does **not** load this registry, so
bridge wrappers should be launched via this script or ``zeroclaw-ainl-run``.

Optional: set ``AINL_ZC_COMPILE_SUBPROCESS=1`` to run ``ainl compile <wrapper>`` in a subprocess
before executing (validates toolchain); graph execution stays in-process.

Usage:
  python3 zeroclaw/bridge/run_wrapper_ainl.py <name> [--dry-run] [--trace] [--verbose]

Dry-run: sets frame[\"dry_run\"] and ``AINL_DRY_RUN`` so adapters skip network/disk side effects.

With ``AINL_ZC_COMPILE_SUBPROCESS=1``, ``--verbose`` logs the ``ainl compile`` subprocess
command, exit code, and stderr (truncated).
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

_BRIDGE_DIR = Path(__file__).resolve().parent
ROOT = _BRIDGE_DIR.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine

from adapters.crm import CrmAdapter
from adapters.github import GitHubAdapter
from adapters.openclaw_defaults import DEFAULT_CRM_HEALTH_URL
from adapters.openclaw_integration import openclaw_monitor_registry

import importlib.util


def _load_bridge_module(stem: str):
    spec = importlib.util.spec_from_file_location(stem, _BRIDGE_DIR / f"{stem}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_zmem = _load_bridge_module("zeroclaw_memory_adapter")
ZeroclawMemoryAdapter = _zmem.ZeroclawMemoryAdapter

_tok = _load_bridge_module("token_budget_adapter")
ZeroclawBridgeTokenBudgetAdapter = _tok.ZeroclawBridgeTokenBudgetAdapter

_q = _load_bridge_module("zeroclaw_queue_adapter")
ZeroclawQueueAdapter = _q.ZeroclawQueueAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ainl.zeroclaw.wrapper")

WRAPPERS = {
    "github-intelligence": ROOT / "scripts" / "wrappers" / "github-intelligence.ainl",
    "content-engine": ROOT / "scripts" / "wrappers" / "content-engine.ainl",
    "supervisor": ROOT / "scripts" / "wrappers" / "supervisor.ainl",
    "full-unification": ROOT / "examples" / "openclaw_full_unification.ainl",
    "token-budget-alert": ROOT / "openclaw" / "bridge" / "wrappers" / "token_budget_alert.ainl",
    "weekly-token-trends": ROOT / "openclaw" / "bridge" / "wrappers" / "weekly_token_trends.ainl",
}


def _crm_health_url() -> str:
    explicit = os.environ.get("CRM_HEALTH_URL")
    if explicit:
        return explicit.strip()
    if os.environ.get("CRM_API_BASE"):
        return f'{os.environ["CRM_API_BASE"].rstrip("/")}/api/health'
    return DEFAULT_CRM_HEALTH_URL


def _zeroclaw_workspace_root() -> str:
    return os.getenv("ZEROCLAW_WORKSPACE", str(Path.home() / ".zeroclaw" / "workspace"))


def build_wrapper_registry():
    if not (os.environ.get("OPENROUTER_API_KEY") or "").strip():
        os.environ["OPENROUTER_API_KEY"] = os.environ.get(
            "AINL_OPENROUTER_PLACEHOLDER_KEY", "unset-openrouter-key-wrapper-registry"
        )
    reg = openclaw_monitor_registry()
    zmem = ZeroclawMemoryAdapter()
    for name in ("openclaw_memory", "zeroclaw_memory", "github", "crm"):
        reg.allow(name)
    # Shared wrappers use R openclaw_memory; under ZeroClaw bridge, route to ~/.zeroclaw workspace files.
    reg.register("openclaw_memory", zmem)
    reg.register("zeroclaw_memory", zmem)
    reg.register("github", GitHubAdapter())
    reg.register("crm", CrmAdapter())
    reg.allow("bridge")
    reg.register("bridge", ZeroclawBridgeTokenBudgetAdapter())
    reg.register("queue", ZeroclawQueueAdapter())

    from runtime.adapters.fs import SandboxedFileSystemAdapter

    reg.register(
        "fs",
        SandboxedFileSystemAdapter(
            sandbox_root=_zeroclaw_workspace_root(),
            max_read_bytes=2_000_000,
            max_write_bytes=2_000_000,
            allow_delete=False,
        ),
    )
    return reg


def _maybe_subprocess_compile(path: Path, *, verbose: bool) -> None:
    if os.environ.get("AINL_ZC_COMPILE_SUBPROCESS", "").strip().lower() not in ("1", "true", "yes"):
        return
    ainl = shutil.which("ainl")
    if not ainl:
        logger.warning("AINL_ZC_COMPILE_SUBPROCESS set but ainl not on PATH; skipping")
        return
    cmd = [ainl, "compile", str(path)]
    if verbose:
        logger.info("AINL_ZC_COMPILE_SUBPROCESS: cwd=%s cmd=%s", ROOT, cmd)
    r = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if verbose:
        logger.info("ainl compile subprocess exit=%s", r.returncode)
        err = (r.stderr or "").strip()
        out = (r.stdout or "").strip()
        if err:
            logger.info("ainl compile stderr (truncated): %s", err[:800])
        if out:
            logger.info("ainl compile stdout (truncated): %s", out[:800])
    if r.returncode != 0:
        logger.warning("subprocess ainl compile failed: %s", (r.stderr or r.stdout)[:400])


def main() -> None:
    argv = [a for a in sys.argv[1:] if a]
    trace = "--trace" in argv
    dry = "--dry-run" in argv
    verbose = "--verbose" in argv or "-v" in argv
    argv = [a for a in argv if a not in ("--trace", "--dry-run", "--verbose", "-v")]
    if not argv:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    name = argv[0]
    path = WRAPPERS.get(name)
    if not path or not path.is_file():
        logger.error("Unknown wrapper %r; known: %s", name, ", ".join(WRAPPERS))
        sys.exit(1)

    _maybe_subprocess_compile(path, verbose=verbose)

    src = path.read_text(encoding="utf-8")
    ir = AICodeCompiler(strict_mode=False, strict_reachability=False).compile(src, emit_graph=True)
    errs = ir.get("errors") or []
    if errs:
        logger.error("Compile errors: %s", errs)
        sys.exit(2)

    reg = build_wrapper_registry()
    eng = RuntimeEngine(ir, adapters=reg, trace=trace, execution_mode="graph-preferred")
    frame: dict = {
        "crm_health_url": _crm_health_url(),
    }
    if dry:
        frame["dry_run"] = True
        os.environ.setdefault("AINL_DRY_RUN", "1")

    try:
        out = eng.run_label("0", frame)
    except Exception as e:
        logger.exception("Runtime error: %s", e)
        sys.exit(3)

    payload = {"ok": True, "wrapper": name, "out": out}
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
