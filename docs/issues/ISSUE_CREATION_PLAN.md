# Post-v1.1.0 Issue Creation Plan

Suggested milestone/grouping for all items below: `Post-v1.1.0`

## 1) Structured diagnostics as first-class compiler contract

- Recommended title: `Compiler: Make structured diagnostics the default first-class contract`
- Suggested labels: `release-followup`, `compiler`, `diagnostics`, `langserver`, `strict-mode`
- Dependency ordering: none (start here)
- Classification: immediate post-release

## 2) Non-strict / legacy artifact migration plan

- Recommended title: `Artifacts: Prioritized migration plan for non-strict and legacy profiles`
- Suggested labels: `release-followup`, `docs`, `strict-mode`, `compatibility`
- Dependency ordering: after #1 preferred (better diagnostics support migration work)
- Classification: immediate post-release

## 3) Compatibility path retirement plan

- Recommended title: `Runtime/Compiler: Define phased compatibility-path retirement plan`
- Suggested labels: `release-followup`, `runtime`, `compiler`, `compatibility`
- Dependency ordering: after #2 preferred
- Classification: near-term cleanup

## 4) Strict adapter contract expansion policy

- Recommended title: `Strict mode: Formalize adapter allowlist expansion policy`
- Suggested labels: `release-followup`, `compiler`, `strict-mode`, `compatibility`
- Dependency ordering: parallel-capable, but after #1 preferred
- Classification: near-term cleanup

## 5) Post-release docs onboarding tightening

- Recommended title: `Docs: Tighten onboarding from first external contributor feedback`
- Suggested labels: `release-followup`, `docs`
- Dependency ordering: none (continuous)
- Classification: immediate post-release
