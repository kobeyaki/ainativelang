"""
Tests for tooling/trace_focus.py (execution-pointer helper).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tooling.trace_focus import trace_to_focus


def test_trace_to_focus_prefers_node_id():
    traces = [
        {"label": "L1", "op": "R", "step": 0, "lineno": 1},
        {"label": "L1", "op": "J", "step": 1, "lineno": 2, "node_id": "n2"},
    ]
    label, focus, lineno = trace_to_focus(traces)
    assert label == "L1"
    assert focus == "n2"
    assert lineno == 2


def test_trace_to_focus_falls_back_to_step():
    traces = [
        {"label": "L9", "op": "R", "step": 3, "lineno": 10},
    ]
    label, focus, lineno = trace_to_focus(traces)
    assert label == "L9"
    assert focus == 3
    assert lineno == 10


def test_trace_to_focus_empty():
    label, focus, lineno = trace_to_focus([])
    assert label is None and focus is None and lineno is None

