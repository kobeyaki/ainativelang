"""Helpers for ZeroClaw cron CLI (list JSON). Used by ``cron_drift_check.py`` in this directory."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple


def zeroclaw_bin() -> str:
    env = (os.environ.get("ZEROCLAW_BIN") or "").strip()
    if env:
        return env
    found = shutil.which("zeroclaw")
    return found if found else "zeroclaw"


def list_cron_jobs_json(timeout_s: float = 60.0) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """Run ``zeroclaw cron list --json``; return (jobs, error_message)."""
    bin_path = zeroclaw_bin()
    try:
        proc = subprocess.run(
            [bin_path, "cron", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except FileNotFoundError:
        return None, "zeroclaw binary not found"
    except subprocess.TimeoutExpired:
        return None, "zeroclaw cron list timed out"
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout or "zeroclaw cron list failed")[:500]
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return None, f"invalid JSON from zeroclaw: {e}"
    jobs = data.get("jobs")
    if not isinstance(jobs, list):
        return None, "zeroclaw JSON missing jobs[]"
    return jobs, None


def job_message(job: Dict[str, Any]) -> str:
    payload = job.get("payload") or {}
    if isinstance(payload, dict):
        msg = payload.get("message") or payload.get("text") or ""
        return str(msg)
    return ""


def job_cron_expr(job: Dict[str, Any]) -> str:
    sched = job.get("schedule") or {}
    if isinstance(sched, dict) and str(sched.get("kind") or "").lower() == "cron":
        return str(sched.get("expr") or "")
    return ""


def find_job_by_payload(jobs: List[Dict[str, Any]], payload_contains: str) -> Optional[Dict[str, Any]]:
    needle = payload_contains.strip()
    if not needle:
        return None
    for j in jobs:
        if needle in job_message(j):
            return j
    return None
