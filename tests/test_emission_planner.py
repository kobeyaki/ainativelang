from pathlib import Path

from tooling.emission_planner import TARGET_ORDER, required_emit_targets


def _manifest() -> dict:
    return {
        "modes": {
            "minimal_emit": {
                "relevance_rules": {
                    "react_ts": {"requires_capability": "needs_react_ts"},
                    "python_api": {"requires_capability": "needs_python_api"},
                    "prisma": {"requires_capability": "needs_prisma"},
                    "cron": {"requires_capability": "needs_cron"},
                    "scraper": {"requires_capability": "needs_scraper"},
                    "mt5": {"requires_capability": "needs_mt5"},
                },
                "fallback_targets": ["python_api"],
            }
        }
    }


def test_required_targets_api_only():
    ir = {
        "emit_capabilities": {
            "needs_react_ts": False,
            "needs_python_api": True,
            "needs_prisma": False,
            "needs_mt5": False,
            "needs_scraper": False,
            "needs_cron": False,
        }
    }
    got = required_emit_targets("L1: R http.GET \"/x\" ->res J res", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    assert got == ["python_api"]


def test_required_targets_frontend_and_types():
    ir = {
        "emit_capabilities": {
            "needs_react_ts": True,
            "needs_python_api": True,
            "needs_prisma": True,
            "needs_mt5": False,
            "needs_scraper": False,
            "needs_cron": False,
        }
    }
    got = required_emit_targets("Type User id int", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    assert got == ["react_ts", "python_api", "prisma"]


def test_required_targets_cron():
    ir = {
        "emit_capabilities": {
            "needs_react_ts": False,
            "needs_python_api": False,
            "needs_prisma": False,
            "needs_mt5": False,
            "needs_scraper": False,
            "needs_cron": True,
        },
        "crons": [{"label": "L1", "expr": "0 * * * *"}],
    }
    got = required_emit_targets("Cron every(1h) ->L1", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    assert got == ["cron"]


def test_required_targets_scraper_and_mt5_from_compiler_metadata():
    ir = {
        "emit_capabilities": {
            "needs_react_ts": False,
            "needs_python_api": False,
            "needs_prisma": False,
            "needs_mt5": True,
            "needs_scraper": True,
            "needs_cron": False,
        }
    }
    got = required_emit_targets("irrelevant source text", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    assert got == ["mt5", "scraper"]


def test_required_targets_deterministic_and_subset_of_full():
    ir = {"required_emit_targets": {"minimal_emit": ["python_api"], "full_multitarget": TARGET_ORDER}}
    first = required_emit_targets("hello", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    second = required_emit_targets("hello", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    assert first == second
    assert set(first).issubset(set(TARGET_ORDER))


def test_required_targets_prefers_required_targets_field_over_heuristics():
    ir = {
        "required_emit_targets": {"minimal_emit": ["cron"], "full_multitarget": TARGET_ORDER},
        "emit_capabilities": {
            "needs_react_ts": True,
            "needs_python_api": True,
            "needs_prisma": True,
            "needs_mt5": True,
            "needs_scraper": True,
            "needs_cron": True,
        },
    }
    got = required_emit_targets("source that could match everything", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    assert got == ["cron", "python_api"]
    assert ir.get("emit_python_api_fallback_stub") is True


def test_minimal_emit_stub_when_cron_scheduled_but_no_cron_entries():
    ir = {
        "emit_capabilities": {
            "needs_react_ts": False,
            "needs_python_api": False,
            "needs_prisma": False,
            "needs_mt5": False,
            "needs_scraper": False,
            "needs_cron": True,
        },
        "crons": [],
        "required_emit_targets": {"minimal_emit": ["cron"], "full_multitarget": TARGET_ORDER},
    }
    got = required_emit_targets("x", ir, mode="minimal_emit", benchmark_manifest=_manifest())
    assert got == ["cron", "python_api"]
    assert ir.get("emit_python_api_fallback_stub") is True


def test_full_multitarget_includes_every_target():
    ir = {"services": {}, "types": {}, "crons": []}
    got = required_emit_targets("hello", ir, mode="full_multitarget", benchmark_manifest=_manifest())
    assert got == TARGET_ORDER
