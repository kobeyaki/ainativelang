import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union


JsonObject = Dict[str, Any]


@dataclass
class ValidationIssue:
    kind: str  # "error" or "warning"
    path: str  # human-readable path hint (e.g. "task_id", "output.actions[0].status")
    message: str


def _require_field(
    obj: JsonObject,
    field: str,
    expected_type: Union[type, Tuple[type, ...]],
    issues: List[ValidationIssue],
    kind: str = "error",
) -> None:
    if field not in obj:
        issues.append(
            ValidationIssue(
                kind=kind,
                path=field,
                message=f"Missing required field '{field}'.",
            )
        )
        return
    value = obj[field]
    if not isinstance(value, expected_type):
        issues.append(
            ValidationIssue(
                kind=kind,
                path=field,
                message=f"Field '{field}' expected type {expected_type}, got {type(value).__name__}.",
            )
        )


def validate_agent_task_request(obj: Any) -> List[ValidationIssue]:
    """
    Validate an AgentTaskRequest-like envelope according to the minimal
    upstream contract documented in docs/AGENT_COORDINATION_CONTRACT.md.
    """
    issues: List[ValidationIssue] = []

    if not isinstance(obj, dict):
        issues.append(
            ValidationIssue(
                kind="error",
                path="",
                message=f"Task envelope must be a JSON object, got {type(obj).__name__}.",
            )
        )
        return issues

    # Required top-level fields (minimal contract)
    _require_field(obj, "schema_version", str, issues)
    _require_field(obj, "task_id", str, issues)
    _require_field(obj, "requester_id", str, issues)
    _require_field(obj, "target_agent", str, issues)
    _require_field(obj, "target_role", str, issues)
    _require_field(obj, "task_type", str, issues)
    _require_field(obj, "description", str, issues)
    _require_field(obj, "input", dict, issues)

    # Input payload/refs shape
    input_val = obj.get("input")
    if isinstance(input_val, dict):
        if "refs" in input_val and not isinstance(input_val["refs"], list):
            issues.append(
                ValidationIssue(
                    kind="error",
                    path="input.refs",
                    message="Field 'input.refs' must be a list when present.",
                )
            )
        if "payload" not in input_val:
            issues.append(
                ValidationIssue(
                    kind="warning",
                    path="input.payload",
                    message="Field 'input.payload' is missing; envelope is valid but payload will be empty.",
                )
            )

    # Optional fields with soft type checks
    if "required_output_contract" in obj and not isinstance(
        obj["required_output_contract"], dict
    ):
        issues.append(
            ValidationIssue(
                kind="error",
                path="required_output_contract",
                message="Field 'required_output_contract' must be an object when present.",
            )
        )

    if "budget_limit" in obj and not isinstance(obj["budget_limit"], dict):
        issues.append(
            ValidationIssue(
                kind="warning",
                path="budget_limit",
                message="Field 'budget_limit' is expected to be an object (tokens/usd_cents).",
            )
        )

    if "allowed_tools" in obj and not isinstance(obj["allowed_tools"], list):
        issues.append(
            ValidationIssue(
                kind="warning",
                path="allowed_tools",
                message="Field 'allowed_tools' should be a list of tool identifiers.",
            )
        )

    return issues


def validate_agent_task_result(obj: Any) -> List[ValidationIssue]:
    """
    Validate an AgentTaskResult-like envelope according to the minimal
    upstream contract documented in docs/AGENT_COORDINATION_CONTRACT.md.
    """
    issues: List[ValidationIssue] = []

    if not isinstance(obj, dict):
        issues.append(
            ValidationIssue(
                kind="error",
                path="",
                message=f"Result envelope must be a JSON object, got {type(obj).__name__}.",
            )
        )
        return issues

    _require_field(obj, "schema_version", str, issues)
    _require_field(obj, "task_id", str, issues)
    _require_field(obj, "agent_id", str, issues)
    _require_field(obj, "status", str, issues)
    _require_field(obj, "output", dict, issues)

    output = obj.get("output")
    if isinstance(output, dict):
        _require_field(output, "summary", str, issues)
        if "actions" in output and not isinstance(output["actions"], list):
            issues.append(
                ValidationIssue(
                    kind="error",
                    path="output.actions",
                    message="Field 'output.actions' must be a list when present.",
                )
            )
        if isinstance(output.get("actions"), list):
            for idx, action in enumerate(output["actions"]):
                if not isinstance(action, dict):
                    issues.append(
                        ValidationIssue(
                            kind="error",
                            path=f"output.actions[{idx}]",
                            message="Each action must be an object.",
                        )
                    )
                    continue
                _require_field(action, "kind", str, issues)
                _require_field(action, "description", str, issues)
                _require_field(action, "status", str, issues)

    return issues


def _iter_jsonl(path: Path) -> Iterable[Tuple[int, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield idx, json.loads(line)
            except json.JSONDecodeError as e:
                yield idx, e


def lint_tasks_file(path: Path) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for lineno, obj in _iter_jsonl(path):
        if isinstance(obj, json.JSONDecodeError):
            issues.append(
                ValidationIssue(
                    kind="error",
                    path=f"{path}:{lineno}",
                    message=f"Invalid JSON line: {obj}",
                )
            )
            continue
        for issue in validate_agent_task_request(obj):
            issues.append(
                ValidationIssue(
                    kind=issue.kind,
                    path=f"{path}:{lineno}:{issue.path}",
                    message=issue.message,
                )
            )
    return issues


def lint_task_file(path: Path) -> List[ValidationIssue]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    return validate_agent_task_request(obj)


def lint_result_file(path: Path) -> List[ValidationIssue]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    return validate_agent_task_result(obj)


def _format_issues(issues: List[ValidationIssue]) -> str:
    lines: List[str] = []
    for issue in issues:
        prefix = "ERROR" if issue.kind == "error" else "WARN"
        location = issue.path or "<root>"
        lines.append(f"{prefix} [{location}]: {issue.message}")
    return "\n".join(lines)


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate coordination mailbox envelopes (AgentTaskRequest JSONL/JSON "
            "and AgentTaskResult JSON) against the upstream coordination contract."
        )
    )
    parser.add_argument(
        "--tasks-jsonl",
        type=str,
        help="Path to a JSONL file of AgentTaskRequest envelopes.",
    )
    parser.add_argument(
        "--task-json",
        type=str,
        help="Path to a single AgentTaskRequest JSON file.",
    )
    parser.add_argument(
        "--result-json",
        type=str,
        help="Path to a single AgentTaskResult JSON file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary instead of human-readable text.",
    )

    args = parser.parse_args(argv)

    all_issues: List[ValidationIssue] = []

    if args.tasks_jsonl:
        all_issues.extend(lint_tasks_file(Path(args.tasks_jsonl)))

    if args.task_json:
        for issue in lint_task_file(Path(args.task_json)):
            issue.path = f"{args.task_json}:{issue.path}"
            all_issues.append(issue)

    if args.result_json:
        for issue in lint_result_file(Path(args.result_json)):
            issue.path = f"{args.result_json}:{issue.path}"
            all_issues.append(issue)

    if args.json:
        payload = {
            "ok": not any(i.kind == "error" for i in all_issues),
            "issues": [asdict(i) for i in all_issues],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if not all_issues:
            print("All checked envelopes are valid according to the upstream coordination schema.")
        else:
            print(_format_issues(all_issues))

    return 1 if any(i.kind == "error" for i in all_issues) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

