import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.engine import RuntimeEngine


FIX_DIR = Path(__file__).resolve().parent / "conformance_runtime" / "fixtures"


def _fixture_paths():
    return sorted(FIX_DIR.glob("*.json"))


@pytest.mark.parametrize("fixture_path", _fixture_paths(), ids=lambda p: p.stem)
def test_runtime_conformance_fixture(fixture_path: Path):
    fx = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload = RuntimeEngine.run(
        fx["code"],
        frame=fx.get("input_frame", {}),
        trace=True,
        strict=bool(fx.get("strict", True)),
        execution_mode="graph-preferred",
    )
    assert payload["ok"] is True
    if "expected_result" in fx:
        assert payload["result"] == fx["expected_result"]
    if "expected_result_contains" in fx:
        assert fx["expected_result_contains"] in str(payload["result"])
    trace_ops = [e.get("op") for e in payload.get("trace", [])]
    if "expected_trace_ops" in fx:
        assert trace_ops == fx["expected_trace_ops"]
    if "expected_trace_ops_contains" in fx:
        for op in fx["expected_trace_ops_contains"]:
            assert op in trace_ops
