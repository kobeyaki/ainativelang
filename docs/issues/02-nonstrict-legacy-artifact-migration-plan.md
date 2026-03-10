# Title

Plan and execute migration of non-strict/legacy artifacts toward strict-valid coverage

## Problem

The repository intentionally includes `non-strict-only` and `legacy-compat` artifacts. Without an explicit migration plan, these can stagnate and blur canonical language expectations for new contributors.

## Why It Matters

- Keeps public examples trustworthy as canonical references.
- Increases strict conformance confidence over time.
- Prevents silent drift between docs and artifact behavior.

## Acceptance Criteria

- Produce a prioritized migration list from `tooling/artifact_profiles.json`.
- For top-priority artifacts, either:
  - migrate to strict-valid and update profile/tests, or
  - document explicit rationale for continued non-strict/legacy status.
- Keep `tests/test_artifact_profiles.py` green throughout migration.

## Non-Goals

- Forcing all artifacts strict-valid in one release.
- Relaxing strict mode to make migration easier.
- Changing runtime/compiler semantics solely to preserve old examples.
