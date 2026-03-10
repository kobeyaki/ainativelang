import json
import os
import tempfile
from pathlib import Path

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.summarize_runs import _iter_runs_from_file, _summarize_runs  # type: ignore


def _make_run_payload(
    *,
    ok: bool,
    label: str,
    result,
    runtime_version: str,
    trace_ops,
) -> dict:
    trace = []
    for idx, op in enumerate(trace_ops):
        # allow None to represent missing op in some traces
        if op is None:
            trace.append({"label": label, "step": idx})
        else:
            trace.append({"label": label, "op": op, "step": idx})
    return {
        "ok": ok,
        "label": label,
        "result": result,
        "runtime_version": runtime_version,
        "trace": trace,
    }


def test_summarize_single_run_payload():
    payload = _make_run_payload(
        ok=True,
        label="1",
        result=5,
        runtime_version="1.0.0",
        trace_ops=["R", "J"],
    )

    summary = _summarize_runs([payload])

    assert summary["run_count"] == 1
    assert summary["ok_count"] == 1
    assert summary["error_count"] == 0
    assert summary["runtime_versions"] == ["1.0.0"]
    assert summary["result_kinds"] == {"int": 1}
    assert summary["trace_op_counts"] == {"R": 1, "J": 1}
    assert summary["label_counts"] == {"1": 2}
    # No wall-clock timestamps in the payloads we summarize today.
    assert summary["timestamps_present"] is False


def test_summarize_multiple_runs_mixed_ok():
    p1 = _make_run_payload(
        ok=True,
        label="1",
        result="ok-result",
        runtime_version="1.0.0",
        trace_ops=["R", "J"],
    )
    p2 = _make_run_payload(
        ok=False,
        label="2",
        result={"error": "x"},
        runtime_version="2.0.0",
        trace_ops=["R", "Err"],
    )

    summary = _summarize_runs([p1, p2])

    assert summary["run_count"] == 2
    assert summary["ok_count"] == 1
    assert summary["error_count"] == 1
    assert summary["runtime_versions"] == ["1.0.0", "2.0.0"]
    # One str result, one dict result.
    assert summary["result_kinds"] == {"str": 1, "dict": 1}
    # Ops aggregated across both runs.
    assert summary["trace_op_counts"] == {"R": 2, "J": 1, "Err": 1}
    # Label 1 appears twice, label 2 appears twice.
    assert summary["label_counts"] == {"1": 2, "2": 2}


def test_iter_runs_from_file_supports_list_of_payloads():
    p1 = _make_run_payload(
        ok=True,
        label="1",
        result=1,
        runtime_version="1.0.0",
        trace_ops=["R"],
    )
    p2 = _make_run_payload(
        ok=False,
        label="2",
        result=2,
        runtime_version="1.0.0",
        trace_ops=["J"],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "runs.json"
        path.write_text(json.dumps([p1, p2]), encoding="utf-8")

        runs = list(_iter_runs_from_file(path))
        assert runs == [p1, p2]

        summary = _summarize_runs(runs)
        assert summary["run_count"] == 2
        assert summary["ok_count"] == 1
        assert summary["error_count"] == 1
        assert summary["runtime_versions"] == ["1.0.0"]
        assert summary["result_kinds"] == {"int": 2}
        assert summary["trace_op_counts"] == {"R": 1, "J": 1}
        assert summary["label_counts"] == {"1": 1, "2": 1}

