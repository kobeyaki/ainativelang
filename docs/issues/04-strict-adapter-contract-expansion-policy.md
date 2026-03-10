# Title

Formalize strict adapter contract expansion policy for newly supported runtime adapters

## Problem

Strict adapter allowlist growth must stay aligned with runtime-supported behavior. Expansion criteria are currently implied by code and tests but not fully standardized as contributor workflow policy.

## Why It Matters

- Prevents strict contract drift or speculative allowlist widening.
- Keeps strict mode trustworthy for external users.
- Makes adapter additions reviewable and reproducible.

## Acceptance Criteria

- Document explicit checklist for adding strict-valid adapter.verb entries.
- Require evidence of runtime support + contract tests before allowlisting.
- Require updates to:
  - `tooling/effect_analysis.py`
  - `tooling/adapter_manifest.json` (if applicable)
  - strict adapter tests
  - related docs.

## Non-Goals

- Broad wildcard allowlists.
- Adding non-runtime-supported adapter verbs.
- Relaxing strict contract enforcement for convenience.
