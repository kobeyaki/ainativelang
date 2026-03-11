# AINL v1.1.0 — First Public GitHub Release (Open-Core Baseline)

This is the first public GitHub release of **AINL** as an open-core baseline.

This release focuses on **clarity, trust, and explicit boundaries** more than feature expansion. The repository now makes a clear distinction between canonical compiler-owned behavior, compatibility paths, and intentionally non-strict artifacts used for migration, examples, or legacy workflows.

## Highlights

* Compiler, runtime, grammar, and strict adapter ownership boundaries are now explicitly documented and reflected in tests.
* Strict vs non-strict artifacts are machine-classified and validated in CI.
* Public contributor onboarding has been tightened across README, CONTRIBUTING, support/security docs, templates, and release docs.
* Compatibility paths remain intentional and documented; no hidden semantic widening was introduced for release convenience.

## Canonical Surfaces In This Release

These are the primary source-of-truth surfaces in the current architecture:

* **Compiler semantics and strict validation:** `compiler_v2.py`
* **Runtime execution ownership:** `runtime/engine.py`
* **Runtime compatibility wrapper only:** `runtime.py`, `runtime/compat.py`
* **Formal grammar orchestration:** `compiler_grammar.py`
* **Strict adapter contract allowlist/effect ownership:** `tooling/effect_analysis.py`
* **Artifact strictness classification ownership:** `tooling/artifact_profiles.json`

## Compatibility and Non-Strict Policy

AINL currently ships with explicit compatibility and non-strict surfaces. These are intentional.

* `ExecutionEngine` remains available as a compatibility API for historical imports.
* `legacy.steps` remains supported as compatibility IR.
* Compatibility and non-strict artifacts are explicitly classified rather than treated as accidental drift.
* `examples/golden/*.ainl` are compatibility-focused examples and are **not** strict conformance targets.

Source of truth:

* `tooling/artifact_profiles.json`
* `tests/test_artifact_profiles.py`

## Contributor Experience Improvements

This release also tightens the public repo surface for first-time external contributors:

* clearer README boundaries and entrypoints
* concrete pre-PR validation commands in `CONTRIBUTING.md`
* release/readiness/runbook docs for maintainers
* support/security/governance docs that are GitHub-safe and truthful
* issue / PR templates aligned with artifact-profile awareness

## CI and Validation

CI and release verification now explicitly include:

* core test profile execution
* artifact strict/non-strict verification
* docs contract checks
* compatibility-focused parser/OpenAPI gates
* profile-aware validation for release-facing examples and fixtures

### Advanced coordination (extension / OpenClaw, experimental)

This release also includes a **local, file-backed coordination substrate** and
OpenClaw-oriented examples. These features are:

- **extension-only and noncanonical** — implemented via the `agent` adapter and
  OpenClaw extension adapters (`extras`, `svc`, `tiktok`, etc.),
- **advanced / operator-only** — intended for operators and advanced users who
  understand the risks and have their own safety, approval, and policy layers,
- **advisory and local-first** — built around local mailbox-style files under
  `AINL_AGENT_ROOT`, with advisory `AgentTaskRequest` / `AgentTaskResult`
  envelopes, and no built-in routing, authentication, or encryption.

These coordination features are **not**:

- a built-in secure multi-tenant messaging fabric,
- a general-purpose orchestration engine,
- a swarm/multi-agent safety layer,
- or a policy/approval enforcement system.

Upstream provides:

- the minimal coordination contract in `docs/AGENT_COORDINATION_CONTRACT.md`,
- explicit safe-use and threat-model guidance in `docs/SAFE_USE_AND_THREAT_MODEL.md`,
- a coordination baseline and mailbox validator
  (`tooling/coordination_validator.py`, `scripts/validate_coordination_mailbox.py`)
  so advanced users can check that envelopes remain on upstream rails.

Operators who choose to use these features are responsible for:

- routing, retries, and scheduling,
- authentication and authorization,
- encryption and transport security,
- human approvals, policy enforcement, and production safety.

## Known Non-Blocking Follow-Ups

* some compatibility and legacy surfaces remain intentionally non-strict
* FastAPI `on_event` deprecation warnings still appear in some test paths
* structured diagnostics can continue improving as a first-class compiler contract
* compatibility retirement remains future roadmap work, not part of this release

## Recommended Next Priorities

See:

* `docs/POST_RELEASE_ROADMAP.md`
* `docs/issues/README.md`

## Project Entry Points

* Project overview: `README.md`
* Contributor guide: `CONTRIBUTING.md`
* Release readiness: `docs/RELEASE_READINESS.md`
* Release operations: `docs/RELEASING.md`
* Conformance details: `docs/CONFORMANCE.md`
