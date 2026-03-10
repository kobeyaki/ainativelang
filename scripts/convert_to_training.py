#!/usr/bin/env python3
"""Convert curated corpus to training formats with train/val/test splits."""

import argparse
import json
import random
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from compiler_v2 import AICodeCompiler
POS = BASE / "corpus" / "curated" / "pos.jsonl"
FULL = BASE / "corpus" / "curated" / "full_workflows.jsonl"
OUT_CHATML = BASE / "corpus" / "train_chatml.jsonl"
OUT_ALPACA = BASE / "corpus" / "train_alpaca.jsonl"
OUT_CHATML_TRAIN = BASE / "corpus" / "train_chatml_train.jsonl"
OUT_CHATML_VAL = BASE / "corpus" / "train_chatml_val.jsonl"
OUT_CHATML_TEST = BASE / "corpus" / "train_chatml_test.jsonl"
OUT_ALPACA_TRAIN = BASE / "corpus" / "train_alpaca_train.jsonl"
OUT_ALPACA_VAL = BASE / "corpus" / "train_alpaca_val.jsonl"
OUT_ALPACA_TEST = BASE / "corpus" / "train_alpaca_test.jsonl"


def load_jsonl(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def _dump(path: Path, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def _strip_fences(text: str) -> str:
    # Remove markdown code fences so training targets stay pure AINL.
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t)
    return t.strip()


def _strict_compile_ok(program: str) -> bool:
    compiler = AICodeCompiler(strict_mode=True)
    ir = compiler.compile(program, emit_graph=False)
    return not bool(ir.get("errors"))


def _split_indices(total: int, val_ratio: float, test_ratio: float) -> tuple[int, int, int]:
    n_test = max(1, int(total * test_ratio)) if total >= 3 else 0
    n_val = max(1, int(total * val_ratio)) if total >= 3 else 0
    n_train = total - n_val - n_test
    if n_train < 1 and total >= 3:
        n_train = 1
        if n_val > 1:
            n_val -= 1
        elif n_test > 1:
            n_test -= 1
    return n_train, n_val, n_test


def main():
    parser = argparse.ArgumentParser(description="Convert curated corpus to training JSONL formats.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for stable shuffling.")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio.")
    parser.add_argument("--test-ratio", type=float, default=0.1, help="Test split ratio.")
    parser.add_argument(
        "--enforce-strict",
        action="store_true",
        help="Keep only examples that pass strict-mode compilation.",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    pos = load_jsonl(POS)
    full = load_jsonl(FULL)
    if not pos and not full:
        raise SystemExit(
            f"No curated training data found. Expected {POS} and/or {FULL}. "
            "Run scripts/generate_corpus.py and scripts/curate_corpus.py first."
        )

    examples = pos + full
    rng.shuffle(examples)

    chatml = []
    alpaca = []

    system_msg = (
        "You are an AINL code generator. Output only valid AINL source code. "
        "Do not output markdown fences, prose, or any other language."
    )
    filtered = 0

    for ex in examples:
        prompt = ex.get("prompt", "Write an AINL program.").replace("Write AINL: ", "").strip()
        program = _strip_fences(ex["program"])
        if args.enforce_strict and not _strict_compile_ok(program):
            filtered += 1
            continue

        # ChatML
        chatml.append(json.dumps({
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"{prompt}\nOutput only AINL code."},
                {"role": "assistant", "content": program}
            ]
        }))

        # Alpaca
        alpaca.append(json.dumps({
            "instruction": "Write an AINL program.",
            "input": prompt,
            "output": program
        }))

    _dump(OUT_CHATML, chatml)
    _dump(OUT_ALPACA, alpaca)

    n_train, n_val, n_test = _split_indices(len(examples), args.val_ratio, args.test_ratio)
    chatml_train = chatml[:n_train]
    chatml_val = chatml[n_train:n_train + n_val]
    chatml_test = chatml[n_train + n_val:n_train + n_val + n_test]
    alpaca_train = alpaca[:n_train]
    alpaca_val = alpaca[n_train:n_train + n_val]
    alpaca_test = alpaca[n_train + n_val:n_train + n_val + n_test]

    _dump(OUT_CHATML_TRAIN, chatml_train)
    _dump(OUT_CHATML_VAL, chatml_val)
    _dump(OUT_CHATML_TEST, chatml_test)
    _dump(OUT_ALPACA_TRAIN, alpaca_train)
    _dump(OUT_ALPACA_VAL, alpaca_val)
    _dump(OUT_ALPACA_TEST, alpaca_test)

    print(f"Converted {len(examples)} examples:")
    print(f"- ChatML: {OUT_CHATML}")
    print(f"- Alpaca: {OUT_ALPACA}")
    print(f"- ChatML split: train={len(chatml_train)} val={len(chatml_val)} test={len(chatml_test)}")
    print(f"- Alpaca split: train={len(alpaca_train)} val={len(alpaca_val)} test={len(alpaca_test)}")
    if args.enforce_strict:
        print(f"- Strict-filtered rows skipped: {filtered}")

if __name__ == "__main__":
    main()
