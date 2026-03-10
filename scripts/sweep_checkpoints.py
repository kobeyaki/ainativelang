#!/usr/bin/env python3
"""
Evaluate adapter checkpoints and rank them by strict AINL task metrics.

Primary metric:
1) strict_ainl_rate
2) runtime_compile_rate
3) nonempty_rate
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


BASE = Path(__file__).resolve().parents[1]
EVAL_SCRIPT = BASE / "scripts" / "eval_finetuned_model.py"
DEFAULT_PROMPTS = BASE / "corpus" / "curated" / "regression_prompts.jsonl"
DEFAULT_OUT = BASE / "corpus" / "curated" / "checkpoint_sweep_report.json"


def _discover_candidates(adapter_root: Path) -> List[Path]:
    out: List[Path] = []
    # Include final merged/output adapter directory itself when loadable.
    if (adapter_root / "adapter_config.json").exists():
        out.append(adapter_root)
    ckpts = sorted(
        [p for p in adapter_root.glob("checkpoint-*") if p.is_dir()],
        key=lambda p: p.name,
    )
    for p in ckpts:
        if (p / "adapter_config.json").exists():
            out.append(p)
    return out


def _run_eval(args, adapter_path: Path, out_json: Path) -> Dict:
    cmd = [
        sys.executable,
        str(EVAL_SCRIPT),
        "--adapter-path",
        str(adapter_path),
        "--base-model",
        args.base_model,
        "--prompt-set",
        str(args.prompt_set),
        "--output-json",
        str(out_json),
        "--max-new-tokens",
        str(args.max_new_tokens),
        "--device",
        args.device,
        "--heartbeat-seconds",
        str(args.heartbeat_seconds),
        "--generation-timeout-seconds",
        str(args.generation_timeout_seconds),
        "--repair-attempts",
        str(args.repair_attempts),
        "--skip-base-eval",
    ]
    if args.limit > 0:
        cmd.extend(["--limit", str(args.limit)])
    if args.constrained_decoding:
        cmd.append("--constrained-decoding")
    if args.canonicalize_output:
        cmd.append("--canonicalize-output")
    if args.emit_timing:
        cmd.append("--emit-timing")
    if args.constraint_diagnostics:
        cmd.append("--constraint-diagnostics")
    if args.bucket_by_prompt_length:
        cmd.append("--bucket-by-prompt-length")
    if args.canonicalize_chunk_lines > 0:
        cmd.extend(["--canonicalize-chunk-lines", str(args.canonicalize_chunk_lines)])
    if args.canonicalize_max_lines > 0:
        cmd.extend(["--canonicalize-max-lines", str(args.canonicalize_max_lines)])
    cmd.extend(["--quantization-mode", args.quantization_mode])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {
            "ok": False,
            "error": f"eval_failed: exit={proc.returncode}",
            "stderr_tail": "\n".join(proc.stderr.splitlines()[-20:]),
            "stdout_tail": "\n".join(proc.stdout.splitlines()[-20:]),
        }
    try:
        with open(out_json, encoding="utf-8") as f:
            report = json.load(f)
    except Exception as e:
        return {
            "ok": False,
            "error": f"failed_to_read_report: {e}",
            "stderr_tail": "\n".join(proc.stderr.splitlines()[-20:]),
            "stdout_tail": "\n".join(proc.stdout.splitlines()[-20:]),
        }
    return {
        "ok": True,
        "report": report,
        "stderr_tail": "\n".join(proc.stderr.splitlines()[-10:]),
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-10:]),
    }


def _score_key(row: Dict) -> tuple:
    return (
        float(row.get("strict_ainl_rate", 0.0)),
        float(row.get("runtime_compile_rate", 0.0)),
        float(row.get("nonempty_rate", 0.0)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep checkpoints and rank by strict AINL metrics.")
    parser.add_argument("--adapter-root", type=Path, required=True)
    parser.add_argument("--base-model", default="microsoft/phi-3-mini-4k-instruct")
    parser.add_argument("--prompt-set", type=Path, default=DEFAULT_PROMPTS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=40)
    parser.add_argument("--device", choices=["cpu", "mps"], default="mps")
    parser.add_argument("--heartbeat-seconds", type=int, default=5)
    parser.add_argument("--generation-timeout-seconds", type=int, default=180)
    parser.add_argument("--repair-attempts", type=int, default=2)
    parser.add_argument("--constrained-decoding", action="store_true")
    parser.add_argument("--canonicalize-output", action="store_true")
    parser.add_argument("--emit-timing", action="store_true")
    parser.add_argument("--constraint-diagnostics", action="store_true")
    parser.add_argument(
        "--bucket-by-prompt-length",
        action="store_true",
        help="Sort prompts by rendered prompt-token length during eval for stable shapes.",
    )
    parser.add_argument("--canonicalize-chunk-lines", type=int, default=256)
    parser.add_argument("--canonicalize-max-lines", type=int, default=512)
    parser.add_argument(
        "--quantization-mode",
        choices=["none", "dynamic-int8"],
        default="none",
        help="Optional eval quantization mode forwarded to eval script.",
    )
    parser.add_argument(
        "--promote-best-link",
        action="store_true",
        help="Create/replace adapter-root/best_by_strict_ainl symlink to top-1 checkpoint.",
    )
    parser.add_argument(
        "--prune-non-topk",
        action="store_true",
        help="Delete checkpoint-* directories outside the selected top-k set.",
    )
    args = parser.parse_args()

    adapter_root = args.adapter_root
    if not adapter_root.exists():
        raise SystemExit(f"Adapter root not found: {adapter_root}")

    candidates = _discover_candidates(adapter_root)
    if not candidates:
        raise SystemExit(f"No loadable adapter checkpoints found under: {adapter_root}")

    sweep_dir = adapter_root / "checkpoint_eval"
    sweep_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict] = []
    for idx, candidate in enumerate(candidates, start=1):
        tmp_report = sweep_dir / f"{candidate.name}.json"
        print(f"[sweep {idx}/{len(candidates)}] Evaluating {candidate}")
        res = _run_eval(args, candidate, tmp_report)
        if not res.get("ok"):
            rows.append(
                {
                    "adapter_path": str(candidate),
                    "ok": False,
                    "error": res.get("error"),
                    "strict_ainl_rate": 0.0,
                    "runtime_compile_rate": 0.0,
                    "nonempty_rate": 0.0,
                }
            )
            continue
        report = res["report"]
        lora = (report.get("summary") or {}).get("lora") or {}
        rows.append(
            {
                "adapter_path": str(candidate),
                "ok": True,
                "strict_ainl_rate": float(lora.get("strict_ainl_rate", 0.0)),
                "runtime_compile_rate": float(lora.get("runtime_compile_rate", 0.0)),
                "nonempty_rate": float(lora.get("nonempty_rate", 0.0)),
                "strict_ainl_ok": int(lora.get("strict_ainl_ok", 0)),
                "runtime_compile_ok": int(lora.get("runtime_compile_ok", 0)),
                "total_prompts": int(lora.get("total_prompts", 0)),
                "report_json": str(tmp_report),
            }
        )

    ranked = sorted(rows, key=_score_key, reverse=True)
    top_k = max(1, args.top_k)
    selected = ranked[:top_k]
    selected_paths = {Path(r["adapter_path"]).resolve() for r in selected}

    if args.promote_best_link and selected:
        link_path = adapter_root / "best_by_strict_ainl"
        best_target = Path(selected[0]["adapter_path"]).resolve()
        try:
            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()
            link_path.symlink_to(best_target, target_is_directory=True)
        except Exception:
            # Fall back to writing a pointer file.
            with open(adapter_root / "best_by_strict_ainl.txt", "w", encoding="utf-8") as f:
                f.write(str(best_target) + "\n")

    pruned: List[str] = []
    if args.prune_non_topk:
        for ckpt in [p for p in adapter_root.glob("checkpoint-*") if p.is_dir()]:
            if ckpt.resolve() in selected_paths:
                continue
            import shutil

            shutil.rmtree(ckpt)
            pruned.append(str(ckpt))

    out = {
        "adapter_root": str(adapter_root),
        "base_model": args.base_model,
        "prompt_set": str(args.prompt_set),
        "top_k": top_k,
        "ranked": ranked,
        "selected": selected,
        "pruned": pruned,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"[sweep] Wrote: {args.output_json}")
    if selected:
        print(
            "[sweep] Top-1 strict/runtime/nonempty: "
            f"{selected[0]['strict_ainl_rate']:.3f}/"
            f"{selected[0]['runtime_compile_rate']:.3f}/"
            f"{selected[0]['nonempty_rate']:.3f}"
        )


if __name__ == "__main__":
    main()
