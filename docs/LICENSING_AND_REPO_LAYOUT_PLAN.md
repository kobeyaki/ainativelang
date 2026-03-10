# Licensing and Repo Layout Plan (Option C Draft)

This plan translates the open-core strategy into concrete repository files and
publication steps.

> Planning document only. Review with legal counsel before finalizing.

## Recommended File Set

At repository root:

- `LICENSE` (open-core code license text)
- `COMMERCIAL_LICENSE.md` (how to obtain commercial terms)
- `MODEL_LICENSE.md` (weights/checkpoints/data-model usage terms)
- `TRADEMARKS.md` (name/logo/compatibility mark usage policy)
- `CONTRIBUTING.md` (already present)
- `SECURITY.md` (already present)
- `CODE_OF_CONDUCT.md` (already present)
- `CITATION.cff` (already present)

In docs:

- `docs/OPEN_CORE_CHARTER.md`
- `docs/OPEN_CORE_BOUNDARY_MAP.md`
- `docs/GITHUB_RELEASE_CHECKLIST.md`

## Publication Wording Requirements

README should clearly state:

1. open-core model
2. what is open and where defined
3. commercial use path and contact channel
4. trademark and compatibility mark policy link

## Licensing Decision Checklist

Before selecting license text:

- Confirm open-core code license family
- Confirm contribution IP policy (CLA vs DCO)
- Confirm patent stance (if applicable)
- Confirm model/data terms and redistribution rules
- Confirm trademark usage policy

## Suggested Rollout Sequence

1. Finalize charter and boundary map.
2. Counsel review of license stack and contributor terms.
3. Add final `LICENSE`, `COMMERCIAL_LICENSE.md`, `MODEL_LICENSE.md`, `TRADEMARKS.md`.
4. Update README and docs index with final links.
5. Publish with release notes explicitly describing licensing model.

## Operational Notes

- Keep `docs/CHANGELOG.md` updated for policy-relevant changes.
- Keep `docs/GITHUB_RELEASE_CHECKLIST.md` as pre-publish gate.
- Keep boundary map current as new paid/open features are introduced.
