# AINL (AI Native Lang) Setup Summary

**Date:** 2026-03-18  
**Repo:** `/data/.openclaw/workspace/skills/ainativelang/`  
**Version:** 1.0.0 (ainl-lang package)

---

## What Was Installed and How

**Environment:** Python 3.14.3 (system Python is Homebrew-managed and blocks system-wide pip installs, so a venv was required)

```bash
python3 -m venv /tmp/ainl-venv
/tmp/ainl-venv/bin/pip install -e ".[dev,web]"
```

**NOTE:** The venv at `/tmp/ainl-venv` is ephemeral (in /tmp). To persist it:
```bash
python3 -m venv /data/.openclaw/workspace/skills/ainativelang/.venv
/data/.openclaw/workspace/skills/ainativelang/.venv/bin/pip install -e ".[dev,web]"
```
(There was a permission error when creating the venv inside the repo dir on first attempt — may have been a transient issue. Try again if needed.)

**Packages installed (key ones):**
- `ainl-lang 1.0.0` (editable install from repo)
- `fastapi`, `uvicorn`, `pydantic` — web server stack
- `pytest`, `hypothesis` — testing
- `pre-commit` — dev hooks
- `httpx`, `anyio`, `uvloop` — async HTTP

**Installed CLIs (available at `/tmp/ainl-venv/bin/`):**
- `ainl-validate` — compile/validate .lang or .ainl files, optionally emit artifacts
- `ainl-tool-api` — structured tool API for agent loops
- `ainl` — main CLI (run, golden, etc.)
- `ainl-runner-service`, `ainl-validator-web`, `ainl-generate-dataset`, and others

---

## Test Results

**Command:** `python scripts/run_test_profiles.py --profile core`

**Result:** 469 passed, 1 failed, 127 deselected (6.73s)

**The one failure:**
```
FAILED tests/test_artifact_policy_manifest.py::test_artifact_policy_paths_and_globs_resolve
AssertionError: glob has no matches: data/synthetic/*.lang
```
**Cause:** The test expects synthetic data files in `data/synthetic/` that haven't been generated yet. This is a known setup step (not a code bug).

**Fix (optional):** Generate synthetic data:
```bash
cd /data/.openclaw/workspace/skills/ainativelang
/tmp/ainl-venv/bin/python scripts/generate_synthetic_dataset.py --count 10000 --out data/synthetic
```
This will generate ~10k valid .lang programs and resolve the failing test.

**All other 469 tests pass,** including conformance, grammar, runtime, golden fixtures, corpus validation, and policy manifest checks.

---

## Available Adapters and What They Do

From `ADAPTER_REGISTRY.json`:

| Adapter | Description | Key Verbs |
|---------|-------------|-----------|
| `core` | Built-in arithmetic, string, date/time, control | `ADD`, `SUB`, `MUL`, `DIV`, `CONCAT`, `now`, `iso`, `parse`, `stringify`, `sleep`, etc. |
| `http` | HTTP client with allowlist + retry | `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS` |
| `sqlite` | SQLite database access | `query` (SELECT), `execute` (DML/DDL) |
| `fs` | Sandboxed file system | `read`, `write`, `list`, `delete` |
| `email` | OpenClaw email integration | `G` → returns list of unread emails `{id, from, subject, body, ts}` |
| `calendar` | OpenClaw calendar integration | `G` → returns upcoming events `{id, title, start, end, location}` |
| `social` | OpenClaw web search for mentions | `G` → returns mentions `{id, text, ts}` (uses `SOCIAL_MONITOR_QUERY` env var) |
| `db` | Leads database (CSV source) | `F` → returns leads from CSV (`LEADS_CSV` env var) |
| `svc` | Infrastructure health checks | `caddy`, `cloudflared`, `maddy`, `crm` → returns `"up"/"down"` |
| `cache` | Persistent key-value store (JSON file) | `get(namespace, key)`, `set(namespace, key, value)` |
| `queue` | Notification queue via OpenClaw | `Put(queue_name, payload)` |
| `wasm` | WebAssembly module execution | `CALL(module, function, args...)` |
| `extras` | Utility health checks | `file_exists`, `docker_image_exists`, `http_status`, `newest_backup_mtime`, `metrics` |
| `agent` | Local mailbox agent coordination | `send_task(envelope)`, `read_result(task_id)` |
| `tiktok` | TikTok reports from CRM DB | `F` (reports), `recent(hours_ago?)`, `videos()` |
| `memory` | Extension memory adapter (SQLite) | `put`, `get`, `append`, `list`, `delete`, `prune` |

**Core adapters** (http, sqlite, fs, tools) are safe-default and have contract tests.  
**OpenClaw adapters** (email, calendar, social, db, svc, queue) require OpenClaw integration.  
**Advanced adapters** (memory, agent, wasm) are operator-only/extension surfaces.

---

## How to Use AINL from Within OpenClaw Sessions

### Quick Start (CLI)

Always use the venv Python/binaries:

```bash
VENV=/tmp/ainl-venv
AINL_DIR=/data/.openclaw/workspace/skills/ainativelang

# Validate a program (strict mode)
$VENV/bin/ainl-validate $AINL_DIR/examples/hello.ainl --strict

# Run a program
cd $AINL_DIR && $VENV/bin/ainl run examples/hello.ainl --json

# Emit OpenAPI spec
echo 'S app api /api
E /health G ->L1
L1:
J {"status":"ok"}' | $VENV/bin/ainl-validate --emit openapi

# Validate and emit IR
$VENV/bin/ainl-validate $AINL_DIR/examples/if_call_workflow.ainl --strict --emit ir
```

