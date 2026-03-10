#!/usr/bin/env python3
"""
Build a targeted boost dataset from failing prompt families in an eval report.

Purpose:
- Identify prompt IDs where LoRA failed strict AINL validation
- Generate additional high-signal supervision for only those failing IDs
- Merge with existing distill dataset to produce boosted train/val/test files
"""

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from scripts.build_regression_supervision import CANONICAL_PROGRAMS, _expand_prompt_variants, _load_prompts
from scripts.teacher_distill_dataset import _broken_candidates, _chatml


PROMPTS = BASE / "corpus" / "curated" / "regression_prompts.jsonl"
DEFAULT_INPUT_TRAIN = BASE / "corpus" / "train_chatml_distill_train.jsonl"
DEFAULT_INPUT_VAL = BASE / "corpus" / "train_chatml_distill_val.jsonl"
DEFAULT_INPUT_TEST = BASE / "corpus" / "train_chatml_distill_test.jsonl"

OUT_ALL = BASE / "corpus" / "train_chatml_distill_boost.jsonl"
OUT_TRAIN = BASE / "corpus" / "train_chatml_distill_boost_train.jsonl"
OUT_VAL = BASE / "corpus" / "train_chatml_distill_boost_val.jsonl"
OUT_TEST = BASE / "corpus" / "train_chatml_distill_boost_test.jsonl"


