"""Executor bridge request schema helper (schemas/executor_bridge_validate.py)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from schemas.executor_bridge_validate import (  # noqa: E402
    BridgeEnvelopeError,
    validate_executor_bridge_request,
)


def test_validate_accepts_promoter_search_envelope():
    raw = '{"run_id":"ainl-x-promoter","step_id":"_poll","executor":"x.search","payload":{"query":"@x"},"timeout_s":120}'
    body = json.loads(raw)
    assert validate_executor_bridge_request(body) is body


def test_validate_rejects_missing_executor():
    with pytest.raises(BridgeEnvelopeError, match="executor"):
        validate_executor_bridge_request({"payload": {}})


def test_validate_rejects_bad_payload_type():
    with pytest.raises(BridgeEnvelopeError, match="payload"):
        validate_executor_bridge_request({"executor": "x", "payload": []})


def test_schema_file_exists():
    p = ROOT / "schemas" / "executor_bridge_request.schema.json"
    assert p.is_file()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("required") == ["executor"]
