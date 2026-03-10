import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler


def _warning_diags(code: str):
    ir = AICodeCompiler(strict_mode=False).compile(code, emit_graph=True)
    assert not ir.get("errors"), ir.get("errors")
    return [d for d in (ir.get("diagnostics") or []) if d.get("severity") == "warning"]


def test_canonical_lint_warns_on_inline_label_content():
    diags = _warning_diags("L1: Set flag true If flag ->L2 ->L3\nL2: J flag\nL3: J flag\n")
    codes = {d.get("code") for d in diags}
    assert "AINL_CANONICAL_INLINE_LABEL" in codes
    assert any(d.get("lineno") == 1 for d in diags if d.get("code") == "AINL_CANONICAL_INLINE_LABEL")


def test_canonical_lint_warns_on_split_token_r_form():
    diags = _warning_diags("L1:\n  R db F User * ->users\n  J users\n")
    assert any(d.get("code") == "AINL_CANONICAL_R_SPLIT_FORM" for d in diags), diags


def test_canonical_lint_warns_on_missing_call_out_and_lowercase_verb():
    diags = _warning_diags("L1:\n  Call L2\n  J _call_result\nL2:\n  R core.add 1 1 ->v\n  J v\n")
    codes = {d.get("code") for d in diags}
    assert "AINL_CANONICAL_CALL_EXPLICIT_OUT" in codes
    assert "AINL_CANONICAL_LOWERCASE_VERB" in codes


def test_canonical_lint_warns_on_compatible_ops():
    diags = _warning_diags("L1:\n  X total add 1 2\n  J total\n")
    assert any(d.get("code") == "AINL_CANONICAL_COMPAT_OP" for d in diags), diags
