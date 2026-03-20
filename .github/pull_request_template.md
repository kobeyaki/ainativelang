## What changed

-

## Why this change

-

## Validation performed

- [ ] Relevant tests passed
- [ ] Script/CLI path validated (if applicable)
- [ ] Docs updated for behavior changes
- [ ] Changelog updated (if release-visible)
- [ ] Docs contract check passed (`ainl-check-docs` or `python scripts/check_docs_contracts.py --scope all`)

Commands run:

```bash
# paste commands here
```

## Risk and rollback

- Risk level: low / medium / high
- Rollback approach:

## Checklist

- [ ] No sensitive data introduced
- [ ] Maintains or improves strict AI Native Lang (AINL) quality metrics (for model pipeline changes)
- [ ] Preserves machine-readable artifacts/diagnostics where required
- [ ] If examples/corpus/fixtures changed, `tooling/artifact_profiles.json` and `tests/test_artifact_profiles.py` were updated/validated
- [ ] If semantics-critical code changed (`compiler_v2.py`, `runtime/engine.py`, `runtime/compat.py`, `runtime.py`, `tooling/graph_normalize.py`, `tooling/effect_analysis.py`), contract docs were updated (`docs/RUNTIME_COMPILER_CONTRACT.md`, `docs/CONFORMANCE.md`, `docs/CHANGELOG.md`, `README.md`)
