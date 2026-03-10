# Releasing AINL (Maintainers)

Use this for the actual GitHub release execution flow.

## 1) Preflight

Run from repo root:

```bash
python scripts/run_test_profiles.py --profile core
python scripts/check_all_strict.py
python scripts/check_all_nonstrict.py
python -m pytest -q tests/test_artifact_profiles.py
python scripts/check_docs_contracts.py --scope all
```

Note: `--profile core` includes `tests/test_artifact_policy_manifest.py`, so artifact policy enforcement is part of the release preflight path.

If any command fails, resolve before tagging.

## 2) Finalize release text and version

- Use `docs/RELEASE_NOTES_DRAFT.md` as the GitHub Releases body.
- Confirm release-scoped docs are current:
  - `README.md`
  - `CONTRIBUTING.md`
  - `docs/RELEASE_READINESS.md`
  - `docs/POST_RELEASE_ROADMAP.md`
- Confirm intended tag/version is consistent in release notes draft.

## 3) Create and publish GitHub release

GitHub-native flow:

1. Open **Releases** in the repository.
2. Click **Draft a new release**.
3. Create/select the tag (for this release, recommended: `v1.1.0`).
4. Set title (recommended from release notes draft).
5. Paste body from `docs/RELEASE_NOTES_DRAFT.md`.
6. Mark as latest release (if appropriate).
7. Publish release.

## 4) Immediate post-release actions

- Open/track first-wave follow-up issues from `docs/issues/`.
- Use `docs/POST_RELEASE_ROADMAP.md` as the short-term priority guide.
- If needed, post a short public summary based on the release notes highlights.

## 5) Notes

- Do not reopen semantics during release execution unless a concrete blocker appears.
- Keep release claims conservative and aligned with current conformance/readiness docs.
