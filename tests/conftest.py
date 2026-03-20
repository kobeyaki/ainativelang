from __future__ import annotations

from pathlib import Path


def pytest_collection_modifyitems(config, items):
    """
    Auto-mark slower/runtime-heavy suites as integration so default profile
    (`not integration and not emits and not lsp`) stays stable.
    """
    integration_name_prefixes = (
        "test_runtime_",
        "test_runner_service",
        "test_replay_determinism",
        "test_capability_contracts",
    )
    integration_exact = {
        "test_conformance.py",
        "test_lossless.py",
    }

    for item in items:
        p = Path(str(item.fspath))
        name = p.name
        # Property tests and runtime-heavy suites are integration profile.
        if "tests/property/" in str(p).replace("\\", "/"):
            item.add_marker("integration")
            continue
        if name in integration_exact or name.startswith(integration_name_prefixes):
            item.add_marker("integration")
