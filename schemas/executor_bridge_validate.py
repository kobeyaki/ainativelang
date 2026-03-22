"""Validate executor-bridge request bodies (matches executor_bridge_request.schema.json)."""

from __future__ import annotations

from typing import Any, Dict


class BridgeEnvelopeError(ValueError):
    """Raised when a body does not satisfy the bridge request contract."""


def validate_executor_bridge_request(body: Any) -> Dict[str, Any]:
    """
    Ensure `body` is a dict with required `executor` and well-typed optional fields.
    Returns the same dict for convenience.
    """
    if not isinstance(body, dict):
        raise BridgeEnvelopeError("bridge request must be a JSON object")
    ex = body.get("executor")
    if not isinstance(ex, str) or not ex.strip():
        raise BridgeEnvelopeError("bridge request requires non-empty string field 'executor'")
    pl = body.get("payload")
    if pl is None:
        pl = {}
    elif not isinstance(pl, dict):
        raise BridgeEnvelopeError("bridge request field 'payload' must be an object when present")
    for key in ("run_id", "step_id"):
        val = body.get(key)
        if val is not None and not isinstance(val, str):
            raise BridgeEnvelopeError(f"bridge request field {key!r} must be a string when present")
    ts = body.get("timeout_s")
    if ts is not None:
        if isinstance(ts, bool) or not isinstance(ts, (int, float)):
            raise BridgeEnvelopeError("bridge request field 'timeout_s' must be a number when present")
        if isinstance(ts, float) and not ts.is_integer():
            raise BridgeEnvelopeError("bridge request field 'timeout_s' must be a whole number when present")
        ti = int(ts)
        if ti < 1:
            raise BridgeEnvelopeError("bridge request field 'timeout_s' must be a positive integer when present")
    return body
