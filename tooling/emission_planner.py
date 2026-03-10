"""Capability-driven emission planning for benchmarking and emit workflows.

Planning precedence:
1) Compiler-emitted target plan (`ir["required_emit_targets"]`)
2) Compiler-emitted capability markers (`ir["emit_capabilities"]`)
3) IR-structural fallback for legacy IRs
4) Narrow source-text fallback (temporary legacy support)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


TARGET_ORDER = ["react_ts", "python_api", "prisma", "mt5", "scraper", "cron"]


def load_benchmark_manifest(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_artifact_capabilities(source_text: str, ir: Dict) -> Dict[str, bool]:
    emit_caps = ir.get("emit_capabilities")
    if isinstance(emit_caps, dict):
        return {
            "needs_react_ts": bool(emit_caps.get("needs_react_ts")),
            "needs_python_api": bool(emit_caps.get("needs_python_api")),
            "needs_prisma": bool(emit_caps.get("needs_prisma")),
            "needs_mt5": bool(emit_caps.get("needs_mt5")),
            "needs_scraper": bool(emit_caps.get("needs_scraper")),
            "needs_cron": bool(emit_caps.get("needs_cron")),
        }

    services = ir.get("services", {}) or {}
    service_modes = {
        k: (v or {}).get("mode")
        for k, v in services.items()
        if isinstance(v, dict)
    }
    lowered = source_text.lower()
    has_core_web = "core" in services and service_modes.get("core") == "web"
    has_types = bool(ir.get("types"))
    has_cron = bool(ir.get("crons")) or service_modes.get("core") == "cron"
    has_scraper = bool(((services.get("scrape") or {}).get("defs") or {}))
    has_mt5 = bool("mt5" in services)
    has_rag = bool(ir.get("rag")) and any(bool(v) for v in (ir.get("rag") or {}).values())
    has_labels = any(lid != "_anon" for lid in (ir.get("labels") or {}).keys())
    # Narrow legacy fallback for older IRs lacking explicit scrape/mt5 metadata.
    if not has_mt5:
        has_mt5 = ("mt5" in lowered or "trader" in lowered or "trade" in lowered)
    if not has_scraper:
        has_scraper = (
        "scrape" in lowered
        or "scraper" in lowered
        or "crawl" in lowered
        or "\nsc " in f"\n{lowered}"
    )
    return {
        "needs_react_ts": bool(services.get("fe")),
        "needs_python_api": bool(has_core_web or has_rag or (has_labels and not (has_scraper or has_mt5 or has_cron))),
        "needs_prisma": has_types,
        "needs_mt5": has_mt5,
        "needs_scraper": has_scraper,
        "needs_cron": has_cron,
    }


def _matches_rule(cap: Dict[str, bool], cfg: Dict) -> bool:
    include = True
    requires_capability = cfg.get("requires_capability")
    if requires_capability:
        include = include and cap.get(requires_capability, False)
    if requires_capability and len(cfg.keys()) == 1:
        return include
    req_services = cfg.get("requires_any_service", [])
    if req_services:
        # service-presence rules represented by capability flags
        include = include and any(
            cap.get(f"has_{svc}", False)
            for svc in req_services
        )
    if cfg.get("requires_core_web"):
        include = include and cap.get("needs_python_api", False)
    if cfg.get("requires_types"):
        include = include and cap.get("needs_prisma", False)
    if cfg.get("requires_cron"):
        include = include and cap.get("needs_cron", False)
    if cfg.get("requires_mt5"):
        include = include and cap.get("needs_mt5", False)
    if cfg.get("requires_scraper"):
        include = include and cap.get("needs_scraper", False)
    return include


def required_emit_targets(
    source_text: str,
    ir: Dict,
    *,
    mode: str,
    benchmark_manifest: Dict,
) -> List[str]:
    if mode == "full_multitarget":
        return list(TARGET_ORDER)
    if mode != "minimal_emit":
        raise ValueError(f"unsupported emission planning mode: {mode}")

    required = ir.get("required_emit_targets")
    if isinstance(required, dict):
        planned = required.get("minimal_emit")
        if isinstance(planned, list):
            out = [t for t in planned if t in TARGET_ORDER]
            if out:
                return out

    cap = infer_artifact_capabilities(source_text, ir)
    mode_cfg = benchmark_manifest.get("modes", {}).get("minimal_emit", {})
    rules = mode_cfg.get("relevance_rules", {})
    included: List[str] = []
    for target in TARGET_ORDER:
        cfg = rules.get(target, {})
        if _matches_rule(cap, cfg):
            included.append(target)
    if included:
        return included
    fallback = [t for t in mode_cfg.get("fallback_targets", []) if t in TARGET_ORDER]
    return fallback or ["python_api"]


def excluded_emit_targets(
    source_text: str,
    ir: Dict,
    *,
    mode: str,
    benchmark_manifest: Dict,
) -> List[str]:
    included = required_emit_targets(
        source_text,
        ir,
        mode=mode,
        benchmark_manifest=benchmark_manifest,
    )
    return [t for t in TARGET_ORDER if t not in included]
