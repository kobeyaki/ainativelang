from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from compiler_v2 import AICodeCompiler  # noqa: E402


@pytest.fixture
def compiler_lossless() -> AICodeCompiler:
    """Lossless compile path for tokenizer round-trip tests.

    We intentionally keep strict mode disabled so the suite can safely tokenize/parse
    even inputs that would fail strict validation later.
    """

    return AICodeCompiler(strict_mode=False)


def pytest_configure(config) -> None:
    """Place syrupy snapshots under ``tests/snapshots/conformance``."""
    # syrupy uses this option to choose the snapshot directory name relative to each
    # test file's directory, so we use a path that resolves to:
    #   tests/conformance/../snapshots/conformance -> tests/snapshots/conformance
    if hasattr(config.option, "snapshot_dirname"):
        config.option.snapshot_dirname = "../snapshots/conformance"


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