def _load_jsonl_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    rows: List[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(line)
    return rows


def _split(rows: List[str], val_ratio: float, test_ratio: float) -> Tuple[List[str], List[str], List[str]]:
    n = len(rows)
    n_test = max(1, int(n * test_ratio)) if n >= 20 else max(0, int(n * test_ratio))
    n_val = max(1, int(n * val_ratio)) if n >= 20 else max(0, int(n * val_ratio))
    n_train = max(1, n - n_val - n_test)
    return rows[:n_train], rows[n_train:n_train + n_val], rows[n_train + n_val:n_train + n_val + n_test]


def _failing_prompt_ids(eval_report: Path) -> Set[str]:
    if not eval_report.exists():
        raise SystemExit(f"Eval report not found: {eval_report}")
    with open(eval_report, encoding="utf-8") as f:
        report = json.load(f)
    out: Set[str] = set()
    for row in report.get("results", []):
        pid = str(row.get("id", "")).strip()
        lora = row.get("lora", {})
        compile_info = lora.get("compile", {}) if isinstance(lora, dict) else {}
        if not bool(compile_info.get("strict_ainl_ok")) and pid:
            out.add(pid)
    return out


def _sample_with_replacement(rows: List[str], n: int, rng: random.Random) -> List[str]:
    if n <= 0 or not rows:
        return []
    if len(rows) >= n:
        picked = list(rows)
        rng.shuffle(picked)
        return picked[:n]
    out = []
    while len(out) < n:
        out.append(rng.choice(rows))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build failure-focused distill boost dataset.")
    parser.add_argument("--eval-report", type=Path, required=True, help="Eval report JSON to mine failing prompt IDs from.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples-per-failed-id", type=int, default=48)
    parser.add_argument("--variants-per-prompt", type=int, default=24)
    parser.add_argument("--mix-gold", type=float, default=0.50)
    parser.add_argument("--mix-repair", type=float, default=0.35)
    parser.add_argument("--mix-check", type=float, default=0.15)
    parser.add_argument("--input-train", type=Path, default=DEFAULT_INPUT_TRAIN)
    parser.add_argument("--input-val", type=Path, default=DEFAULT_INPUT_VAL)
    parser.add_argument("--input-test", type=Path, default=DEFAULT_INPUT_TEST)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    args = parser.parse_args()

    mix_total = args.mix_gold + args.mix_repair + args.mix_check
    if abs(mix_total - 1.0) > 1e-6:
        raise SystemExit(f"Mix ratios must sum to 1.0, got {mix_total:.4f}")
    if args.samples_per_failed_id < 3:
        raise SystemExit("--samples-per-failed-id must be >= 3")

    rng = random.Random(args.seed)
    failing_ids = _failing_prompt_ids(args.eval_report)
    prompts = {r["id"]: r["prompt"] for r in _load_prompts(PROMPTS)}

    if not failing_ids:
        print("No failing prompt IDs found in eval report; copying existing distill datasets.")
        base_train = _load_jsonl_lines(args.input_train)
        base_val = _load_jsonl_lines(args.input_val)
        base_test = _load_jsonl_lines(args.input_test)
        all_rows = base_train + base_val + base_test
        with open(OUT_ALL, "w", encoding="utf-8") as f:
            for ln in all_rows:
                f.write(ln + "\n")
        for out_path, rows in ((OUT_TRAIN, base_train), (OUT_VAL, base_val), (OUT_TEST, base_test)):
            with open(out_path, "w", encoding="utf-8") as f:
                for ln in rows:
                    f.write(ln + "\n")
        print(f"Output: {OUT_ALL}")
        return

    system_gold = (
        "You are a teacher model for AINL. Return only canonical line-based AINL. "
        "No markdown fences, no YAML, no Python, no prose."
    )
    system_repair = (
        "You repair broken model outputs into strict canonical AINL. "
        "Return only corrected AINL lines."
    )

    boost_rows: List[str] = []
    skipped = 0
    for pid in sorted(failing_ids):
        task = prompts.get(pid, "").strip()
        gold = CANONICAL_PROGRAMS.get(pid, "").strip()
        if not task or not gold:
            skipped += 1
            continue

        target_total = int(args.samples_per_failed_id)
        gold_n = max(1, int(round(target_total * args.mix_gold)))
        repair_n = max(1, int(round(target_total * args.mix_repair)))
        check_n = max(1, target_total - gold_n - repair_n)
        while gold_n + repair_n + check_n > target_total:
            if repair_n > 1:
                repair_n -= 1
            elif gold_n > 1:
                gold_n -= 1
            else:
                check_n -= 1
        while gold_n + repair_n + check_n < target_total:
            repair_n += 1

        gold_rows: List[str] = []
        for user_prompt in _expand_prompt_variants(task, max(args.variants_per_prompt, gold_n), rng):
            gold_rows.append(_chatml(system_gold, user_prompt, gold, "boost_gold", pid))

        candidates = _broken_candidates(gold)
        rng.shuffle(candidates)
        repair_rows: List[str] = []
        for bad in candidates:
            for template in (
                "Task:\n{task}\n\nThis draft is invalid or non-canonical. Rewrite it into strict canonical AINL only:\n{bad}\n",
                "Convert this broken output into valid canonical AINL only.\nTask: {task}\nBroken:\n{bad}\n",
                "Repair to canonical AINL. Return only corrected AINL lines.\nTask: {task}\nCandidate:\n{bad}\n",
            ):
                repair_rows.append(_chatml(system_repair, template.format(task=task, bad=bad), gold, "boost_repair", pid))

        check_rows: List[str] = []
        for bad in candidates[: max(1, min(len(candidates), 4))]:
            checker_prompt = (
                "Check whether this output is valid canonical AINL. "
                "If invalid, rewrite to valid canonical AINL and output only the corrected program.\n"
                f"Task: {task}\n"
                f"Candidate:\n{bad}"
            )
            check_rows.append(_chatml(system_repair, checker_prompt, gold, "boost_check_rewrite", pid))

        boost_rows.extend(_sample_with_replacement(gold_rows, gold_n, rng))
        boost_rows.extend(_sample_with_replacement(repair_rows, repair_n, rng))
        boost_rows.extend(_sample_with_replacement(check_rows, check_n, rng))

    rng.shuffle(boost_rows)

    base_train = _load_jsonl_lines(args.input_train)
    base_val = _load_jsonl_lines(args.input_val)
    base_test = _load_jsonl_lines(args.input_test)
    merged_all = base_train + base_val + base_test + boost_rows
    rng.shuffle(merged_all)
    train, val, test = _split(merged_all, args.val_ratio, args.test_ratio)

    for out_path, rows in ((OUT_ALL, merged_all), (OUT_TRAIN, train), (OUT_VAL, val), (OUT_TEST, test)):
        with open(out_path, "w", encoding="utf-8") as f:
            for line in rows:
                f.write(line + "\n")

    print(f"Failing prompt IDs: {len(failing_ids)} (skipped missing canonical/prompt: {skipped})")
    print(f"Boost rows generated: {len(boost_rows)}")
    print(f"Merged total rows: {len(merged_all)}")
    print(f"Splits: train={len(train)} val={len(val)} test={len(test)}")
    print(f"Output: {OUT_ALL}")


if __name__ == "__main__":
    main()
