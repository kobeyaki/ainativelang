from pathlib import Path

from compiler_v2 import AICodeCompiler


ROOT = Path(__file__).resolve().parent.parent


def _compile(rel_path: str):
    src = (ROOT / rel_path).read_text(encoding="utf-8")
    return AICodeCompiler(strict_mode=False).compile(src)


def test_public_example_intent_matches_compiler_capabilities():
    # Narrow trust guard for high-visibility benchmarked examples.
    expected = {
        "examples/scraper/basic_scraper.ainl": "needs_scraper",
        "examples/web/basic_web_api.ainl": "needs_python_api",
        "examples/cron/monitor_and_alert.ainl": "needs_cron",
        "examples/rag_pipeline.ainl": "needs_python_api",
        "examples/retry_error_resilience.ainl": "needs_python_api",
        "examples/if_call_workflow.ainl": "needs_python_api",
        "examples/webhook_automation.ainl": "needs_python_api",
        "examples/monitor_escalation.ainl": "needs_cron",
    }
    for rel, cap in expected.items():
        ir = _compile(rel)
        assert ir["emit_capabilities"].get(cap) is True
