# Install (Cross-OS)

See also:

- `DOCS_INDEX.md` for full navigation
- `RUNTIME_COMPILER_CONTRACT.md` for runtime/compiler semantics and strict literal policy
- `CONFORMANCE.md` for current implementation status

## Requirements

- Python 3.9+
- pip

## Linux / macOS

```bash
bash scripts/bootstrap.sh
source .venv/bin/activate
ainl-validate examples/blog.lang --emit ir
```

## Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
.\.venv\Scripts\Activate.ps1
ainl-validate examples/blog.lang --emit ir
```

## Manual install

```bash
python -m pip install -e ".[dev,web]"
```

## Optional local guardrails (recommended)

Enable pre-commit hooks for fast local feedback before pushing:

```bash
pre-commit install
pre-commit run --all-files
```

This includes the AINL docs contract hook (`ainl-docs-contract`) so docs/runtime
contract drift is caught locally before CI.

## CLI tools installed

- `ainl-validate` - compile/validate/emit from `.lang`
- `ainl-validator-web` - run FastAPI validator UI
- `ainl-generate-dataset` - synthetic dataset generator
- `ainl-compat-report` - IR compatibility report
- `ainl-tool-api` - structured tool API CLI
- `ainl-ollama-eval` - local Ollama eval harness

## Runtime adapter CLI examples

Use `ainl run` with `--enable-adapter` flags to bootstrap reference adapters without writing Python glue code.

### HTTP adapter

```bash
ainl run app.ainl --json \
  --enable-adapter http \
  --http-allow-host api.example.com \
  --http-timeout-s 5
```

### SQLite adapter

```bash
ainl run app.ainl --json \
  --enable-adapter sqlite \
  --sqlite-db ./data/app.db \
  --sqlite-allow-write \
  --sqlite-allow-table users \
  --sqlite-allow-table orders
```

### Sandboxed FS adapter

```bash
ainl run app.ainl --json \
  --enable-adapter fs \
  --fs-root ./sandbox \
  --fs-max-read-bytes 2000000 \
  --fs-max-write-bytes 2000000 \
  --fs-allow-ext .txt \
  --fs-allow-ext .json
```

### Tools bridge adapter

```bash
ainl run app.ainl --json \
  --enable-adapter tools \
  --tools-allow echo \
  --tools-allow sum
```

### Deterministic record/replay

Record adapter calls:

```bash
ainl run app.ainl --json \
  --enable-adapter http \
  --record-adapters calls.json
```

Replay from recorded calls (no live side effects):

```bash
ainl run app.ainl --json \
  --replay-adapters calls.json
```
