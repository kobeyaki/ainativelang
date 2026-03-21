# AINL Canonical Core

This document defines the **public recommended lane** for AINL going forward.

It is intentionally narrower than the full accepted repository surface.

Purpose:
- give humans one clear answer to "what is canonical AINL?"
- give AI agents one clean syntax/semantic lane for generation and repair
- reduce drift between docs, examples, training, and strict validation
- preserve compatibility by distinguishing **recommended** from merely **accepted**

Machine-readable support metadata:
- `tooling/support_matrix.json`
- `tooling/artifact_profiles.json`

## What "Canonical" Means

Canonical in this document means:
- recommended for new examples
- recommended for new training assets
- recommended for public documentation
- the intended convergence lane for future strictness and tooling work

It does **not** mean the compiler rejects all other accepted forms today.

## Canonical Mental Model

AINL is best understood as:
- a compact textual surface
- compiling to canonical graph IR
- executed by a graph-first runtime
- emitted into practical targets

The graph is the semantic center.
The source text is the compact authoring and transport layer.

## Canonical Syntax

### Service Header

```text
S core web /api
```

or for scheduled workflows:

```text
S core cron
Cr L_tick "*/5 * * * *"
```

### Endpoint Binding

```text
E /users G ->L_users ->users
```

Canonical guidance:
- prefer explicit `->return_var` in public examples when it improves clarity

### Label Block

```text
L_users:
  R db.F User * ->users
  J users
```

### Adapter Call

Canonical form:

```text
R <adapter>.<VERB> <target> [args...] ->out
```

Examples:

```text
R core.ADD 2 3 ->x
R db.F User * ->users
R http.POST "https://example.com/hook" payload ->resp
```

Canonical guidance:
- prefer dotted adapter form
- prefer uppercase verbs in canonical examples
- prefer explicit `->out`

### Return

```text
J out
```

### Branch

```text
If flag ->L_then ->L_else
```

### Call

```text
Call L9 ->out
```

Canonical guidance:
- prefer explicit `Call ... ->out`
- do not rely on compatibility fallback behaviors when a direct binding is available

### Retry and Error Handling

```text
Retry @n1 2 0
Err @n1 ->L_fail
```

### Set

```text
Set out "ok"
```

Canonical guidance:
- in strict mode, quote string literals in read positions

## Canonical Op Set

This is the current public recommended core:

- `S`
- `D`
- `E`
- `L`
- `R`
- `J`
- `If`
- `Err`
- `Retry`
- `Call`
- `Set`
- `Cr`
- `Sc`

These are not the only ops the compiler/runtime may accept, but they are the
recommended public lane for current onboarding and canonical training.

## Compatible But Not Canonical

These forms may remain supported for continuity, but they are not the preferred path:

- split-token adapter forms such as `R cache get ...`
- compatibility-heavy inline multi-step label lines
- broader accepted execution ops such as:
  - `Filt`
  - `Sort`
  - `X`
  - `Loop`
  - `While`
  - `CacheGet`
  - `CacheSet`
  - `QueuePut`
  - `Tx`
  - `Enf`
- compatibility example families under:
  - `examples/openclaw/`
  - `examples/golden/`

These surfaces are important to preserve during migration, but they should not
define the public mental model of AINL.

## Canonical Example Set

Current canonical examples:

- `examples/hello.ainl`
- `examples/crud_api.ainl`
- `examples/rag_pipeline.ainl`
- `examples/retry_error_resilience.ainl`
- `examples/if_call_workflow.ainl`
- `examples/webhook_automation.ainl`
- `examples/monitor_escalation.ainl`
- `examples/web/basic_web_api.ainl`
- `examples/scraper/basic_scraper.ainl`

See:
- `docs/EXAMPLE_SUPPORT_MATRIX.md`
- `examples/README.md`

## Canonical Target Expectations

Best-supported current public targets:
- runtime-backed server
- OpenAPI
- runtime runner service

Implemented but less central to the canonical public lane:
- React
- Prisma
- SQL migrations
- Docker/Compose/K8s
- Next.js API routes
- Vue / Svelte
- cron / scraper / MT5

Treat target breadth as real, but uneven in maturity.

## Canonical Training Guidance

Canonical training assets should:
- use only canonical syntax
- use strict-valid examples
- prefer graph-normalized outputs where applicable
- avoid compatibility-only examples in the canonical lane

This is how AINL becomes easier for both humans and AI agents to learn and trust.

## Short Answer

If someone asks "What is canonical AINL today?", the answer should be:

> A small graph-first public core built around `S`, `D`, `E`, `L`, `R`, `J`,
> `If`, `Err`, `Retry`, `Call`, `Set`, `Cr`, and `Sc`, using dotted adapter
> calls, strict-valid examples, and graph-first runtime semantics.

## OpenClaw Bridge Layer (Non-Canonical)

**AINL canonical core** (this document’s lane) is the language surface, graph IR, graph-first runtime, and **portable** examples that do not assume OpenClaw’s workspace, CLI, or daily-memory layout.

**OpenClaw bridge** code lives under **`openclaw/bridge/`** and related **`docs/`**, **`examples/`**, and backward-compatible **`scripts/`** shims. It includes:

- Wrapper runner, cron drift checker, memory append CLI, and thin triggers (`run_wrapper_ainl.py`, `cron_drift_check.py`, `ainl_memory_append_cli.py`, `trigger_ainl_wrapper.py`, `sync_node_to_ainl_memory.py`).
- **Production monitoring stack (token budget, cache prune, weekly trends, consolidated notifications, duplicate guard)** implemented as bridge wrappers + `bridge_token_budget_adapter.py` — **not** part of canonical core syntax. Operator-facing documentation: **`docs/operations/UNIFIED_MONITORING_GUIDE.md`** (memory files default to **`~/.openclaw/workspace/memory/YYYY-MM-DD.md`**).
- Documentation for OpenClaw cron payloads, session keys, and parallel `daemon.sh` operation (`openclaw/bridge/README.md`, `docs/ainl_openclaw_unified_integration.md`, `docs/CRON_ORCHESTRATION.md`, `docs/openclaw/BRIDGE_TOKEN_BUDGET_ALERT.md`, `docs/operations/UNIFIED_MONITORING_GUIDE.md`).
- **Examples** that call OpenClaw-oriented adapters (e.g. `examples/openclaw_full_unification.ainl`) are **integration samples**, not canonical training material.

Treat **`openclaw/bridge/`** as the **official home** for cron/daemon/supervisor **unification glue** that ties AINL to OpenClaw. The compiler, core runtime, and `modules/common/` remain free of that glue; bridge scripts import them as libraries.
