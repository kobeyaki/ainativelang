import json
import os
import tempfile

from adapters.extras import ExtrasAdapter
from runtime.adapters.base import AdapterError


def _with_summary_root(tmpdir: str):
  os.environ["AINL_SUMMARY_ROOT"] = tmpdir


def test_extras_metrics_reads_summary_and_derives_ok_ratio():
  adapter = ExtrasAdapter()

  summary = {
      "run_count": 10,
      "ok_count": 7,
      "error_count": 3,
      "runtime_versions": ["1.0.0", "1.1.0"],
      "result_kinds": {"dict": 10},
      "trace_op_counts": {"R": 20, "J": 10},
      "label_counts": {"1": 5, "2": 5},
      "timestamps_present": False,
  }

  with tempfile.TemporaryDirectory() as tmpdir:
    _with_summary_root(tmpdir)
    # metrics arg is a path *relative* to AINL_SUMMARY_ROOT
    rel_path = "summary.json"
    abs_path = os.path.join(tmpdir, rel_path)
    with open(abs_path, "w", encoding="utf-8") as f:
      json.dump(summary, f)

    result = adapter.call("metrics", [rel_path], context={})

  assert result["run_count"] == 10
  assert result["ok_count"] == 7
  assert result["error_count"] == 3
  assert result["ok_ratio"] == 0.7
  assert result["runtime_versions"] == ["1.0.0", "1.1.0"]
  assert result["result_kinds"] == {"dict": 10}
  assert result["trace_op_counts"] == {"R": 20, "J": 10}
  assert result["label_counts"] == {"1": 5, "2": 5}
  assert result["timestamps_present"] is False


def test_extras_metrics_raises_on_missing_file():
  adapter = ExtrasAdapter()
  with tempfile.TemporaryDirectory() as tmpdir:
    _with_summary_root(tmpdir)
    missing_rel = "missing.json"
    try:
      adapter.call("metrics", [missing_rel], context={})
    except AdapterError as e:
      assert "metrics failed to read" in str(e)
    else:
      raise AssertionError("expected AdapterError for missing summary file")


def test_extras_metrics_raises_on_invalid_json():
  adapter = ExtrasAdapter()
  with tempfile.TemporaryDirectory() as tmpdir:
    _with_summary_root(tmpdir)
    rel_path = "bad.json"
    abs_path = os.path.join(tmpdir, rel_path)
    with open(abs_path, "w", encoding="utf-8") as f:
      f.write("{not valid json")

    try:
      adapter.call("metrics", [rel_path], context={})
    except AdapterError as e:
      assert "metrics failed to read" in str(e)
    else:
      raise AssertionError("expected AdapterError for invalid json")


def test_extras_metrics_raises_on_non_object_summary():
  adapter = ExtrasAdapter()
  with tempfile.TemporaryDirectory() as tmpdir:
    _with_summary_root(tmpdir)
    rel_path = "list.json"
    abs_path = os.path.join(tmpdir, rel_path)
    with open(abs_path, "w", encoding="utf-8") as f:
      json.dump([{"run_count": 1}], f)

    try:
      adapter.call("metrics", [rel_path], context={})
    except AdapterError as e:
      assert "metrics expects JSON object summary" in str(e)
    else:
      raise AssertionError("expected AdapterError for non-object summary")
