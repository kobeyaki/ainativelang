import hashlib
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_inline_if_with_missing_then_target_does_not_crash():
    c = AICodeCompiler(strict_mode=True)
    code = "L1: If cond\nL2: J ok\n"
    ir = c.compile(code)
    assert isinstance(ir, dict)
    assert "labels" in ir


@pytest.mark.parametrize(
    "code,expected_substring",
    [
        ("htp.Get /x ->out\n", "unknown module"),
        ("If cond ->L1 ->L2\n", "label-only op"),
        ("S core web /api\nE /x G\n", "requires at least"),
        ("L1: J a\nD User id:I\n", "auto-closed label"),
    ],
)
def test_diagnostic_classifier_substrings_remain_present(code: str, expected_substring: str):
    c = AICodeCompiler(strict_mode=True)
    ir = c.compile(code)
    joined = "\n".join(ir.get("errors", []))
    assert expected_substring in joined


@pytest.mark.parametrize(
    "name,code,expected",
    [
        (
            "arith_endpoint",
            "S core web /api\nE /sum G ->L1 ->out\nL1: X out add 2 3 J out\n",
            {
                "labels_sha256": "ef566311fa33b4f2641b832464d8e31d527796d4fd9111ba23650bbe03e10191",
                "graph_semantic_checksum": "sha256:6c2054b0040775d99d41bd8070e338bf2d4cf7d6b40f4ce13f4497b6b41053a3",
                "emit_ir_json_sha256": "d683ae1db74df671f2ac86b10a355df60bbb48c49e3cbe2a326ab700d1b7293b",
                "emit_openapi_sha256": "da94673422c765dc848bf34f99a3197ff326418d3c930631320b6cb69a9af547",
                "emit_server_sha256": "7ef87a29711800176ff33e252ec7e3e27b239575b8bac7d4b9d58e3f7088488a",
                "emit_react_sha256": "445caf103f4e83486813e7df9d1c19492570c80978ab88c439d55552feb68e2b",
            },
        ),
        (
            "inline_if_flow",
            "S core web /api\nE /flow G ->L1 ->out\nL1: Set cond true If cond ->L2 ->L3\nL2: Set out pass J out\nL3: Set out fail J out\n",
            {
                "labels_sha256": "63aaf5c65678a1ca7966a3b2f51b872f3e071155691d76546b15546d72e24a11",
                "graph_semantic_checksum": "sha256:03597e2e690a15964074adb1fcdf52b0f323fd47267fc493b69bb610277f111e",
                "emit_ir_json_sha256": "636da282ac1accf856e3a78ef70b56f10ca8ba81fc5b7524f2a8f42690ce4f2d",
                "emit_openapi_sha256": "23c32ff2a1ea80dc8c74d5b8bb73f48c627adb820f61c5e871e9034cdd3e2f99",
                "emit_server_sha256": "55f4495330c24eab3b833ab0368a120e4366a2c730b233b9c55f55253a2d60a6",
                "emit_react_sha256": "445caf103f4e83486813e7df9d1c19492570c80978ab88c439d55552feb68e2b",
            },
        ),
    ],
)
def test_patch_a_valid_artifacts_fingerprint_lock(name: str, code: str, expected: dict):
    c = AICodeCompiler(strict_mode=False)
    ir = c.compile(code)
    assert not ir.get("errors"), f"{name} compile errors: {ir.get('errors')}"

    labels_json = json.dumps(ir.get("labels", {}), sort_keys=True, separators=(",", ":"))
    actual = {
        "labels_sha256": _sha256(labels_json),
        "graph_semantic_checksum": ir.get("graph_semantic_checksum"),
        "emit_ir_json_sha256": _sha256(c.emit_ir_json(ir)),
        "emit_openapi_sha256": _sha256(c.emit_openapi(ir)),
        "emit_server_sha256": _sha256(c.emit_server(ir)),
        "emit_react_sha256": _sha256(c.emit_react(ir)),
    }
    assert actual == expected


@pytest.mark.parametrize(
    "if_tail",
    [
        "c ->L2",
        "c ->L2 ->L3",
        "c L2 L3",
        "c ->L2 L3:",
        "c L2 ->L3",
        "c L2 3",
    ],
)
def test_if_step_shape_parity_inline_vs_standalone(if_tail: str):
    c_inline = AICodeCompiler()
    ir_inline = c_inline.compile(f"L1: If {if_tail}\nL2: J ok\nL3: J err\n")
    step_inline = ir_inline["labels"]["1"]["legacy"]["steps"][0]

    c_standalone = AICodeCompiler()
    ir_standalone = c_standalone.compile(f"L1:\nIf {if_tail}\nL2: J ok\nL3: J err\n")
    step_standalone = ir_standalone["labels"]["1"]["legacy"]["steps"][0]

    assert step_inline["op"] == "If"
    assert step_standalone["op"] == "If"
    assert step_inline["then"] == step_standalone["then"]
    assert step_inline["else"] == step_standalone["else"]
