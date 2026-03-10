import ast
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.emits
@pytest.mark.integration
def test_emitted_python_artifacts_parse():
    """
    Emitter outputs under tests/emits include filenames with extra dots
    (e.g. test_rag.api.py). We validate them as source artifacts by parsing
    file contents directly, avoiding module-name import issues.
    """
    root = Path(__file__).resolve().parent / "emits"
    py_files = sorted(p for p in root.rglob("*.py") if p.is_file())
    assert py_files, "expected emitted python artifacts under tests/emits"

    bad = []
    for f in py_files:
        try:
            ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except Exception as e:
            bad.append((str(f), str(e)))

    assert not bad, f"invalid emitted artifacts: {bad}"

