#!/usr/bin/env python3
"""AINL MCP Server — workflow-level MCP integration for AI coding agents.

Exposes AINL compilation, validation, execution, capability discovery, and
security introspection as MCP tools.  Designed for stdio transport so any
MCP-compatible host (Gemini CLI, Claude Code, Codex Agents SDK, etc.) can
discover and call AINL without custom integration code.

Security posture:
  - Safe-by-default: ``ainl-run`` is restricted to the ``core`` adapter with
    conservative limits.  Callers can add *further* restrictions via a
    ``policy`` parameter but can never widen beyond the server defaults.
  - Read-only tools (validate, compile, capabilities, security-report) have
    no side effects.

Requires Python >=3.10 and the ``mcp`` extra:
    pip install -e ".[mcp]"

Run:
    ainl-mcp                     # stdio (default)
    python -m scripts.ainl_mcp_server
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP

    _HAS_MCP = True
except ImportError:
    _HAS_MCP = False

from compiler_v2 import AICodeCompiler
from runtime.adapters.base import AdapterRegistry, RuntimeAdapter
from runtime.engine import AinlRuntimeError, RuntimeEngine, RUNTIME_VERSION
from tooling.policy_validator import validate_ir_against_policy
from tooling.security_report import analyze_ir

_TOOLING_DIR = Path(__file__).resolve().parent.parent / "tooling"

_DEFAULT_ALLOWED_ADAPTERS: List[str] = ["core"]
_DEFAULT_POLICY: Dict[str, Any] = {
    "forbidden_privilege_tiers": ["local_state", "network", "operator_sensitive"],
}
_DEFAULT_LIMITS: Dict[str, Any] = {
    "max_steps": 500,
    "max_depth": 10,
    "max_adapter_calls": 50,
    "max_time_ms": 5000,
}

_mcp_server: Any = None

if _HAS_MCP:
    _mcp_server = FastMCP(
        "AINL",
        instructions=(
            "AINL is a graph-canonical workflow execution layer. "
            "Use ainl-validate to check syntax, ainl-compile to produce IR, "
            "ainl-capabilities to discover adapters, ainl-security-report to "
            "audit privilege tiers, and ainl-run to execute workflows."
        ),
    )


def _compile(code: str, strict: bool = True) -> Dict[str, Any]:
    compiler = AICodeCompiler(strict_mode=strict)
    return compiler.compile(code)


def _load_json(name: str) -> Dict[str, Any]:
    path = _TOOLING_DIR / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _load_capabilities() -> Dict[str, Any]:
    manifest = _load_json("adapter_manifest.json")
    adapters: Dict[str, Any] = {}
    for name, info in (manifest.get("adapters") or {}).items():
        adapters[name] = {
            "support_tier": info.get("support_tier"),
            "verbs": info.get("verbs", []),
            "effect_default": info.get("effect_default"),
            "recommended_lane": info.get("recommended_lane"),
            "privilege_tier": info.get("privilege_tier"),
        }
    return {
        "schema_version": "1.0",
        "runtime_version": RUNTIME_VERSION,
        "policy_support": True,
        "adapters": adapters,
    }


def _merge_policy(caller_policy: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Restrictively merge caller policy on top of server defaults."""
    merged: Dict[str, Any] = {}
    for key in ("forbidden_adapters", "forbidden_effects",
                "forbidden_effect_tiers", "forbidden_privilege_tiers"):
        base = set(_DEFAULT_POLICY.get(key) or [])
        extra = set((caller_policy or {}).get(key) or [])
        combined = sorted(base | extra)
        if combined:
            merged[key] = combined
    return merged


