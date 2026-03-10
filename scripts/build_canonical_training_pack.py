#!/usr/bin/env python3
"""Build canonical training/export packs from strict-valid curriculum."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_PATH = ROOT / "tooling" / "canonical_curriculum.json"
ARTIFACT_PROFILES_PATH = ROOT / "tooling" / "artifact_profiles.json"
MANIFEST_OUT = ROOT / "tooling" / "canonical_training_pack.json"
PACK_DIR = ROOT / "tooling" / "training_packs"


def _load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_source(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def _pack_selection(name: str, entries: List[Dict]) -> List[Dict]:
    if name == "full_ordered":
        return entries
    if name == "starter":
        return [e for e in entries if e["order"] <= 4]
    if name == "workflow":
        wanted = {"call_return", "if_call_workflow", "web_endpoint", "webhook_automation", "scraper_cron"}
        return [e for e in entries if e["primary_pattern"] in wanted]
    if name == "resilience":
        wanted = {"retry_error", "monitoring_escalation", "webhook_automation"}
        return [e for e in entries if e["primary_pattern"] in wanted]
    raise ValueError(f"unknown pack name: {name}")


def _to_jsonl(path: Path, rows: List[Dict]) -> None:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=True) for r in rows) + "\n", encoding="utf-8")


def _to_markdown(path: Path, title: str, rows: List[Dict]) -> None:
    lines: List[str] = [f"# {title}", ""]
    for row in rows:
        lines.append(f"## {row['order']}. `{row['path']}`")
        lines.append(f"- Primary: `{row['primary_pattern']}`")
        lines.append(f"- Secondary: `{row['secondary_pattern']}`")
        lines.append("")
        lines.append("```ainl")
        lines.append(row["source"].rstrip())
        lines.append("```")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    curriculum = _load_json(CURRICULUM_PATH)
    profiles = _load_json(ARTIFACT_PROFILES_PATH)
    strict_valid = set(profiles["examples"]["strict-valid"])

    entries: List[Dict] = []
    for item in sorted(curriculum["examples"], key=lambda x: int(x["order"])):
        rel = item["path"]
        entries.append(
            {
                "id": rel.replace("/", "__").replace(".", "_"),
                "order": int(item["order"]),
                "path": rel,
                "primary_pattern": item["primary_pattern"],
                "secondary_pattern": item["secondary_pattern"],
                "strict_valid": rel in strict_valid,
                "public_safe": True,
                "suitable_for": {
                    "finetuning": True,
                    "few_shot": True,
                    "eval": True,
                    "onboarding": True,
                },
                "source": _read_source(rel),
            }
        )

    manifest = {
        "schema_version": "1.0",
        "source_of_truth": {
            "curriculum": str(CURRICULUM_PATH.relative_to(ROOT)),
            "artifact_profiles": str(ARTIFACT_PROFILES_PATH.relative_to(ROOT)),
        },
        "examples": entries,
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    PACK_DIR.mkdir(parents=True, exist_ok=True)
    pack_defs = {
        "full_ordered": "Canonical Full Ordered Pack",
        "starter": "Canonical Starter Pack",
        "workflow": "Canonical Workflow Pack",
        "resilience": "Canonical Resilience Pack",
    }
    for name, title in pack_defs.items():
        selected = _pack_selection(name, entries)
        # Prompt-ready JSONL rows
        few_shot_rows = [
            {
                "id": r["id"],
                "order": r["order"],
                "path": r["path"],
                "primary_pattern": r["primary_pattern"],
                "secondary_pattern": r["secondary_pattern"],
                "instruction": "Use this as a canonical AI Native Lang example.",
                "completion": r["source"],
            }
            for r in selected
        ]
        _to_jsonl(PACK_DIR / f"{name}.fewshot.jsonl", few_shot_rows)
        _to_markdown(PACK_DIR / f"{name}.fewshot.md", title, selected)

    # Eval export: structured canonical references for offline harnesses.
    eval_rows = [
        {
            "id": r["id"],
            "order": r["order"],
            "path": r["path"],
            "primary_pattern": r["primary_pattern"],
            "secondary_pattern": r["secondary_pattern"],
            "strict_valid_expected": True,
            "canonical_source": r["source"],
            "checks": {
                "no_compat_return_binding": "_call_result" not in r["source"],
                "uppercase_adapter_verbs_preferred": True,
            },
        }
        for r in entries
    ]
    _to_jsonl(PACK_DIR / "canonical.eval.jsonl", eval_rows)
    (PACK_DIR / "canonical.eval.json").write_text(json.dumps({"schema_version": "1.0", "examples": eval_rows}, indent=2) + "\n", encoding="utf-8")

    print(f"wrote manifest: {MANIFEST_OUT}")
    print(f"wrote packs: {PACK_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
