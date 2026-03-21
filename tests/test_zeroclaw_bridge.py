"""Tests for zeroclaw/bridge (mocked zeroclaw CLI)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_zeroclaw_cron_list_json_mocked() -> None:
    from zeroclaw.bridge.zeroclaw_cron_adapter import list_cron_jobs_json

    fake_out = json.dumps({"jobs": [{"name": "j1", "payload": {"message": "run_wrapper_ainl"}}]})
    proc = MagicMock()
    proc.returncode = 0
    proc.stdout = fake_out
    proc.stderr = ""
    with patch("zeroclaw.bridge.zeroclaw_cron_adapter.subprocess.run", return_value=proc):
        jobs, err = list_cron_jobs_json()
    assert err is None
    assert jobs is not None
    assert jobs[0]["name"] == "j1"


def test_zeroclaw_memory_append_today_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZEROCLAW_WORKSPACE", str(tmp_path / "zc"))
    from zeroclaw.bridge.zeroclaw_memory_adapter import ZeroclawMemoryAdapter

    ad = ZeroclawMemoryAdapter()
    n = ad.call("append_today", ["hello"], {"dry_run": True})
    assert n == 1
    mem = tmp_path / "zc" / "memory"
    assert not mem.exists() or not any(mem.glob("*.md"))


def test_zeroclaw_queue_put_dry_run() -> None:
    from zeroclaw.bridge.zeroclaw_queue_adapter import ZeroclawQueueAdapter

    ad = ZeroclawQueueAdapter()
    r = ad.call("Put", ["notify", "ping"], {"dry_run": True})
    assert r == "dry_run"


def test_zeroclaw_bridge_main_help_exits_zero() -> None:
    bridge_main = REPO_ROOT / "zeroclaw" / "bridge" / "zeroclaw_bridge_main.py"
    with patch.object(sys, "argv", [str(bridge_main), "--help"]):
        with pytest.raises(SystemExit) as ei:
            import runpy

            runpy.run_path(str(bridge_main), run_name="__main__")
        assert ei.value.code == 0


def test_cron_drift_report_json_mocked_zeroclaw(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    reg_path = tmp_path / "cron_registry.json"
    reg_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "meta": {"untracked_payload_substrings": []},
                "jobs": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("CRON_REGISTRY_PATH", str(reg_path))

    jobs = [{"name": "x", "payload": {"message": "nope"}}]
    with patch(
        "zeroclaw.bridge.cron_drift_check.list_cron_jobs_json",
        return_value=(jobs, None),
    ):
        from zeroclaw.bridge.cron_drift_check import run_report

        report = run_report()

    assert report.get("zeroclaw_bin")
    assert report.get("ok") is True
