from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "docs" / "runtime" / "SAFE_OPTIMIZATION_POLICY.md"


def test_safe_optimization_policy_exists_and_has_required_sections():
    assert POLICY.exists(), "missing docs/runtime/SAFE_OPTIMIZATION_POLICY.md"
    text = POLICY.read_text(encoding="utf-8")
    required_headers = [
        "## Optimization Rule",
        "## Safe / Recommended Now",
        "## Safe But Requires Design Discipline",
        "## Dangerous / Avoid For Now",
        "## Small-Model Impact",
        "## Required Acceptance Test For Language-Surface Changes",
        "## Recommended Order Of Implementation",
        "## Before Optimizing AINL Source Syntax",
        "## Benchmark Interpretation Note",
    ]
    for header in required_headers:
        assert header in text, f"missing policy section: {header}"
