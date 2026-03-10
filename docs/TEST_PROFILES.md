# Test Profiles

AINL now defines explicit test profiles so default CI/local runs stay stable while integration checks remain available.

## Profiles

- `core` (default): fast and stable suite (no emits/lsp integration tests).
- `emits`: parse/syntax checks over emitted Python artifacts in `tests/emits`.
- `lsp`: language server smoke script (`scripts/test_lsp.py`).
- `integration`: emits + lsp.
- `full`: core + integration.
- `docs`: docs contract consistency checks (cross-links, stale phrasing, required coupling).

## Commands

Using the script entrypoint:

```bash
.venv/bin/python scripts/run_test_profiles.py --profile core
.venv/bin/python scripts/run_test_profiles.py --profile emits
.venv/bin/python scripts/run_test_profiles.py --profile lsp
.venv/bin/python scripts/run_test_profiles.py --profile integration
.venv/bin/python scripts/run_test_profiles.py --profile full
.venv/bin/python scripts/run_test_profiles.py --profile docs
```

Equivalent Python invocation:

```bash
.venv/bin/python scripts/run_test_profiles.py --profile core
```

Direct docs guard command:

```bash
ainl-check-docs
# or
python scripts/check_docs_contracts.py --scope all
```

Optional pre-commit guard:

```bash
pre-commit install
pre-commit run --all-files
```

## CI policy

- **Pull requests / pushes** run the `core` profile on a cross-platform matrix.
- **Nightly and manual dispatch** run the `full` profile on Ubuntu.

This keeps day-to-day CI fast and stable while still exercising integration paths regularly.

## Pytest defaults

`pyproject.toml` now configures pytest to:

- collect from `tests/`
- skip recursion into `tests/emits` and `scripts` by default
- run with marker expression:

```text
not integration and not emits and not lsp
```

This prevents invalid module-name artifacts (e.g. `test_rag.api.py`) and script-style files from breaking default collection, while preserving explicit integration checks through profiles.

