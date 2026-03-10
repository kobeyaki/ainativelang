import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_PATH = ROOT / "tooling" / "canonical_curriculum.json"
ARTIFACT_PROFILES_PATH = ROOT / "tooling" / "artifact_profiles.json"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_curriculum_matches_strict_valid_set():
    curriculum = _load_json(CURRICULUM_PATH)
    artifact_profiles = _load_json(ARTIFACT_PROFILES_PATH)
    strict_valid = set(artifact_profiles["examples"]["strict-valid"])
    listed = {entry["path"] for entry in curriculum["examples"]}
    assert listed == strict_valid


def test_curriculum_order_is_stable_and_sequential():
    curriculum = _load_json(CURRICULUM_PATH)
    orders = [entry["order"] for entry in curriculum["examples"]]
    assert orders == list(range(1, len(orders) + 1))


def test_curriculum_primary_pattern_is_unique():
    curriculum = _load_json(CURRICULUM_PATH)
    patterns = [entry["primary_pattern"] for entry in curriculum["examples"]]
    assert len(patterns) == len(set(patterns))


def test_curriculum_covers_required_agent_workflow_categories():
    curriculum = _load_json(CURRICULUM_PATH)
    patterns = {entry["primary_pattern"] for entry in curriculum["examples"]}
    required = {
        "web_endpoint",
        "scraper_cron",
        "retry_error",
        "if_call_workflow",
        "monitoring_escalation",
    }
    assert required.issubset(patterns)
