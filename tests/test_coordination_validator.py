import json
from pathlib import Path

import tooling.coordination_validator as cv


FIXTURES_DIR = Path(__file__).parent.parent / "examples" / "openclaw"


def test_valid_agent_task_request_from_example():
    path = FIXTURES_DIR / "token_cost_advice_request.lang"
    # This is a .lang file, not JSON; construct a minimal envelope matching the example.
    envelope = {
        "schema_version": "1.0",
        "task_id": "token-cost-advice-20260309",
        "requester_id": "openclaw.token_cost_tracker",
        "target_agent": "cursor.advisor",
        "target_role": "advisor",
        "task_type": "advisory_token_cost_review",
        "description": "Review daily token cost and suggest safe model/usage optimizations.",
        "input": {
            "refs": [],
            "payload": {
                "date": "2026-03-09",
                "total_cost_usd": 12.34,
            },
        },
    }
    issues = cv.validate_agent_task_request(envelope)
    assert not any(i.kind == "error" for i in issues)


def test_valid_agent_task_result_fixture():
    path = FIXTURES_DIR / "demo-openclaw-monitor-001.result.json"
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    issues = cv.validate_agent_task_result(obj)
    assert not any(i.kind == "error" for i in issues)


def test_missing_required_fields_fail_for_task():
    bad = {
        "schema_version": "1.0",
        # missing task_id, requester_id, target_agent, etc.
        "input": {"refs": [], "payload": {}},
    }
    issues = cv.validate_agent_task_request(bad)
    kinds = {i.path for i in issues}
    assert "task_id" in kinds
    assert "requester_id" in kinds
    assert any(i.kind == "error" for i in issues)


def test_non_object_result_fails():
    issues = cv.validate_agent_task_result(["not", "an", "object"])
    assert any(i.kind == "error" for i in issues)


def test_jsonl_linter_reports_line_numbers(tmp_path):
    jsonl_path = tmp_path / "tasks.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        f.write('{"schema_version": "1.0", "task_id": "ok", "requester_id": "r", "target_agent": "a", "target_role": "role", "task_type": "t", "description": "d", "input": {"refs": [], "payload": {}}}\n')
        f.write('{"schema_version": "1.0", "input": {}}\n')  # missing many fields

    issues = cv.lint_tasks_file(jsonl_path)
    # We expect at least one error tied to the second line.
    assert any("tasks.jsonl:2" in i.path and i.kind == "error" for i in issues)

