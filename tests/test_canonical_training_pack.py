import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "tooling" / "canonical_curriculum.json"
ARTIFACT_PROFILES = ROOT / "tooling" / "artifact_profiles.json"
MANIFEST = ROOT / "tooling" / "canonical_training_pack.json"
PACK_DIR = ROOT / "tooling" / "training_packs"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_training_manifest_matches_curriculum_and_strict_valid_set():
    curriculum = _json(CURRICULUM)
    profiles = _json(ARTIFACT_PROFILES)
    manifest = _json(MANIFEST)

    curriculum_paths = [e["path"] for e in sorted(curriculum["examples"], key=lambda x: x["order"])]
    strict_valid = set(profiles["examples"]["strict-valid"])
    manifest_paths = [e["path"] for e in sorted(manifest["examples"], key=lambda x: x["order"])]

    assert manifest_paths == curriculum_paths
    assert set(manifest_paths) == strict_valid
    assert all(e["strict_valid"] for e in manifest["examples"])
    assert all(e["public_safe"] for e in manifest["examples"])


def test_full_ordered_pack_order_and_membership():
    manifest = _json(MANIFEST)
    full_pack = _jsonl(PACK_DIR / "full_ordered.fewshot.jsonl")
    manifest_paths = [e["path"] for e in sorted(manifest["examples"], key=lambda x: x["order"])]
    pack_paths = [e["path"] for e in full_pack]
    assert pack_paths == manifest_paths


def test_no_non_strict_examples_leak_into_canonical_packs():
    profiles = _json(ARTIFACT_PROFILES)
    non_strict = set(profiles["examples"]["non-strict-only"])
    pack_files = [
        PACK_DIR / "full_ordered.fewshot.jsonl",
        PACK_DIR / "starter.fewshot.jsonl",
        PACK_DIR / "workflow.fewshot.jsonl",
        PACK_DIR / "resilience.fewshot.jsonl",
        PACK_DIR / "canonical.eval.jsonl",
    ]
    for pack in pack_files:
        rows = _jsonl(pack)
        assert not any(row["path"] in non_strict for row in rows)


def test_pack_metadata_matches_manifest():
    manifest = _json(MANIFEST)
    by_path = {e["path"]: e for e in manifest["examples"]}
    for row in _jsonl(PACK_DIR / "full_ordered.fewshot.jsonl"):
        m = by_path[row["path"]]
        assert row["order"] == m["order"]
        assert row["primary_pattern"] == m["primary_pattern"]
        assert row["secondary_pattern"] == m["secondary_pattern"]
