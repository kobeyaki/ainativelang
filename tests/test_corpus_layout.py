import os
import json
from pathlib import Path


def test_corpus_examples_have_required_files():
    root = Path(__file__).resolve().parent.parent / "corpus"
    assert root.exists()
    examples = [p for p in root.iterdir() if p.is_dir() and p.name.startswith("example_")]
    assert examples, "expected at least one corpus example directory"
    required = {
        "prompt.txt",
        "program.ainl",
        "corrected_program.ainl",
        "invalid_program.ainl",
        "ir.json",
        "errors.json",
    }
    for ex in examples:
        have = {p.name for p in ex.iterdir() if p.is_file()}
        missing = required - have
        assert not missing, f"{ex.name} missing: {sorted(missing)}"


def test_ir_snapshots_are_generated_not_placeholders():
    root = Path(__file__).resolve().parent.parent
    corpus = root / "corpus"
    examples = [p for p in corpus.iterdir() if p.is_dir() and p.name.startswith("example_")]
    for ex in examples:
        ir_path = ex / "ir.json"
        obj = json.loads(ir_path.read_text(encoding="utf-8"))
        assert "_note" not in obj, f"{ir_path} is a placeholder, expected generated IR snapshot"
        assert obj.get("ir_version"), f"{ir_path} missing ir_version"
        source = obj.get("source") or {}
        assert source.get("text"), f"{ir_path} missing source.text"

    demo_ir = root / "demo" / "emit" / "ir.json"
    demo_obj = json.loads(demo_ir.read_text(encoding="utf-8"))
    assert "_note" not in demo_obj, f"{demo_ir} is a placeholder, expected generated IR snapshot"
    assert demo_obj.get("ir_version"), f"{demo_ir} missing ir_version"

