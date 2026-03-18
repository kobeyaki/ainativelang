from __future__ import annotations

from typing import Any, Dict, Optional


def summarize_run_result(
    result: Dict[str, Any],
    *,
    task_id: Optional[str] = None,
    review_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a small, host-friendly summary envelope around a single AINL run result.

    This is intended for environments like Claude Cowork / Dispatch, Dispatch-style
    batch runners, and MCP hosts that want a compact, stable surface for logging
    and review. It is an additive helper: it does not change the underlying
    compiler/runtime semantics or result schema.

    The input ``result`` is expected to be the structured payload returned by
    either:

    - the MCP ``ainl_run`` tool (see ``scripts/ainl_mcp_server.py``), or
    - the HTTP runner service ``/run`` endpoint
      (see ``scripts/runtime_runner_service.py``).
    """

    ok = bool(result.get("ok"))
    trace_id = result.get("trace_id")

    # Classify status in a small, host-oriented enum.
    if ok:
        status = "ok"
    elif result.get("error") == "policy_violation" or result.get("policy_errors"):
        status = "policy_violation"
    elif result.get("errors"):
        # Validation/compile errors before execution.
        status = "validation_error"
    else:
        status = "runtime_error"

    # Short, human-readable summary. Hosts remain free to override or extend.
    if status == "ok":
        label = result.get("label")
        summary = "AINL run ok"
        if label:
            summary += f" (entry label={label})"
    elif status == "policy_violation":
        errors = result.get("policy_errors") or []
        summary = f"AINL policy violation ({len(errors)} error(s))"
    elif status == "validation_error":
        errors = result.get("errors") or []
        summary = f"AINL validation error ({len(errors)} issue(s))"
    else:
        err = str(result.get("error") or "runtime error")
        summary = f"AINL runtime error: {err}"

    return {
        "task_id": task_id,
        "status": status,
        "summary": summary,
        "result": result,
        "trace_id": trace_id,
        "policy_errors": result.get("policy_errors") or [],
        "artifacts": [],
        "review_hint": review_hint,
    }

