from pathlib import Path

from compiler_v2 import AICodeCompiler
from tooling.bench_metrics import tiktoken_count


ROOT = Path(__file__).resolve().parent.parent


def _compile_file(rel_path: str):
    src = (ROOT / rel_path).read_text(encoding="utf-8")
    return AICodeCompiler(strict_mode=False).compile(src)


def _compile_source(src: str):
    return AICodeCompiler(strict_mode=False).compile(src)


def test_web_api_emit_capabilities():
    ir = _compile_file("examples/web/basic_web_api.ainl")
    caps = ir["emit_capabilities"]
    assert caps["needs_python_api"] is True
    assert caps["needs_cron"] is False
    assert caps["needs_scraper"] is False
    assert "python_api" in ir["required_emit_targets"]["minimal_emit"]


def test_crud_emit_capabilities():
    ir = _compile_file("examples/crud_api.ainl")
    caps = ir["emit_capabilities"]
    assert caps["needs_python_api"] is True
    assert ir["required_emit_targets"]["minimal_emit"] == ["python_api"]


def test_scraper_emit_capabilities():
    ir = _compile_file("examples/scraper/basic_scraper.ainl")
    caps = ir["emit_capabilities"]
    assert caps["needs_scraper"] is True
    assert caps["needs_cron"] is True
    assert ir["required_emit_targets"]["minimal_emit"] == ["scraper", "cron"]


def test_cron_monitor_emit_capabilities():
    ir = _compile_file("examples/cron/monitor_and_alert.ainl")
    caps = ir["emit_capabilities"]
    assert caps["needs_cron"] is True
    assert caps["needs_python_api"] is False
    assert ir["required_emit_targets"]["minimal_emit"] == ["cron"]


def test_rag_emit_capabilities():
    ir = _compile_file("examples/rag_pipeline.ainl")
    caps = ir["emit_capabilities"]
    assert caps["needs_python_api"] is True
    assert "python_api" in ir["required_emit_targets"]["minimal_emit"]


def test_openclaw_daily_digest_emit_capabilities():
    ir = _compile_file("examples/openclaw/daily_digest.lang")
    caps = ir["emit_capabilities"]
    assert caps["needs_cron"] is True
    assert "cron" in ir["required_emit_targets"]["minimal_emit"]


def test_mt5_emit_capabilities_from_runtime_steps():
    ir = _compile_source(
        "L1: R mt5.BUY EURUSD 1 ->x J x\n"
    )
    caps = ir["emit_capabilities"]
    assert caps["needs_mt5"] is True
    assert "mt5" in ir["required_emit_targets"]["minimal_emit"]


def test_core_cron_without_cr_entries_adds_minimal_python_api_fallback():
    ir = _compile_source(
        "S core cron\n"
        "L1:\n"
        "  J x\n"
    )
    assert ir["required_emit_targets"]["minimal_emit"] == ["cron", "python_api"]
    assert ir.get("emit_python_api_fallback_stub") is True
    stub = AICodeCompiler(strict_mode=False).emit_python_api(ir)
    assert "asyncio.run(main())" in stub
    assert "FastAPI" not in stub


def test_compact_prisma_react_emit_smoke_and_token_budget():
    """Compact prisma/react emit: valid shape + materially smaller than pre-compaction baselines."""
    c = AICodeCompiler(strict_mode=False)
    ir = c.compile("D User id:I name:S\nU Dash\nT rows:J\n")
    pr = c.emit_prisma_schema(ir)
    assert 'generator client' in pr and "model User" in pr and "Steven Hooley" in pr
    assert tiktoken_count(pr) < 55

    rx = c.emit_react(ir)
    assert "export const Dash" in rx and "useState" in rx and "Steven Hooley" in rx
    assert tiktoken_count(rx) < 85
