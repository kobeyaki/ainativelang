#!/usr/bin/env python3
"""
Build a compact trends view from evaluation report JSON files.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


BASE = Path(__file__).resolve().parents[1]
DEFAULT_DIR = BASE / "corpus" / "curated"
DEFAULT_OUT = DEFAULT_DIR / "model_eval_trends.json"


def _safe_get(d: Dict[str, Any], *keys, default=None):
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


def _load_report(path: Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _row(path: Path, rep: Dict[str, Any]) -> Dict[str, Any]:
    lora = _safe_get(rep, "summary", "lora", default={}) or {}
    base = _safe_get(rep, "summary", "base", default={}) or {}
    ff = _safe_get(rep, "summary", "failure_families", default={}) or {}
    lora_diag = _safe_get(rep, "diagnostics", "lora", default={}) or {}
    lora_health = lora_diag.get("constraint_health") or {}
    lora_buckets = lora_diag.get("length_buckets") or {}
    worst_strict_bucket = None
    slowest_bucket = None
    if isinstance(lora_buckets, dict) and lora_buckets:
        items = list(lora_buckets.items())
        worst_strict_bucket = min(
            items,
            key=lambda kv: float((kv[1] or {}).get("strict_ainl_rate", 0.0)),
        )[0]
        slowest_bucket = max(
            items,
            key=lambda kv: float(((kv[1] or {}).get("timing_totals") or {}).get("prompt_total_seconds", 0.0)),
        )[0]
    return {
        "report_file": str(path),
        "report_name": path.name,
        "modified_epoch": path.stat().st_mtime,
        "adapter_path": rep.get("adapter_path"),
        "prompt_set": rep.get("prompt_set"),
        "max_new_tokens": rep.get("max_new_tokens"),
        "constrained_decoding": bool(rep.get("constrained_decoding")),
        "quantization_mode": rep.get("quantization_mode"),
        "repair_attempts": int(rep.get("repair_attempts", 0)),
        "lora": {
            "strict_ainl_rate": float(lora.get("strict_ainl_rate", 0.0)),
            "runtime_compile_rate": float(lora.get("runtime_compile_rate", 0.0)),
            "nonempty_rate": float(lora.get("nonempty_rate", 0.0)),
        },
        "base": {
            "strict_ainl_rate": float(base.get("strict_ainl_rate", 0.0)),
            "runtime_compile_rate": float(base.get("runtime_compile_rate", 0.0)),
            "nonempty_rate": float(base.get("nonempty_rate", 0.0)),
        } if base else None,
        "failure_families_lora": ff.get("lora"),
        "constraint_alerts_lora": lora_health.get("alerts", []),
        "constraint_ratios_lora": lora_health.get("ratios", {}),
        "quantization_lora": lora_diag.get("quantization"),
        "length_bucket_count_lora": len(lora_buckets) if isinstance(lora_buckets, dict) else 0,
        "worst_strict_bucket_lora": worst_strict_bucket,
        "slowest_bucket_lora": slowest_bucket,
    }


def _delta(new: Dict[str, Any], old: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for key in ("strict_ainl_rate", "runtime_compile_rate", "nonempty_rate"):
        out[f"lora_{key}_delta"] = float(new["lora"].get(key, 0.0)) - float(old["lora"].get(key, 0.0))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze trends across model eval reports.")
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--glob", default="model_eval_report*.json")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--latest-n", type=int, default=25)
    parser.add_argument("--min-lora-strict-ainl-rate", type=float, default=0.55)
    parser.add_argument("--min-lora-runtime-rate", type=float, default=0.70)
    parser.add_argument("--min-lora-nonempty-rate", type=float, default=0.60)
    parser.add_argument(
        "--max-regression-strict",
        type=float,
        default=0.05,
        help="Maximum allowed strict_ainl_rate drop vs previous run.",
    )
    parser.add_argument(
        "--max-regression-runtime",
        type=float,
        default=0.05,
        help="Maximum allowed runtime_compile_rate drop vs previous run.",
    )
    parser.add_argument(
        "--max-regression-nonempty",
        type=float,
        default=0.05,
        help="Maximum allowed nonempty_rate drop vs previous run.",
    )
    parser.add_argument(
        "--enforce-gate",
        action="store_true",
        help="Exit non-zero when quality gate fails.",
    )
    args = parser.parse_args()

    files = sorted(args.reports_dir.glob(args.glob), key=lambda p: p.stat().st_mtime)
    if not files:
        raise SystemExit(f"No reports found in {args.reports_dir} with glob {args.glob}")

    rows: List[Dict[str, Any]] = []
    for p in files:
        try:
            rows.append(_row(p, _load_report(p)))
        except Exception:
            continue
    if not rows:
        raise SystemExit("No parseable report files found.")

    latest_rows = rows[-max(1, args.latest_n) :]
    latest = latest_rows[-1]
    previous = latest_rows[-2] if len(latest_rows) > 1 else None
    summary = {
        "total_reports_seen": len(rows),
        "latest_report": latest["report_name"],
        "latest_lora": latest["lora"],
        "previous_report": previous["report_name"] if previous else None,
        "delta_vs_previous": _delta(latest, previous) if previous else None,
    }

    gate_failures: List[str] = []
    latest_lora = latest["lora"]
    if float(latest_lora.get("strict_ainl_rate", 0.0)) < args.min_lora_strict_ainl_rate:
        gate_failures.append(
            f"strict_ainl_rate_below_min:{latest_lora.get('strict_ainl_rate'):.4f}<"
            f"{args.min_lora_strict_ainl_rate:.4f}"
        )
    if float(latest_lora.get("runtime_compile_rate", 0.0)) < args.min_lora_runtime_rate:
        gate_failures.append(
            f"runtime_compile_rate_below_min:{latest_lora.get('runtime_compile_rate'):.4f}<"
            f"{args.min_lora_runtime_rate:.4f}"
        )
    if float(latest_lora.get("nonempty_rate", 0.0)) < args.min_lora_nonempty_rate:
        gate_failures.append(
            f"nonempty_rate_below_min:{latest_lora.get('nonempty_rate'):.4f}<"
            f"{args.min_lora_nonempty_rate:.4f}"
        )
    if previous is not None:
        d = _delta(latest, previous)
        if float(d.get("lora_strict_ainl_rate_delta", 0.0)) < -args.max_regression_strict:
            gate_failures.append(
                f"strict_ainl_rate_regressed:{d.get('lora_strict_ainl_rate_delta'):.4f}<-{args.max_regression_strict:.4f}"
            )
        if float(d.get("lora_runtime_compile_rate_delta", 0.0)) < -args.max_regression_runtime:
            gate_failures.append(
                f"runtime_compile_rate_regressed:{d.get('lora_runtime_compile_rate_delta'):.4f}<-{args.max_regression_runtime:.4f}"
            )
        if float(d.get("lora_nonempty_rate_delta", 0.0)) < -args.max_regression_nonempty:
            gate_failures.append(
                f"nonempty_rate_regressed:{d.get('lora_nonempty_rate_delta'):.4f}<-{args.max_regression_nonempty:.4f}"
            )
    gate = {
        "passed": len(gate_failures) == 0,
        "failures": gate_failures,
        "thresholds": {
            "min_lora_strict_ainl_rate": args.min_lora_strict_ainl_rate,
            "min_lora_runtime_rate": args.min_lora_runtime_rate,
            "min_lora_nonempty_rate": args.min_lora_nonempty_rate,
            "max_regression_strict": args.max_regression_strict,
            "max_regression_runtime": args.max_regression_runtime,
            "max_regression_nonempty": args.max_regression_nonempty,
        },
    }
    summary["gate"] = gate

    out = {
        "summary": summary,
        "latest_rows": latest_rows,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Trend report written: {args.output_json}")
    print(f"Latest report: {summary['latest_report']}")
    print(f"Gate passed: {gate['passed']}")
    if gate_failures:
        print("Gate failures:")
        for f in gate_failures:
            print(f"- {f}")
    if args.enforce_gate and not gate["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
