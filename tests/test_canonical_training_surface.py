import json
from pathlib import Path

from compiler_v2 import AICodeCompiler


ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_PROFILES = ROOT / "tooling" / "artifact_profiles.json"


def _strict_valid_examples():
    profile = json.loads(ARTIFACT_PROFILES.read_text(encoding="utf-8"))
    return list(profile["examples"]["strict-valid"])


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_canonical_training_surface_covers_required_patterns():
    examples = _strict_valid_examples()
    compiler = AICodeCompiler(strict_mode=True)
    compiled = {rel: compiler.compile(_read(rel)) for rel in examples}

    has_web_api = any((ir.get("emit_capabilities") or {}).get("needs_python_api") for ir in compiled.values())
    has_scraper = any((ir.get("emit_capabilities") or {}).get("needs_scraper") for ir in compiled.values())
    has_cron = any((ir.get("emit_capabilities") or {}).get("needs_cron") for ir in compiled.values())
    has_retry_error = any(("Retry @" in _read(rel) and "Err @" in _read(rel)) for rel in examples)
    has_if_call = any(("If " in _read(rel) and "Call " in _read(rel) and "->out" in _read(rel)) for rel in examples)

    assert has_web_api, "missing canonical web/api coverage"
    assert has_scraper, "missing canonical scraper coverage"
    assert has_cron, "missing canonical scheduled/monitoring coverage"
    assert has_retry_error, "missing canonical retry/error coverage"
    assert has_if_call, "missing canonical if/call workflow coverage"


def test_new_canonical_examples_are_part_of_strict_valid_surface():
    examples = set(_strict_valid_examples())
    required = {
        "examples/retry_error_resilience.ainl",
        "examples/if_call_workflow.ainl",
        "examples/webhook_automation.ainl",
        "examples/monitor_escalation.ainl",
    }
    assert required.issubset(examples)
