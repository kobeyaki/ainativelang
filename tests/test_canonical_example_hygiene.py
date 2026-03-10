from pathlib import Path

from compiler_v2 import AICodeCompiler


ROOT = Path(__file__).resolve().parent.parent


CANONICAL_EXAMPLES = [
    "examples/hello.ainl",
    "examples/web/basic_web_api.ainl",
    "examples/crud_api.ainl",
    "examples/scraper/basic_scraper.ainl",
    "examples/rag_pipeline.ainl",
    "examples/retry_error_resilience.ainl",
    "examples/if_call_workflow.ainl",
    "examples/webhook_automation.ainl",
    "examples/monitor_escalation.ainl",
]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_canonical_examples_compile_strict():
    compiler = AICodeCompiler(strict_mode=True)
    for rel in CANONICAL_EXAMPLES:
        ir = compiler.compile(_read(rel))
        assert not ir.get("errors"), f"{rel} strict errors: {ir.get('errors')}"


def test_canonical_examples_avoid_compat_return_binding_style():
    for rel in CANONICAL_EXAMPLES:
        text = _read(rel)
        assert "_call_result" not in text, f"{rel} uses compatibility return binding"


def test_canonical_examples_use_explicit_uppercase_core_http_verbs():
    checks = {
        "examples/hello.ainl": "core.ADD",
        "examples/rag_pipeline.ainl": "core.ADD",
        "examples/scraper/basic_scraper.ainl": "http.GET",
        "examples/webhook_automation.ainl": "http.POST",
        "examples/monitor_escalation.ainl": "core.MAX",
    }
    for rel, token in checks.items():
        text = _read(rel)
        assert token in text, f"{rel} missing canonical token {token}"
