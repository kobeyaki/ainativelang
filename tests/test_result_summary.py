from __future__ import annotations

from tooling.result_summary import summarize_run_result


def test_summarize_run_result_ok():
    raw = {
        "ok": True,
        "trace_id": "t-1",
        "label": "L1",
        "out": {"x": 5},
        "runtime_version": "1.0.0",
        "ir_version": "1.0.0",
    }

    wrapped = summarize_run_result(raw, task_id="task-1")

    assert wrapped["task_id"] == "task-1"
    assert wrapped["status"] == "ok"
    assert "AINL run ok" in wrapped["summary"]
    assert wrapped["trace_id"] == "t-1"
    assert wrapped["result"] is raw
    assert wrapped["policy_errors"] == []
    assert isinstance(wrapped["artifacts"], list)


def test_summarize_run_result_policy_violation():
    raw = {
        "ok": False,
        "trace_id": "t-2",
        "error": "policy_violation",
        "policy_errors": [{"code": "DENY_ADAPTER", "message": "adapter not allowed"}],
    }

    wrapped = summarize_run_result(raw)

    assert wrapped["status"] == "policy_violation"
    assert "policy violation" in wrapped["summary"]
    assert wrapped["policy_errors"] == raw["policy_errors"]


def test_summarize_run_result_validation_error():
    raw = {
        "ok": False,
        "trace_id": "t-3",
        "errors": [{"message": "syntax error"}],
    }

    wrapped = summarize_run_result(raw)

    assert wrapped["status"] == "validation_error"
    assert "validation error" in wrapped["summary"]
    assert wrapped["policy_errors"] == []


def test_summarize_run_result_runtime_error():
    raw = {
        "ok": False,
        "trace_id": "t-4",
        "error": "division by zero",
    }

    wrapped = summarize_run_result(raw, review_hint="check adapter inputs")

    assert wrapped["status"] == "runtime_error"
    assert "runtime error" in wrapped["summary"]
    assert "division by zero" in wrapped["summary"]
    assert wrapped["review_hint"] == "check adapter inputs"


def test_summarize_run_result_runner_style_ok():
    # Typical HTTP runner `/run` success payload (no policy errors, has label/out).
    raw = {
        "ok": True,
        "trace_id": "runner-1",
        "replay_artifact_id": "artifact-123",
        "label": "L_main",
        "out": {"status": "ok"},
    }

    wrapped = summarize_run_result(raw)

    assert wrapped["status"] == "ok"
    assert wrapped["trace_id"] == "runner-1"
    assert wrapped["result"] is raw
