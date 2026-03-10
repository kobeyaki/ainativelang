#!/usr/bin/env python3
"""
Build a canonical AINL-only curriculum dataset.

Goal:
- Force model behavior toward canonical line-based AINL output
- Avoid markdown/python/yaml style outputs in supervision
- Stage samples by complexity (easy -> medium -> hard)
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

POS = BASE / "corpus" / "curated" / "pos.jsonl"
FULL = BASE / "corpus" / "curated" / "full_workflows.jsonl"

OUT_CHATML = BASE / "corpus" / "train_chatml_curriculum.jsonl"
OUT_CHATML_TRAIN = BASE / "corpus" / "train_chatml_curriculum_train.jsonl"
OUT_CHATML_VAL = BASE / "corpus" / "train_chatml_curriculum_val.jsonl"
OUT_CHATML_TEST = BASE / "corpus" / "train_chatml_curriculum_test.jsonl"

OP_RE = re.compile(
    r"^(S|D|E|L[\w-]*:|R|J|If|Err|Retry|Call|Set|Filt|Sort|X|Loop|While|CacheGet|CacheSet|QueuePut|Tx|Enf)(\b|\s|$)"
)


def _load_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    rows: List[Dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _dedupe(rows: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    seen = set()
    for r in rows:
        p = (r.get("program") or "").strip()
        if not p or p in seen:
            continue
        seen.add(p)
        row = dict(r)
        row["program"] = p
        out.append(row)
    return out


def _strict_compile_ok(program: str) -> bool:
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(program, emit_graph=False)
    return not bool(ir.get("errors"))


def _canonical_ainl_ok(program: str) -> bool:
    lines = [ln.strip() for ln in (program or "").splitlines() if ln.strip()]
    if not lines:
        return False
    if any(tok in program for tok in ("```", "import ", "def ", "class ", "{", "}")):
        return False
    if not any(OP_RE.match(ln) for ln in lines):
        return False
    # At least half lines should look like AINL ops/labels.
    hit = sum(1 for ln in lines if OP_RE.match(ln))
    return (hit / len(lines)) >= 0.5


def _complexity_score(program: str) -> int:
    lines = [ln.strip() for ln in program.splitlines() if ln.strip()]
    n = len(lines)
    has_control = any(tok in program for tok in ("If ", "Err ", "Retry", "Loop", "While", "L"))
    has_io = any("."
                 in ln for ln in lines if ln.startswith("R "))
    score = n + (4 if has_control else 0) + (2 if has_io else 0)
    return score


def _chatml_row(prompt: str, program: str, difficulty: str) -> str:
    system = (
        "You are an AINL compiler assistant. "
        "Return only canonical line-based AINL source. "
        "No markdown, no prose, no YAML, no Python."
    )
    user = (
        f"{prompt.strip()}\n"
        "Output constraints:\n"
        "- Only AINL lines\n"
        "- Use canonical op/label style (e.g., S/D/E/L:/R/If/X/J)\n"
        "- No code fences"
    )
    return json.dumps(
        {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": program.strip()},
            ],
            "difficulty": difficulty,
        },
        ensure_ascii=True,
    )


def _write_jsonl(path: Path, rows: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(r + "\n")


def _split(rows: List[str], val_ratio: float, test_ratio: float) -> Tuple[List[str], List[str], List[str]]:
    total = len(rows)
    n_test = max(1, int(total * test_ratio)) if total >= 10 else max(0, int(total * test_ratio))
    n_val = max(1, int(total * val_ratio)) if total >= 10 else max(0, int(total * val_ratio))
    n_train = max(1, total - n_val - n_test)
    if n_train + n_val + n_test > total:
        n_train = total - n_val - n_test
    train = rows[:n_train]
    val = rows[n_train:n_train + n_val]
    test = rows[n_train + n_val:n_train + n_val + n_test]
    return train, val, test


def main() -> None:
    parser = argparse.ArgumentParser(description="Build canonical AINL curriculum dataset.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument(
        "--easy-oversample",
        type=float,
        default=1.5,
        help="Multiplier for easy samples in curriculum front-loading.",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    source = _dedupe(_load_jsonl(POS) + _load_jsonl(FULL))
    if not source:
        raise SystemExit("No curated source rows found. Run curate_corpus first.")

    filtered: List[Dict] = []
    dropped = 0
    for row in source:
        p = row["program"].strip()
        if not _strict_compile_ok(p):
            dropped += 1
            continue
        if not _canonical_ainl_ok(p):
            dropped += 1
            continue
        score = _complexity_score(p)
        out = dict(row)
        out["complexity_score"] = score
        filtered.append(out)

    # Assign tiers by sorted index thirds (not score threshold ties) so we
    # always produce easy/medium/hard curriculum groups.
    if not filtered:
        raise SystemExit("No rows left after canonical filtering.")
    sorted_rows = sorted(filtered, key=lambda x: x["complexity_score"])
    n = len(sorted_rows)
    b1 = max(1, n // 3)
    b2 = max(b1 + 1, (2 * n) // 3)
    for i, r in enumerate(sorted_rows):
        if i < b1:
            r["difficulty"] = "easy"
        elif i < b2:
            r["difficulty"] = "medium"
        else:
            r["difficulty"] = "hard"

    easy = [r for r in filtered if r["difficulty"] == "easy"]
    med = [r for r in filtered if r["difficulty"] == "medium"]
    hard = [r for r in filtered if r["difficulty"] == "hard"]

    rng.shuffle(easy)
    rng.shuffle(med)
    rng.shuffle(hard)

    # Curriculum order: easy -> medium -> hard, with optional easy oversampling.
    curriculum_rows: List[Dict] = []
    curriculum_rows.extend(easy)
    curriculum_rows.extend(med)
    curriculum_rows.extend(hard)
    if args.easy_oversample > 1 and easy:
        extra_n = int((args.easy_oversample - 1.0) * len(easy))
        curriculum_rows = easy[:extra_n] + curriculum_rows

    chatml = [
        _chatml_row(r.get("prompt", "Write an AINL program."), r["program"], r["difficulty"])
        for r in curriculum_rows
    ]
    _write_jsonl(OUT_CHATML, chatml)

    # Split after curriculum ordering so early train is easier.
    train, val, test = _split(chatml, args.val_ratio, args.test_ratio)
    _write_jsonl(OUT_CHATML_TRAIN, train)
    _write_jsonl(OUT_CHATML_VAL, val)
    _write_jsonl(OUT_CHATML_TEST, test)

    print(f"Canonical curriculum built from {len(source)} source rows")
    print(f"- Kept: {len(filtered)}")
    print(f"- Dropped: {dropped}")
    print(f"- Difficulty: easy={len(easy)} medium={len(med)} hard={len(hard)}")
    print(f"- Curriculum total: {len(chatml)}")
    print(f"- Splits: train={len(train)} val={len(val)} test={len(test)}")
    print(f"- Output: {OUT_CHATML}")


if __name__ == "__main__":
    main()