def _merge_limits(caller_limits: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge caller limits with server defaults — take the more restrictive."""
    merged = dict(_DEFAULT_LIMITS)
    for key, default_val in _DEFAULT_LIMITS.items():
        caller_val = (caller_limits or {}).get(key)
        if caller_val is not None:
            merged[key] = min(int(caller_val), int(default_val))
    return merged


class _EchoAdapter(RuntimeAdapter):
    def call(self, target: str, args: list, context: dict) -> Any:
        return args[0] if args else target


def _register_tool(fn: Any) -> Any:
    """Register a function as an MCP tool when the SDK is available."""
    if _mcp_server is not None:
        _mcp_server.tool()(fn)
    return fn


def _register_resource(uri: str):
    """Register a function as an MCP resource when the SDK is available."""
    def decorator(fn: Any) -> Any:
        if _mcp_server is not None:
            _mcp_server.resource(uri)(fn)
        return fn
    return decorator


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@_register_tool
def ainl_validate(code: str, strict: bool = True) -> dict:
    """Validate AINL source code without executing it.

    Returns whether the code compiles successfully, along with any errors
    or warnings.  No side effects.
    """
    ir = _compile(code, strict=strict)
    errors = ir.get("errors") or []
    warnings = ir.get("warnings") or []
    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings}


@_register_tool
def ainl_compile(code: str, strict: bool = True) -> dict:
    """Compile AINL source code to canonical graph IR.

    Returns the full IR JSON on success.  No execution, no side effects.
    """
    ir = _compile(code, strict=strict)
    errors = ir.get("errors") or []
    if errors:
        return {"ok": False, "errors": errors}
    return {"ok": True, "ir": ir}


@_register_tool
def ainl_capabilities() -> dict:
    """Discover runtime adapter capabilities, privilege tiers, and metadata.

    Returns available adapters with their verbs, support tiers, effect
    defaults, recommended lanes, and privilege tiers.  No side effects.
    """
    return _load_capabilities()


@_register_tool
def ainl_security_report(code: str) -> dict:
    """Generate a security/privilege map for an AINL workflow.

    Shows which adapters, verbs, and privilege tiers the workflow uses,
    broken down per label and in aggregate.  No execution, no side effects.
    """
    ir = _compile(code, strict=False)
    errors = ir.get("errors") or []
    if errors:
        return {"ok": False, "errors": errors}
    report = analyze_ir(ir)
    return {"ok": True, "report": report}


@_register_tool
def ainl_run(
    code: str,
    strict: bool = True,
    policy: Optional[dict] = None,
    limits: Optional[dict] = None,
    frame: Optional[dict] = None,
    label: Optional[str] = None,
) -> dict:
    """Compile, validate policy, and execute an AINL workflow.

    By default, only the ``core`` adapter is available and conservative
    resource limits are applied.  The caller may supply additional policy
    restrictions and tighter limits but cannot widen beyond the server
    defaults.

    Returns structured execution output on success or a policy/runtime
    error on failure.
    """
    trace_id = str(uuid.uuid4())

    ir = _compile(code, strict=strict)
    errors = ir.get("errors") or []
    if errors:
        return {"ok": False, "trace_id": trace_id, "errors": errors}

    merged_policy = _merge_policy(policy)
    policy_result = validate_ir_against_policy(ir, merged_policy)
    if not policy_result["ok"]:
        return {
            "ok": False,
            "trace_id": trace_id,
            "error": "policy_violation",
            "policy_errors": policy_result["errors"],
        }

    merged_limits = _merge_limits(limits)
    reg = AdapterRegistry(allowed=list(_DEFAULT_ALLOWED_ADAPTERS))
    reg.register("core", _EchoAdapter())

    try:
        eng = RuntimeEngine(
            ir=ir,
            adapters=reg,
            trace=False,
            step_fallback=True,
            execution_mode="graph-preferred",
            limits=merged_limits,
        )
        entry = label or eng.default_entry_label()
        out = eng.run_label(entry, frame=frame or {})
    except AinlRuntimeError as e:
        return {
            "ok": False,
            "trace_id": trace_id,
            "error": str(e),
            "error_structured": e.to_dict(),
        }
    except Exception as e:
        return {"ok": False, "trace_id": trace_id, "error": str(e)}

    return {
        "ok": True,
        "trace_id": trace_id,
        "label": entry,
        "out": out,
        "runtime_version": RUNTIME_VERSION,
        "ir_version": ir.get("ir_version"),
    }


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------

@_register_resource("ainl://adapter-manifest")
def adapter_manifest_resource() -> str:
    """Full adapter metadata including verbs, tiers, effects, and privilege levels."""
    return json.dumps(_load_json("adapter_manifest.json"), indent=2)


@_register_resource("ainl://security-profiles")
def security_profiles_resource() -> str:
    """Named security profiles for common deployment scenarios."""
    return json.dumps(_load_json("security_profiles.json"), indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if _mcp_server is None:
        raise SystemExit(
            "MCP SDK not installed. Install with: pip install -e '.[mcp]'"
        )
    _mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()
