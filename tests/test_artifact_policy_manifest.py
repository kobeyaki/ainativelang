import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler


ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "tooling" / "artifact_policy.json"


def _load() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def test_artifact_policy_paths_and_globs_resolve():
    p = _load()
    for rel in p["canonical_generated"]["files"]:
        assert (ROOT / rel).exists(), rel
    for rel in p["canonical_sources"]["files"]:
        assert (ROOT / rel).exists(), rel
    for rel in p["non_strict_only"]["files"]:
        assert (ROOT / rel).exists(), rel
    for g in p["historical_training"]["globs"]:
        matches = list(ROOT.glob(g))
        assert matches, f"glob has no matches: {g}"


def test_canonical_generated_ir_is_not_placeholder():
    p = _load()
    for rel in p["canonical_generated"]["files"]:
        obj = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        assert "_note" not in obj, rel
        assert obj.get("ir_version"), rel
        src = obj.get("source") or {}
        assert src.get("text"), rel


def test_packaging_embedded_policy_targets_exist():
    p = _load()
    for entry in p["packaging_embedded"]["entries"]:
        code = (ROOT / entry["file"]).read_text(encoding="utf-8")
        for sym in entry["symbols"]:
            assert sym in code, f"missing symbol {sym} in {entry['file']}"
        for rel in entry["source_of_truth"]:
            assert (ROOT / rel).exists(), rel


def test_non_strict_only_demo_policy_behavior():
    p = _load()
    for rel in p["non_strict_only"]["files"]:
        code = (ROOT / rel).read_text(encoding="utf-8")
        strict_errs = list(AICodeCompiler(strict_mode=True).compile(code, emit_graph=True).get("errors", []))
        loose_errs = list(AICodeCompiler(strict_mode=False).compile(code, emit_graph=True).get("errors", []))
        assert not loose_errs, f"{rel} should compile in non-strict mode"
        assert strict_errs, f"{rel} should fail strict mode by policy"
