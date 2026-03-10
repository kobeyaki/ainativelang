# AI Native Lang (AINL) Runtime Release Readiness

This document summarizes the current production-hardening surface and where each capability is implemented and validated.
Timeline anchor: Foundational AI research and cross-platform experimentation by
the human founder began in **2024**. After partial loss of early artifacts, AINL
workstreams were rebuilt, retested, and formalized in overlapping phases through
**2025-2026**.

Release communication draft for tagging is maintained at `docs/RELEASE_NOTES_DRAFT.md`.
Immediate post-release engineering priorities are tracked in `docs/POST_RELEASE_ROADMAP.md`.
Maintainer release execution steps are documented in `docs/RELEASING.md`.

## Scope Completed

- Frozen runtime semantics and execution policies
- Property/fuzz safety tests
- Side-effect recording and replay
- Runtime guardrails for untrusted programs
- Real-world HTTP adapter with contract tests
- CLI golden fixture execution
- Conformance + compatibility coverage
- Deployable runner service (sync + async + metrics + health)

## Public Stability Boundaries

Release packaging expects these boundaries to stay explicit:

- Canonical runtime semantics: `runtime/engine.py`
- Compatibility runtime facade only: `runtime/compat.py`, `runtime.py`
- Compiler/strict semantic ownership: `compiler_v2.py`
- Example/corpus/fixture strictness classes: `tooling/artifact_profiles.json`
- Strict adapter contract allowlist ownership: `tooling/effect_analysis.py`
- Safe optimization policy (benchmark/compaction without syntax drift): `docs/SAFE_OPTIMIZATION_POLICY.md`

## Capability Map (Code + Tests)

### 1) Runtime Semantics + Policy

- **Code**
  - `SEMANTICS.md`
  - `runtime/engine.py`
  - `runtime/compat.py`
  - `runtime.py` (compatibility re-export only)
  - `compiler_v2.py` (`ir_version`, `runtime_policy`, warnings)
- **Tests**
  - `tests/test_runtime_basic.py`
  - `tests/test_runtime_graph_only.py`
  - `tests/test_runtime_graph_only_negative.py`
  - `tests/test_runtime_parity.py`
  - `tests/test_runtime_api_compat.py`
  - `tests/test_runtime_compiler_conformance.py`

### 2) Graph/Step Execution Controls

- **Code**
  - `runtime/engine.py`
    - execution modes: `graph-preferred`, `steps-only`, `graph-only`
    - unknown-op policy: `skip|error`
- **Tests**
  - `tests/test_runtime_graph_only.py::test_graph_mode_is_canonical_when_graph_exists_unless_force_steps`
  - `tests/test_runtime_api_compat.py::test_runtime_unknown_op_policy_error_steps_mode`

### 3) Runtime Guardrails

- **Code**
  - `runtime/engine.py` limits:
    - `max_steps`
    - `max_depth`
    - `max_adapter_calls`
    - `max_time_ms`
    - `max_frame_bytes`
    - `max_loop_iters`
- **Tests**
  - `tests/test_runtime_limits.py`

### 4) Real-world Adapters: HTTP + SQLite + FS + Tools

- **Code**
  - `runtime/adapters/http.py` (`SimpleHttpAdapter`)
  - `runtime/adapters/sqlite.py` (`SimpleSqliteAdapter`)
  - `runtime/adapters/fs.py` (`SandboxedFileSystemAdapter`)
  - `runtime/adapters/tools.py` (`ToolBridgeAdapter`)
  - `runtime/adapters/base.py` (`HttpAdapter`, `get_http()`)
  - `runtime/adapters/__init__.py`
- **Tests**
  - `tests/test_http_adapter_contracts.py`
  - `tests/test_sqlite_adapter_contracts.py`
  - `tests/test_fs_adapter_contracts.py`
  - `tests/test_tools_adapter_contracts.py`
    - input validation
    - allowlist behavior
    - timeout/error mapping
    - request/response shape

### 5) Side-effect Logging + Replay

- **Code**
  - `tests/helpers/recording_adapters.py`
    - `RecordingAdapter`
    - `RecordingAdapterRegistry`
    - `ReplayAdapterRegistry`
