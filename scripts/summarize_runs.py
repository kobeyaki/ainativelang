#!/usr/bin/env python3
"""
summarize_runs.py

Small helper to summarize one or more JSON payloads produced by
RuntimeEngine.run(..., trace=True) or equivalent saved outputs.

Input:
  - One or more file paths to JSON files.
  - Each file should contain either a single run payload object or a list
    of run payload objects.

Output (to stdout, as JSON):
  {
    "run_count": <int>,
    "ok_count": <int>,
    "error_count": <int>,
    "runtime_versions": [ ... ],
    "result_kinds": { "<type>": count, ... },
    "trace_op_counts": { "<op>": count, ... },
    "label_counts": { "<label>": count, ... },
    "timestamps_present": false
  }

Notes:
  - This script is tooling-only; it does not change any compiler or runtime
    semantics.
  - It only works with the existing RuntimeEngine.run trace payload shape and
    does not attempt to guess other artifact formats.
"""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _iter_runs_from_file(path: Path) -> Iterable[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        yield data
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
    else:
        # Unsupported top-level shape; ignore.
        return


def _summarize_runs(payloads: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    run_count = 0
    ok_count = 0
    error_count = 0
    runtime_versions: set[str] = set()
    result_kinds: Counter[str] = Counter()
    trace_op_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()

    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        run_count += 1

        ok = bool(payload.get("ok"))
        if ok:
            ok_count += 1
        else:
            error_count += 1

        rv = payload.get("runtime_version")
        if isinstance(rv, str):
            runtime_versions.add(rv)

        res = payload.get("result")
        result_kinds[type(res).__name__] += 1

        trace = payload.get("trace") or []
        if isinstance(trace, list):
            for event in trace:
                if not isinstance(event, dict):
                    continue
                op = event.get("op")
                if isinstance(op, str):
                    trace_op_counts[op] += 1
                label = event.get("label")
                if label is not None:
                    label_counts[str(label)] += 1

    summary: Dict[str, Any] = {
        "run_count": run_count,
        "ok_count": ok_count,
        "error_count": error_count,
        "runtime_versions": sorted(runtime_versions),
        "result_kinds": dict(result_kinds),
        "trace_op_counts": dict(trace_op_counts),
        "label_counts": dict(label_counts),
        # Current RuntimeEngine.run payloads do not include timestamps, so we
        # explicitly report that freshness cannot be computed here.
        "timestamps_present": False,
    }
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Summarize one or more RuntimeEngine.run(..., trace=True) payloads."
    )
    ap.add_argument(
        "files",
        nargs="+",
        help="Path(s) to JSON file(s) containing run payload(s).",
    )
    args = ap.parse_args()

    all_runs: List[Dict[str, Any]] = []
    for fname in args.files:
        path = Path(fname)
        if not path.is_file():
            continue
        all_runs.extend(list(_iter_runs_from_file(path)))

    summary = _summarize_runs(all_runs)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
