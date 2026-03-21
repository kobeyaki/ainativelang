#!/usr/bin/env python3
"""
Compare canonical cron intent (tooling/cron_registry.json) with:
  - compiled AINL schedules (IR ``crons`` from each ainl_program)
  - ZeroClaw cron jobs (``zeroclaw cron list --json``), matched via ``openclaw_match.payload_contains``

Uses the same registry fingerprints as OpenClaw drift checks so one ``cron_registry.json`` row can
validate either host. Does not modify ZeroClaw or system cron.

Official location: zeroclaw/bridge/

Usage:
  python3 zeroclaw/bridge/cron_drift_check.py
  python3 zeroclaw/bridge/cron_drift_check.py --json

Env:
  ZEROCLAW_BIN — optional; else ``shutil.which("zeroclaw")``
  AINL_REPO_ROOT — repo root (default: parent of zeroclaw/)
  CRON_REGISTRY_PATH — registry JSON path
  CRON_DRIFT_UNTRACKED_SUBSTRINGS — comma-separated override
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zeroclaw.bridge.zeroclaw_cron_adapter import (
    find_job_by_payload,
    job_cron_expr,
    job_message,
    list_cron_jobs_json,
    zeroclaw_bin,
)

_CRON_LINE = re.compile(r'^\s*S\s+core\s+cron\s+"([^"]+)"\s*$', re.MULTILINE)

# zeroclaw/bridge/ -> repo root (AI_Native_Lang)
_BRIDGE_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = _BRIDGE_DIR.parent.parent


def _root() -> Path:
    return Path(os.environ.get("AINL_REPO_ROOT", str(DEFAULT_ROOT))).resolve()


def _registry_path(root: Path) -> Path:
    raw = os.environ.get("CRON_REGISTRY_PATH", "").strip()
    if not raw:
        return root / "tooling" / "cron_registry.json"
    p = Path(raw)
    return p.resolve() if p.is_absolute() else (root / p).resolve()


def _load_registry(root: Path) -> Dict[str, Any]:
    p = _registry_path(root)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _untracked_substrings(reg: Dict[str, Any]) -> List[str]:
    env = (os.environ.get("CRON_DRIFT_UNTRACKED_SUBSTRINGS") or "").strip()
    if env:
        return [s.strip() for s in env.split(",") if s.strip()]
    meta = reg.get("meta") if isinstance(reg.get("meta"), dict) else {}
    raw = meta.get("untracked_payload_substrings")
    if isinstance(raw, list):
        return [str(s).strip() for s in raw if str(s).strip()]
    return []


def _cron_expr_from_schedule_module(root: Path, rel_module: Optional[str]) -> Optional[str]:
    if not rel_module or not isinstance(rel_module, str):
        return None
    path = root / rel_module
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    m = _CRON_LINE.search(text)
    return m.group(1).strip() if m else None


def _compile_crons(root: Path, rel_program: str) -> List[Dict[str, str]]:
    sys.path.insert(0, str(root))
    from compiler_v2 import AICodeCompiler

    path = root / rel_program
    src = path.read_text(encoding="utf-8")
    ir = AICodeCompiler(strict_mode=False, strict_reachability=False).compile(src, emit_graph=True)
    if ir.get("errors"):
        raise RuntimeError(f"compile failed for {rel_program}: {ir.get('errors')}")
    crons = ir.get("crons") or []
    return [c for c in crons if isinstance(c, dict)]


def run_report() -> Dict[str, Any]:
    root = _root()
    reg = _load_registry(root)
    jobs_def = [j for j in reg.get("jobs", []) if isinstance(j, dict)]
    zc_jobs, zc_err = list_cron_jobs_json()

    issues: List[Dict[str, Any]] = []
    rows: List[Dict[str, Any]] = []

    for job in jobs_def:
        jid = str(job.get("id", ""))
        row: Dict[str, Any] = {"id": jid, "human_name": job.get("human_name"), "checks": {}}

        prog = job.get("ainl_program")
        expr_expected = str(job.get("schedule_cron") or "")
        ir_exprs: List[str] = []
        try:
            if isinstance(prog, str):
                crons = _compile_crons(root, prog)
                ir_exprs = [str(c.get("expr") or "") for c in crons]
                row["checks"]["ainl_ir_crons"] = ir_exprs
        except Exception as e:
            issues.append({"job_id": jid, "kind": "ainl_compile_error", "detail": str(e)})
            row["checks"]["ainl_ir_crons"] = None

        mod = job.get("schedule_module")
        module_expr = _cron_expr_from_schedule_module(root, str(mod) if mod else None)
        row["checks"]["schedule_module_expr"] = module_expr

        ainl_authoritative = module_expr or (ir_exprs[0] if ir_exprs else None)
        row["checks"]["ainl_authoritative_schedule"] = ainl_authoritative

        if expr_expected and ainl_authoritative and expr_expected != ainl_authoritative:
            issues.append(
                {
                    "job_id": jid,
                    "kind": "schedule_mismatch_registry_vs_ainl",
                    "registry_schedule_cron": expr_expected,
                    "ainl_schedule": ainl_authoritative,
                    "detail": "Update tooling/cron_registry.json, modules/openclaw/cron_*.ainl, and adapters/openclaw_defaults.py together.",
                }
            )

        match = job.get("openclaw_match") or {}
        payload_contains = str(match.get("payload_contains") or "")
        required = bool(job.get("openclaw_required"))

        if zc_err:
            row["checks"]["zeroclaw"] = {"error": zc_err}
            if required:
                issues.append({"job_id": jid, "kind": "zeroclaw_unavailable", "detail": zc_err})
        else:
            assert zc_jobs is not None
            hit = find_job_by_payload(zc_jobs, payload_contains) if payload_contains else None
            row["checks"]["zeroclaw"] = {
                "matched": hit is not None,
                "zeroclaw_name": (hit or {}).get("name"),
                "zeroclaw_expr": job_cron_expr(hit) if hit else None,
                "zeroclaw_enabled": (hit or {}).get("enabled"),
            }
            if payload_contains and hit is None:
                msg = "No ZeroClaw job whose payload contains the registry fingerprint."
                issues.append(
                    {
                        "job_id": jid,
                        "kind": "zeroclaw_job_missing",
                        "detail": msg,
                        "payload_contains": payload_contains,
                        "severity": "error" if required else "info",
                    }
                )
            if hit is not None and expr_expected:
                zexpr = job_cron_expr(hit)
                if zexpr and zexpr != expr_expected:
                    issues.append(
                        {
                            "job_id": jid,
                            "kind": "schedule_mismatch_zeroclaw_vs_registry",
                            "registry_schedule_cron": expr_expected,
                            "zeroclaw_schedule_expr": zexpr,
                            "detail": "ZeroClaw job exists but cron expression differs from registry/AINL.",
                        }
                    )

        rows.append(row)

    untracked: List[str] = []
    needles = _untracked_substrings(reg)
    if zc_jobs and needles:
        fingerprints: List[str] = []
        for job in jobs_def:
            m = job.get("openclaw_match") or {}
            pc = str(m.get("payload_contains") or "")
            if pc:
                fingerprints.append(pc)
        for j in zc_jobs:
            msg = job_message(j)
            if not any(n in msg for n in needles):
                continue
            if not any(fp in msg for fp in fingerprints if fp):
                name = str(j.get("name") or j.get("id"))
                untracked.append(name)
    if untracked:
        issues.append(
            {
                "kind": "zeroclaw_untracked_ainlish",
                "jobs": untracked,
                "detail": "ZeroClaw job payloads matched untracked_payload_substrings but no registry fingerprint — add a row, clear meta.untracked_payload_substrings, or adjust CRON_DRIFT_UNTRACKED_SUBSTRINGS.",
            }
        )

    serious_kinds = (
        "ainl_compile_error",
        "schedule_mismatch_registry_vs_ainl",
        "schedule_mismatch_zeroclaw_vs_registry",
    )
    serious = [
        i
        for i in issues
        if i.get("kind") in serious_kinds
        or (i.get("kind") == "zeroclaw_job_missing" and i.get("severity") == "error")
    ]
    return {
        "ok": len(serious) == 0,
        "repo_root": str(root),
        "registry_path": str(_registry_path(root)),
        "zeroclaw_bin": zeroclaw_bin(),
        "untracked_substrings_used": needles,
        "registry_schema_version": reg.get("schema_version"),
        "jobs": rows,
        "issues": issues,
    }


def main() -> None:
    as_json = "--json" in sys.argv
    report = run_report()
    strict = os.environ.get("CRON_DRIFT_STRICT", "").strip().lower() in ("1", "true", "yes")

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Cron drift report (repo={report['repo_root']})")
        print(f"Registry: {report.get('registry_path')}")
        print(f"zeroclaw CLI: {report.get('zeroclaw_bin')}")
        print(f"untracked heuristic substrings: {report.get('untracked_substrings_used')!r}")
        print(f"Registry schema: {report.get('registry_schema_version')}")
        print(f"ok (no serious drift): {report.get('ok')}")
        for row in report.get("jobs", []):
            print(f"\n--- {row.get('id')} ({row.get('human_name')}) ---")
            print(json.dumps(row.get("checks"), indent=2))
        if report.get("issues"):
            print("\nIssues:")
            for i in report["issues"]:
                print(f"  - {json.dumps(i)}")
        else:
            print("\nNo issues detected (for defined checks).")

    if strict and not report.get("ok", True):
        sys.exit(1)
    if os.environ.get("CRON_DRIFT_FAIL_ON_UNTRACKED", "").strip().lower() in ("1", "true", "yes"):
        for i in report.get("issues", []):
            if i.get("kind") == "zeroclaw_untracked_ainlish":
                sys.exit(1)


if __name__ == "__main__":
    main()