- **Tests**
  - `tests/test_replay_determinism.py`
  - `tests/property/test_runtime_equivalence.py::test_property_steps_vs_graph_side_effect_log_equivalence`

### 6) Property/Fuzz Safety

- **Code**
  - `tests/property/test_runtime_equivalence.py`
  - `tests/property/test_ir_fuzz_safety.py`
- **Tests**
  - same files (Hypothesis-backed)

### 7) API Ergonomics

- **Code**
  - `runtime/engine.py`
    - `RuntimeEngine.run(code, frame, ...)`
    - `trace_sink`
    - trace events include `lineno`
- **Tests**
  - `tests/test_runtime_api_compat.py::test_runtime_engine_run_wrapper`
  - `tests/test_runtime_api_compat.py::test_runtime_trace_sink_receives_events`

### 8) CLI + Golden Fixtures

- **Code**
  - `cli/main.py`
    - `run` mode/policy/limits flags
    - `golden` command
    - `--trace-out`
  - `examples/*.expected.json` (golden command executes only examples with matching expected files)
  - `tooling/artifact_profiles.json` (strict/non-strict/legacy classification for examples/corpus/fixtures)
- **Tests**
  - `tests/test_runtime_api_compat.py::test_cli_golden_examples_pass`
  - `tests/test_artifact_profiles.py`

### 9) Conformance + Runtime Test Entrypoint

- **Code**
  - `scripts/run_runtime_tests.py`
  - `tests/test_conformance.py`
  - `docs/CONFORMANCE.md`
  - `docs/RUNTIME_COMPILER_CONTRACT.md`
- **Tests**
  - `tests/test_conformance.py`
  - `tests/test_runtime_compiler_conformance.py`
  - `tests/test_grammar_constraint_alignment.py`

### 12) Reproducible Size Benchmark Surface

- **Code**
  - `scripts/benchmark_size.py` (manifest-driven benchmark over canonical public artifacts)
- **Artifacts**
  - `tooling/benchmark_size.json` (machine-readable output)
  - `BENCHMARK.md` (human-readable table)
- **Policy**
  - default metric is `approx_chunks` (approximate lexical-size proxy)
  - tokenizer-accurate counting is optional via `--metric tiktoken` when available

### 11) Strict Dataflow and Literal Ambiguity Contract

- **Code**
  - `compiler_v2.py` (`_analyze_step_rw`, strict dataflow diagnostics, quoted-literal handling hints)
  - `tooling/effect_analysis.py` (defined-before-use model used by strict validation)
- **Policy**
  - strict mode keeps defined-before-use enabled
  - bare identifier-like tokens in read positions are treated as variable references
  - string literals must be quoted in strict mode
- **Tests**
  - `tests/test_runtime_compiler_conformance.py` strict quoted-vs-bare matrix:
    - `Set.ref`, `Filt.value`, `CacheGet.key`, `CacheGet.fallback`, `CacheSet.value`, `QueuePut.value`

### 10) Runner Service (Deployable Product Surface)

- **Code**
  - `scripts/runtime_runner_service.py`
  - `services/runtime_runner/Dockerfile`
  - `services/runtime_runner/docker-compose.yml`
- **Behavior**
  - sync execution: `POST /run`
  - async execution: `POST /enqueue`, `GET /result/{id}`
  - health/readiness: `GET /health`, `GET /ready`
  - runtime metrics: `GET /metrics`
  - compile cache + structured logs + trace IDs
- **Tests**
  - `tests/test_runner_service.py`

## CI / Verification Command Set

Core confidence suite:

```bash
python scripts/run_test_profiles.py --profile core
```

Integration confidence suite:

```bash
python scripts/run_test_profiles.py --profile integration
```

Full confidence suite:

```bash
python scripts/run_test_profiles.py --profile full
```

Adapter manifest consistency:

```bash
pytest tests/test_adapter_manifest.py -v
```

Artifact profile consistency:

```bash
pytest tests/test_artifact_profiles.py -v
```

## Release Notes Checklist

- [x] Semantic contracts documented
- [x] Runtime/compiler contract documented and cross-linked
- [x] Safety limits implemented and tested
- [x] Adapter contracts covered
- [x] Replay determinism covered
- [x] CLI golden fixtures available
- [x] Conformance suite passing
