import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import benchmark_size  # type: ignore


def test_benchmark_markdown_contains_interpretation_sections():
    report = {
        "metric": "approx_chunks",
        "headline_profile": "canonical_strict_valid",
        "modes": {
            "full_multitarget": {
                "profiles": [
                    {
                        "name": "canonical_strict_valid",
                        "summary": {
                            "artifact_count": 1,
                            "ainl_source_total": 10,
                            "aggregate_generated_output_total": 20,
                            "aggregate_ratio_vs_source": 2.0,
                        },
                        "size_drivers": {"top_targets": [], "top_artifacts": []},
                        "artifacts": [],
                    }
                ]
            },
            "minimal_emit": {
                "profiles": [
                    {
                        "name": "canonical_strict_valid",
                        "summary": {
                            "artifact_count": 1,
                            "ainl_source_total": 10,
                            "aggregate_generated_output_total": 10,
                            "aggregate_ratio_vs_source": 1.0,
                        },
                        "size_drivers": {"top_targets": [], "top_artifacts": []},
                        "artifacts": [],
                    }
                ]
            },
        },
    }
    manifest = {"profiles": {"canonical_strict_valid": {"description": "strict"}}}
    text = benchmark_size.render_markdown(report, manifest)
    required_sections = [
        "## How To Read These Results",
        "## Full Multitarget vs Minimal Emit",
        "## Why Some Ratios Got Worse After Truthfulness Fixes",
        "## What We Can Honestly Claim",
        "## What These Numbers Are Not",
        "## Size Drivers (Actionable Diagnosis)",
        "## Residual Overhead Audit (minimal_emit)",
        "## Including Legacy Artifacts",
    ]
    for section in required_sections:
        assert section in text
