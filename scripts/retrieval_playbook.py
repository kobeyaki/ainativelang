#!/usr/bin/env python3
"""
Deterministic playbook retrieval for AINL generation.
Uses tag/keyword overlap (no embeddings) for reproducible eval runs.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _words(text: str) -> set:
    return set(re.findall(r"[a-z0-9_]+", (text or "").lower()))


def load_playbooks(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    items: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            obj = json.loads(ln)
            if not isinstance(obj, dict):
                continue
            items.append(obj)
    return items


def score_playbook(prompt: str, pb: Dict[str, Any]) -> int:
    pw = _words(prompt)
    tags = set((pb.get("tags") or []))
    keywords = set((pb.get("task_keywords") or []))
    score = 0
    for t in tags:
        if t.lower() in pw:
            score += 3
    for k in keywords:
        if k.lower() in pw:
            score += 2
    if pb.get("domain", "").lower() in pw:
        score += 2
    return score


def retrieve_playbooks(prompt: str, playbooks: List[Dict[str, Any]], top_k: int = 2) -> List[Dict[str, Any]]:
    scored: List[Tuple[int, Dict[str, Any]]] = []
    for pb in playbooks:
        scored.append((score_playbook(prompt, pb), pb))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [pb for sc, pb in scored[:top_k] if sc > 0]


def compose_playbook_context(prompt: str, playbooks: List[Dict[str, Any]], top_k: int = 2) -> str:
    matched = retrieve_playbooks(prompt, playbooks, top_k=top_k)
    if not matched:
        return ""
    lines: List[str] = []
    lines.append("Use these AINL capability playbooks when relevant. Prefer additive changes and strict-valid structures.")
    for pb in matched:
        lines.append(f"- Playbook: {pb.get('id', 'unknown')}")
        rules = pb.get("rules") or []
        if rules:
            lines.append("  Rules:")
            for r in rules[:5]:
                lines.append(f"  - {r}")
        ex = (pb.get("ainl") or "").strip()
        if ex:
            lines.append("  Example:")
            lines.append(ex)
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Preview deterministic playbook retrieval")
    ap.add_argument("--prompt", required=True, help="Task prompt text")
    ap.add_argument("--playbooks", default="data/evals/playbooks/default.jsonl", help="JSONL playbook file")
    ap.add_argument("--top-k", type=int, default=2, help="Number of playbooks to retrieve")
    args = ap.parse_args()

    pbs = load_playbooks(args.playbooks)
    matched = retrieve_playbooks(args.prompt, pbs, top_k=args.top_k)
    print(json.dumps({"count": len(matched), "ids": [m.get("id") for m in matched]}, indent=2))
    print("\n--- composed context ---\n")
    print(compose_playbook_context(args.prompt, pbs, top_k=args.top_k))


if __name__ == "__main__":
    main()
