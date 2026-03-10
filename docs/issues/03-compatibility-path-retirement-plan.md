# Title

Define phased retirement plan for compatibility-only runtime/compiler paths

## Problem

Compatibility paths are intentionally retained, but retirement criteria/timeline are not yet formalized for maintainers and contributors.

## Why It Matters

- Reduces long-term maintenance overhead.
- Improves clarity on canonical execution path ownership.
- Prevents accidental feature work on compatibility-only surfaces.

## Acceptance Criteria

- Inventory compatibility-only paths (runtime wrappers, legacy IR paths, related docs).
- Define phase gates for retirement (usage signals, test coverage, docs updates).
- Add explicit "do not extend semantics here" guidance where applicable.
- Publish a short deprecation/retirement timeline in docs.

## Non-Goals

- Immediate removal of compatibility paths.
- Breaking historical imports without migration notes.
- Architecture rewrites unrelated to retirement clarity.
