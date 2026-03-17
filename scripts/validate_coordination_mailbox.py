#!/usr/bin/env python3
"""
Extension-only CLI for validating coordination mailbox envelopes.

This script checks AgentTaskRequest and AgentTaskResult JSON/JSONL payloads
against the minimal upstream coordination contract documented in
`docs/advanced/AGENT_COORDINATION_CONTRACT.md`.

It does not change compiler/runtime semantics and is intended as a governance
and compatibility tool for advanced coordination usage.
"""

from tooling.coordination_validator import main


if __name__ == "__main__":
    raise SystemExit(main())