**Important:** The `ainl` CLI requires the package to be on the Python path. Run from the repo dir or set `PYTHONPATH`:
```bash
cd /data/.openclaw/workspace/skills/ainativelang && $VENV/bin/ainl run examples/hello.ainl --json
# OR
PYTHONPATH=/data/.openclaw/workspace/skills/ainativelang $VENV/bin/ainl run my.ainl --json
```

### Tool API (for agent loops)

```bash
# Compile via stdin
echo '{"action": "compile", "code": "L1:\nR core.ADD 2 3 ->x\nJ x"}' | $VENV/bin/ainl-tool-api

# From a request file
$VENV/bin/ainl-tool-api --request-file my_request.json
```

### Validate an inline program

```bash
cat << 'EOF' | $VENV/bin/ainl-validate --strict
L1:
  R core.ADD 2 3 ->x
  J x
EOF
```

### Start the HTTP runner service

```bash
cd /data/.openclaw/workspace/skills/ainativelang
$VENV/bin/python scripts/runtime_runner_service.py
# Then: GET http://localhost:8770/capabilities
# POST http://localhost:8770/run with {"code": "...", "strict": true}
```

### Three Integration Paths

1. **CLI only** — `ainl-validate` / `ainl run` — fastest, no server needed
2. **HTTP runner** — `ainl-runner-service` at port 8770 — for orchestrator integration
3. **MCP server** — `ainl-mcp` (needs `pip install -e ".[mcp]"`) — for MCP-compatible agent hosts

---

## Issues Encountered and Resolutions

| Issue | Resolution |
|-------|-----------|
| System Python (Homebrew) blocks `pip install` system-wide | Used `python3 -m venv /tmp/ainl-venv` and installed into the venv |
| Venv in repo dir failed first time (permission error on `.csh` file) | Used `/tmp/ainl-venv` instead |
| `ainl run` gives `ModuleNotFoundError: No module named 'tooling'` when run outside repo dir | Must `cd` to repo dir first, or set `PYTHONPATH=/data/.openclaw/workspace/skills/ainativelang` |
| `ainl-validate --version` doesn't work | The CLI doesn't support `--version`; use `--help` to verify installation |
| 1 test failing: `test_artifact_policy_paths_and_globs_resolve` | Expects `data/synthetic/*.lang` which hasn't been generated. Run `python scripts/generate_synthetic_dataset.py --count 10000 --out data/synthetic` to fix |
| `examples/openclaw/daily_digest.lang` fails strict validation | That file is intentionally non-strict (uses experimental adapters); use `daily_digest.strict.lang` for strict validation, or validate without `--strict` |

---

## Example AINL Programs That Work

### 1. Hello World (`examples/hello.ainl`)
```ainl
L1:
  R core.ADD 2 3 ->x
  J x
```
**Run:** `cd ainativelang && /tmp/ainl-venv/bin/ainl run examples/hello.ainl --json`  
**Output:** `{"ok": true, "label": "1", "result": "x", "runtime_version": "1.0.0"}`

### 2. Conditional workflow (`examples/if_call_workflow.ainl`)
```ainl
L1:
  Call L8 ->has_payload
  If has_payload ->L2 ->L3
L8:
  Set v true
  J v
L2:
  Call L9 ->out
  J out
L3:
  Set out "missing_payload"
  J out
L9:
  R core.CONCAT "task_" "ready" ->res
  J res
```
Demonstrates Call/If/Set branching.

### 3. Simple API endpoint (inline)
```ainl
S app api /api
E /health G ->L1
L1:
J {"status":"ok"}
```
Compiles cleanly and emits OpenAPI with `--emit openapi`.

### 4. Arithmetic pipeline
```ainl
S app api /api
L1:
R core.ADD 2 3 ->sum
J sum
```
Compiles with full IR (nodes/edges) and strict validation passes.

### 5. OpenClaw daily digest (`examples/openclaw/daily_digest.lang`)
Multi-step workflow fetching email, calendar, social, leads — the production monitor pattern. Run with `ainl-validate` (without `--strict`) to inspect IR.

---

## openclaw/ Directory

The `openclaw/` directory contains **implementation documentation only** (Markdown files), not code. These are notes about how each monitor/workflow was implemented. No code needs to be "applied" from this directory — the actual AINL programs are in `examples/openclaw/` and `demo/`.

Key programs:
- `demo/monitor_system.lang` — production multi-service monitor (runs every 15 min)
- `examples/openclaw/daily_digest.lang` — daily digest (email + calendar + social + leads)
- `examples/openclaw/infrastructure_watchdog.lang` — infra health monitor
- `examples/openclaw/lead_enrichment.lang` — lead enrichment pipeline

---

## Persistence Note

The venv at `/tmp/ainl-venv` will be lost on system restart. To make it permanent:

```bash
python3 -m venv /data/.openclaw/workspace/skills/ainativelang/.venv
/data/.openclaw/workspace/skills/ainativelang/.venv/bin/pip install -e ".[dev,web]"
# Then use /data/.openclaw/workspace/skills/ainativelang/.venv/bin/ instead of /tmp/ainl-venv/bin/
```

Or add an alias/wrapper to workspace TOOLS.md for convenience.

## Permanent venv (added 2026-03-18)

Persistent venv created at: `/data/.openclaw/workspace/ainl-venv/`

To use AINL CLIs:
```bash
export PYTHONPATH=/data/.openclaw/workspace/skills/ainativelang
/data/.openclaw/workspace/ainl-venv/bin/ainl-validate [file]
/data/.openclaw/workspace/ainl-venv/bin/ainl-tool-api --action compile
/data/.openclaw/workspace/ainl-venv/bin/ainl run [file]
```
