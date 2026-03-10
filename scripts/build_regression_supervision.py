#!/usr/bin/env python3
"""
Build a prompt-target supervision dataset from regression prompts.

This is intentionally narrow and high-precision:
- user prompts close to evaluation prompts
- assistant outputs are canonical line-based AINL only
- strict compiler-gated rows only
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from compiler_v2 import AICodeCompiler

PROMPTS = BASE / "corpus" / "curated" / "regression_prompts.jsonl"
OUT_ALL = BASE / "corpus" / "train_chatml_regression_supervised.jsonl"
OUT_TRAIN = BASE / "corpus" / "train_chatml_regression_supervised_train.jsonl"
OUT_VAL = BASE / "corpus" / "train_chatml_regression_supervised_val.jsonl"
OUT_TEST = BASE / "corpus" / "train_chatml_regression_supervised_test.jsonl"


CANONICAL_PROGRAMS: Dict[str, str] = {
    "weather_email": (
        "L1: R http.GET \"/weather?city=Seattle\" ->resp\n"
        "L2: R queue.PUT \"alerts\" resp ->_ J \"done\""
    ),
    "api_status_alert": (
        "Cr */5 * * * * ->L0\n"
        "L0: R api.G \"/status\" ->resp\n"
        "L1: If resp.ok ->L2 ->L3\n"
        "L2: J \"done\"\n"
        "L3: R queue.PUT \"alerts\" resp ->_ J \"done\""
    ),
    "rss_to_sqlite": (
        "Cr */10 * * * * ->L0\n"
        "L0: R http.GET \"/rss\" ->feed\n"
        "L1: R sqlite.QUERY \"SELECT 1\" ->rows J \"done\""
    ),
    "daily_csv_report": (
        "Cr 0 8 * * * ->L0\n"
        "L0: R sqlite.QUERY \"SELECT * FROM report\" ->rows\n"
        "L1: R fs.WRITE \"/tmp/report.csv\" rows ->_ J \"done\""
    ),
    "webhook_ingest": (
        "L0: R http.GET \"/webhook\" ->payload\n"
        "L1: If payload ->L2 ->L3\n"
        "L2: R sqlite.EXECUTE \"INSERT INTO payloads(raw) VALUES (?)\" payload ->_ J \"done\"\n"
        "L3: J \"invalid_payload\""
    ),
    "retry_on_http_fail": (
        "L1: R http.GET \"/upstream\" ->resp Retry @n1 3 0 Err @n1 ->L9 J resp\n"
        "L9: J \"failed\""
    ),
    "branch_on_risk": (
        "L1: R api.G \"/records\" ->records\n"
        "L2: If records.risk ->L3 ->L4\n"
        "L3: J \"manual_review\"\n"
        "L4: J \"auto_process\""
    ),
    "queue_worker": (
        "Cr */1 * * * * ->L0\n"
        "L0: R queue.PUT \"jobs\" {\"task\":\"tick\"} ->job\n"
        "L1: If job ->L2 ->L3\n"
        "L2: J \"done\"\n"
        "L3: J \"done\""
    ),
    "db_to_email_digest": (
        "Cr 0 9 * * * ->L0\n"
        "L0: R sqlite.QUERY \"SELECT * FROM tickets WHERE open=1\" ->rows\n"
        "L1: R queue.PUT \"ticket_digest\" rows ->_ J \"done\""
    ),
    "auth_policy_gate": (
        "L1: R ext.ECHO \"ok\" ->auth\n"
        "L2: If auth ->L3 ->L4\n"
        "L3: R sqlite.QUERY \"SELECT 1\" ->rows J \"done\"\n"
        "L4: J \"unauthorized\""
    ),
    "transform_and_post": (
        "L1: R http.GET \"/source\" ->resp\n"
        "L2: X payload resp\n"
        "L3: R http.POST \"/target\" payload ->post_resp J \"done\""
    ),
    "cron_backup_notify": (
        "Cr 0 2 * * * ->L0\n"
        "L0: R sqlite.QUERY \"SELECT * FROM items\" ->rows\n"
        "L1: R fs.WRITE \"/tmp/backup.json\" rows ->_\n"
        "L2: R queue.PUT \"ops\" rows ->_ J \"done\""
    ),
}

REQUIRED_OPS_BY_PROMPT: Dict[str, Set[str]] = {
    "weather_email": {"R", "J"},
    "api_status_alert": {"Cr", "R", "If", "J"},
    "rss_to_sqlite": {"Cr", "R"},
    "daily_csv_report": {"Cr", "R"},
    "webhook_ingest": {"R", "If", "J"},
    "retry_on_http_fail": {"R", "Retry", "J"},
    "branch_on_risk": {"R", "If", "J"},
    "queue_worker": {"Cr", "R", "If", "J"},
    "db_to_email_digest": {"Cr", "R", "J"},
    "auth_policy_gate": {"R", "If", "J"},
    "transform_and_post": {"R", "X", "J"},
    "cron_backup_notify": {"Cr", "R", "J"},
}

OP_RE = re.compile(
    r"^(S|D|E|L[\w-]*:|R|J|U|T|Q|Sc|Cr|P|C|A|Rt|Lay|Fm|Tbl|Ev|"
    r"If|Err|Retry|Call|Set|Filt|Sort|X|Loop|While|CacheGet|CacheSet|QueuePut|Tx|Enf)(\b|\s|$)"
)
KNOWN_OPS = {
    "S", "D", "E", "R", "J", "U", "T", "Q", "Sc", "Cr", "P", "C", "A", "Rt", "Lay", "Fm", "Tbl", "Ev",
    "If", "Err", "Retry", "Call", "Set", "Filt", "Sort", "X", "Loop", "While", "CacheGet", "CacheSet",
    "QueuePut", "Tx", "Enf",
}


def _load_prompts(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                rows.append({"id": row["id"], "prompt": row["prompt"]})
    return rows


def _strict_ok(program: str) -> bool:
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(program, emit_graph=False)
    return not bool(ir.get("errors"))


def _chatml(user_prompt: str, program: str) -> str:
    return json.dumps(
        {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You generate canonical AINL only. "
                        "Return only line-based AINL source with ops/labels. "
                        "No markdown fences. No Python. No YAML."
                    ),
                },
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": program},
            ]
        },
        ensure_ascii=True,
    )


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
    ops = set(_program_ops(program))
    required = REQUIRED_OPS_BY_PROMPT.get(prompt_id, set())
    return required.issubset(ops)


def _expand_prompt_variants(prompt: str, variants_per_prompt: int, rng: random.Random) -> List[str]:
    base_templates = [
        "{prompt}",
        "Write canonical AINL for this task: {prompt}",
        "Produce strict AINL (no markdown, no YAML): {prompt}",
        "{prompt} Output only canonical AINL lines.",
        "{prompt} Use only AINL op lines (S/D/E/L:/R/If/X/J).",
    ]
    prefixes = [
        "Return only AINL source.",
        "No prose, only AINL lines.",
        "Use canonical line-based AINL.",
        "Generate strict AINL program.",
    ]
    suffixes = [
        "No markdown fences.",
        "No YAML or Python.",
        "Only ops and labels.",
        "Keep syntax strict.",
    ]
    replacements = [
        ("Generate", "Create"),
        ("Generate", "Build"),
        ("Create", "Generate"),
        ("Build", "Generate"),
        ("workflow", "program"),
        ("program", "workflow"),
        ("emails", "sends email to"),
        ("checks", "queries"),
    ]

    out: List[str] = []
    seen = set()

    def add(text: str) -> None:
        t = " ".join((text or "").split()).strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)

    # Seed with stable templates.
    for tmpl in base_templates:
        add(tmpl.format(prompt=prompt))

    # Create more paraphrases with prefix/suffix + lexical substitutions.
    attempts = 0
    while len(out) < variants_per_prompt and attempts < variants_per_prompt * 20:
        attempts += 1
        core = rng.choice(base_templates).format(prompt=prompt)
        src, dst = rng.choice(replacements)
        core = core.replace(src, dst, 1)
        text = f"{rng.choice(prefixes)} {core} {rng.choice(suffixes)}"
        add(text)

    return out[:variants_per_prompt]


def _split(rows: List[str], val_ratio: float, test_ratio: float):
    n = len(rows)
    n_test = max(1, int(n * test_ratio)) if n >= 10 else 0
    n_val = max(1, int(n * val_ratio)) if n >= 10 else 0
    n_train = max(1, n - n_val - n_test)
    return rows[:n_train], rows[n_train:n_train + n_val], rows[n_train + n_val:n_train + n_val + n_test]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build regression-paired canonical supervision dataset.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument(
        "--variants-per-prompt",
        type=int,
        default=24,
        help="How many paraphrased user prompts to create per regression id.",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=3,
        help="Minimum non-empty lines required in canonical target programs.",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    prompts = _load_prompts(PROMPTS)
    rows: List[str] = []
    skipped = 0
    for row in prompts:
        pid = row["id"]
        prompt = row["prompt"]
        program = CANONICAL_PROGRAMS.get(pid)
        if not program:
            skipped += 1
            continue
        if not _strict_ok(program):
            skipped += 1
            continue
        if not _passes_quality_gate(pid, program, args.min_lines):
            skipped += 1
            continue
        for user_prompt in _expand_prompt_variants(prompt, args.variants_per_prompt, rng):
            rows.append(_chatml(user_prompt, program))

    rng.shuffle(rows)
    train, val, test = _split(rows, args.val_ratio, args.test_ratio)

    for path, data in [(OUT_ALL, rows), (OUT_TRAIN, train), (OUT_VAL, val), (OUT_TEST, test)]:
        with open(path, "w", encoding="utf-8") as f:
            for line in data:
                f.write(line + "\n")

    print(f"Built regression supervision rows: {len(rows)} (skipped prompts: {skipped})")
    print(f"Split sizes: train={len(train)} val={len(val)} test={len(test)}")
    print(f"Output: {OUT_ALL}")


if __name__ == "__main__":
    main()
