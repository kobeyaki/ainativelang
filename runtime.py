"""Compatibility re-exports for historical `runtime.py` imports.

Canonical execution semantics are implemented in `runtime.engine` and exposed via
the compatibility shim `runtime.compat.ExecutionEngine`.
"""

from runtime.compat import ExecutionEngine, _normalize_label_id, _normalize_node_id

__all__ = ["ExecutionEngine", "_normalize_label_id", "_normalize_node_id"]
