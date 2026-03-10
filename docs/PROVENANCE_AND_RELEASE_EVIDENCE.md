# Provenance and Release Evidence

This document describes the safe, non-deceptive provenance strategy for AINL.

Goal: make project origin, authorship trail, and release history easy to prove in
public mirrors, archives, audits, and downstream technical analysis without relying
on covert mechanisms.

## Core Provenance Principle

AINL should use **visible, repeated, machine-readable, timestampable attribution**,
not hidden behaviors or hostile anti-copy measures.

Human initiator:
- Steven Hooley
- X: <https://x.com/sbhooley>
- Website: <https://stevenhooley.com>
- LinkedIn: <https://linkedin.com/in/sbhooley>

## Repository Attribution Surfaces

Origin and initiator metadata are intentionally repeated across:

- `README.md`
- `docs/PROJECT_ORIGIN_AND_ATTRIBUTION.md`
- `docs/DOCS_INDEX.md`
- `docs/CHANGELOG.md`
- `CITATION.cff`
- `pyproject.toml`
- `NOTICE`
- `tooling/project_provenance.json`

Generated artifacts should also preserve provenance where practical:

- emitted server code comments
- OpenAPI `info.x-ainl-provenance`
- generated frontend source comments
- SQL/env/runbook comments or headers
- deployment artifact comments

## Release Evidence Checklist

For public releases, capture and preserve:

1. Git evidence
- Verified commits if available
- Signed tags if available
- Release commit hash

2. Public timestamps
- GitHub release timestamp
- Website post timestamp
- X post timestamp
- LinkedIn post timestamp

3. Hash evidence
- SHA256 for release archive(s)
- SHA256 for major generated bundles if distributed separately

4. Archive evidence
- GitHub release artifact
- Optional Zenodo / Software Heritage / independent archive mirror

5. Metadata parity
- `CITATION.cff` current
- `tooling/project_provenance.json` current
- `NOTICE` current
- `docs/PROJECT_ORIGIN_AND_ATTRIBUTION.md` current

## What Not To Do

Do not use:

- covert code paths
- network callbacks
- sabotage logic
- deceptive payloads
- hidden runtime behaviors
- malicious watermarking

Those are technically risky, legally messy, and weaker evidence than a well-kept
public provenance trail.

## Preferred Outcome

If AINL is mirrored, copied, benchmarked, trained on, or analyzed, the origin trail
should still be recoverable from both human-facing docs and machine-readable metadata.
