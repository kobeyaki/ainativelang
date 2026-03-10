#!/usr/bin/env python3
"""
Create a teacher-style distillation dataset for AINL.

Outputs mixed supervision examples:
1) direct task -> canonical AINL
2) broken output -> repaired canonical AINL
3) validity-check prompt -> canonical rewrite
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from compiler_v2 import AICodeCompiler
from scripts.build_regression_supervision import (
    CANONICAL_PROGRAMS,
    REQUIRED_OPS_BY_PROMPT,
    _expand_prompt_variants,
    _load_prompts,
)

PROMPTS = BASE / "corpus" / "curated" / "regression_prompts.jsonl"
OUT_ALL = BASE / "corpus" / "train_chatml_distill.jsonl"
OUT_TRAIN = BASE / "corpus" / "train_chatml_distill_train.jsonl"
OUT_VAL = BASE / "corpus" / "train_chatml_distill_val.jsonl"
OUT_TEST = BASE / "corpus" / "train_chatml_distill_test.jsonl"
OP_RE = re.compile(
    r"^(S|D|E|L[\w-]*:|R|J|U|T|Q|Sc|Cr|P|C|A|Rt|Lay|Fm|Tbl|Ev|"
    r"If|Err|Retry|Call|Set|Filt|Sort|X|Loop|While|CacheGet|CacheSet|QueuePut|Tx|Enf)(\b|\s|$)"
)
KNOWN_OPS = {
    "S", "D", "E", "R", "J", "U", "T", "Q", "Sc", "Cr", "P", "C", "A", "Rt", "Lay", "Fm", "Tbl", "Ev",
    "If", "Err", "Retry", "Call", "Set", "Filt", "Sort", "X", "Loop", "While", "CacheGet", "CacheSet",
    "QueuePut", "Tx", "Enf",
}


def _strict_ok(program: str) -> bool:
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(program, emit_graph=False)
    return not bool(ir.get("errors"))


def _chatml(system: str, user: str, assistant: str, sample_type: str, prompt_id: str) -> str:
    return json.dumps(
        {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": assistant},
            ],
            "sample_type": sample_type,
            "prompt_id": prompt_id,
        },
        ensure_ascii=True,
    )


def _broken_candidates(program: str) -> List[str]:
    lines = [ln.strip() for ln in program.splitlines() if ln.strip()]
    compact = " ".join(lines)
    out = [
        f"```ainl\n{program}\n```",
        "workflow:\n  - " + "\n  - ".join(lines[: min(4, len(lines))]),
        "import requests\n# generated code\n" + compact,
        program.replace("->", "=>"),
        program.replace(" J ", " RETURN "),
    ]
    if lines:
        out.append("\n".join(lines[:-1]))  # truncated output
    return out


def _program_ops(program: str) -> List[str]:
    ops: List[str] = []
    for raw in (program or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if parts and parts[0].endswith(":"):
            line = line[len(parts[0]) :].strip()
        for token in line.split():
            t = token.strip()
            if t in KNOWN_OPS and OP_RE.match(t):
                ops.append(t)
    return ops


def _passes_quality_gate(prompt_id: str, program: str, min_lines: int) -> bool:
    lines = [ln.strip() for ln in (program or "").splitlines() if ln.strip()]
    if len(lines) < min_lines:
        return False
    required = REQUIRED_OPS_BY_PROMPT.get(prompt_id, set())
    return required.issubset(set(_program_ops(program)))


def _sample_with_replacement(rows: List[str], n: int, rng: random.Random) -> List[str]:
    if n <= 0:
        return []
    if not rows:
        return []
    if len(rows) >= n:
        picked = list(rows)
        rng.shuffle(picked)
        return picked[:n]
    out = []
    while len(out) < n:
        out.append(rng.choice(rows))
    return out


def _split(rows: List[str], val_ratio: float, test_ratio: float) -> Tuple[List[str], List[str], List[str]]:
    n = len(rows)
    n_test = max(1, int(n * test_ratio)) if n >= 20 else max(0, int(n * test_ratio))
    n_val = max(1, int(n * val_ratio)) if n >= 20 else max(0, int(n * val_ratio))
    n_train = max(1, n - n_val - n_test)
    return rows[:n_train], rows[n_train:n_train + n_val], rows[n_train + n_val:n_train + n_val + n_test]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build teacher distillation dataset for AINL.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--variants-per-prompt", type=int, default=24)
    parser.add_argument("--samples-per-prompt", type=int, default=40)
    parser.add_argument("--mix-gold", type=float, default=0.50)
    parser.add_argument("--mix-repair", type=float, default=0.35)
    parser.add_argument("--mix-check", type=float, default=0.15)
    parser.add_argument("--min-lines", type=int, default=3)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    args = parser.parse_args()
    mix_total = args.mix_gold + args.mix_repair + args.mix_check
    if abs(mix_total - 1.0) > 1e-6:
        raise SystemExit(f"Mix ratios must sum to 1.0, got {mix_total:.4f}")
    if args.samples_per_prompt < 3:
        raise SystemExit("--samples-per-prompt must be >= 3")

    rng = random.Random(args.seed)
    prompts = _load_prompts(PROMPTS)
    rows: List[str] = []
    skipped = 0

    system_gold = (
        "You are a teacher model for AINL. Return only canonical line-based AINL. "
        "No markdown fences, no YAML, no Python, no prose."
    )
    system_repair = (
        "You repair broken model outputs into strict canonical AINL. "
        "Return only corrected AINL lines."
    )

    for row in prompts:
        pid = row["id"]
        task = row["prompt"].strip()
        gold = CANONICAL_PROGRAMS.get(pid)
        if not gold or not _strict_ok(gold):
            skipped += 1
            continue
        if not _passes_quality_gate(pid, gold, args.min_lines):
            skipped += 1
            continue

        target_total = int(args.samples_per_prompt)
        gold_n = max(1, int(round(target_total * args.mix_gold)))
        repair_n = max(1, int(round(target_total * args.mix_repair)))
        check_n = max(1, target_total - gold_n - repair_n)
        # Rebalance if rounding overflowed.
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
            gold_rows.append(_chatml(system_gold, user_prompt, gold, "gold", pid))

        # Repair supervision from hard negatives.
        repair_rows: List[str] = []
        candidates = _broken_candidates(gold)
        rng.shuffle(candidates)
        for bad in candidates:
            for template in (
                "Task:\n{task}\n\nThis draft is invalid or non-canonical. Rewrite it into strict canonical AINL only:\n{bad}\n",
                "Convert this broken output into valid canonical AINL only.\nTask: {task}\nBroken:\n{bad}\n",
                "Repair to canonical AINL. Return only corrected AINL lines.\nTask: {task}\nCandidate:\n{bad}\n",
            ):
                user_prompt = template.format(task=task, bad=bad)
                repair_rows.append(_chatml(system_repair, user_prompt, gold, "repair", pid))

        # Validity-check style supervision.
        check_rows: List[str] = []
        for bad in candidates[: max(1, min(len(candidates), 3))]:
            checker_prompt = (
                "Check whether this output is valid canonical AINL. "
                "If invalid, rewrite to valid canonical AINL and output only the corrected program.\n"
                f"Task: {task}\n"
                f"Candidate:\n{bad}"
            )
            check_rows.append(_chatml(system_repair, checker_prompt, gold, "check_rewrite", pid))

        rows.extend(_sample_with_replacement(gold_rows, gold_n, rng))
        rows.extend(_sample_with_replacement(repair_rows, repair_n, rng))
        rows.extend(_sample_with_replacement(check_rows, check_n, rng))

    rng.shuffle(rows)
    train, val, test = _split(rows, args.val_ratio, args.test_ratio)

    for path, data in ((OUT_ALL, rows), (OUT_TRAIN, train), (OUT_VAL, val), (OUT_TEST, test)):
        with open(path, "w", encoding="utf-8") as f:
            for line in data:
                f.write(line + "\n")

    print(f"Distill rows: {len(rows)} (skipped prompts: {skipped})")
    print(
        "Mix ratios used: "
        f"gold={args.mix_gold:.2f} repair={args.mix_repair:.2f} check={args.mix_check:.2f} "
        f"samples_per_prompt={args.samples_per_prompt}"
    )
    print(f"Split sizes: train={len(train)} val={len(val)} test={len(test)}")
    print(f"Output: {OUT_ALL}")


if __name__ == "__main__":
    main()
