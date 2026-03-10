AINL `v1.1.0` marks the first public GitHub release of the project as an open-core baseline.

The focus of this release is not flashy expansion. It is architectural clarity. The repository now makes explicit which surfaces are canonical and compiler-owned, which runtime paths are compatibility-only, how formal grammar and constrained decoding are separated from non-authoritative priors, and which artifacts are strict-valid versus intentionally non-strict.

A few concrete outcomes:

* compiler semantics and strict validation remain compiler-owned
* runtime execution ownership is centered in `runtime/engine.py`
* grammar admissibility is separated from decoder UX priors
* strict adapter contracts are explicit allowlist/effect metadata, not fuzzy heuristics
* artifact classification is machine-readable and enforced in CI

This should make the repo more trustworthy for outside contributors: fewer hidden assumptions, clearer compatibility boundaries, and less ambiguity about what counts as canonical behavior versus legacy support.

If you are evaluating or contributing, start with the README, then the RC checklist in CONTRIBUTING, and then the release/readiness docs for the current project boundaries.
