# AI Native Lang (AINL) Architecture Overview

This document provides a publication-ready map of how AINL works end to end.

## Timeline Context

Timeline anchor: Foundational AI research and cross-platform experimentation by
the human founder began in **2024**. After partial loss of early artifacts, AINL
workstreams were rebuilt, retested, and formalized in overlapping phases through
**2025-2026**.

## System Layers

1. **Language Layer**
   - AINL source programs (`.lang` / canonical line-oriented forms)
   - formal grammar and semantics

2. **Compiler Layer**
   - parser + normalization + validation
   - canonical IR graph + legacy step-list emission
   - target emitters (server/web/tooling artifacts)

3. **Runtime Layer**
   - canonical graph-first execution engine (`RuntimeEngine`)
   - step fallback for compatibility and policy-controlled modes
   - compatibility wrapper (`ExecutionEngine`) as thin shim only
   - adapter-backed side-effect operations

4. **Training and Evaluation Layer**
   - corpus builders (gold/repair/check-rewrite/boost)
   - LoRA fine-tuning pipeline
   - constrained decoding + compile/repair evaluation gate

5. **Release and Operations Layer**
   - checkpoint sweep by task metrics
   - trend/regression gating
   - machine-readable run health artifact

## Core Components (Code Map)

- Compiler: `compiler_v2.py`
- Runtime: `runtime/engine.py`
- Runtime compatibility shim: `runtime/compat.py` + `runtime.py` re-export
- Formal prefix grammar: `compiler_grammar.py`
- Decoder priors: `grammar_priors.py`
- Decoder constraints compatibility adapter: `grammar_constraint.py`
- Runtime/compiler execution contract: `docs/RUNTIME_COMPILER_CONTRACT.md`
- Fine-tune script: `scripts/finetune_ainl.py`
- Eval gate: `scripts/eval_finetuned_model.py`
- Checkpoint sweep: `scripts/sweep_checkpoints.py`
- One-command orchestration: `scripts/run_alignment_cycle.sh`

## Data and Model Quality Flow

1. Build supervision datasets:
   - `scripts/build_regression_supervision.py`
   - `scripts/teacher_distill_dataset.py`
   - optional: `scripts/build_failure_boost_dataset.py`
2. Train adapter via LoRA.
3. Sweep checkpoints by strict AINL task metrics.
4. Evaluate selected checkpoint with constrained decoding and repair loop.
5. Analyze trends and apply quality/regression gates.
6. Emit run health summary for automation.

## Quality Signals (Primary)

- `strict_ainl_rate`
- `runtime_compile_rate`
- `nonempty_rate`

These are preferred over plain `eval_loss` for checkpoint selection in AINL generation.

## Diagnostics and Observability

The evaluation stack emits:

- generation/compile/repair timing breakdowns
- constraint diagnostics (fallback/eos/rejection counters)
- failure-family counts
- prompt-length bucket diagnostics
- quantization diagnostics (when enabled)

## Safety and Stability Principles

- Keep strict AINL correctness non-negotiable.
- Prefer additive feature flags over behavior-breaking changes.
- Keep machine-readable artifacts stable for automation and analysis.
- Preserve deterministic eval paths for apples-to-apples comparisons.

## Grammar and Runtime Ownership Contract

- Grammar law (slot transitions, semantic-prefix checks, lexical-prefix scanning, prefix transition application) is compiler-owned in `compiler_v2.py`.
- Formal prefix orchestration (state + admissibility masking) is in `compiler_grammar.py`.
- Non-authoritative token sampling priors are isolated in `grammar_priors.py`.
- Compatibility/composition surface for consumers lives in `grammar_constraint.py`.
- Runtime executes compiler-emitted step schema as documented in `docs/RUNTIME_COMPILER_CONTRACT.md` and validated by:
  - compiler-owned runtime helper contract in `compiler_v2.py` (`runtime_normalize_*`, `runtime_canonicalize_r_step`)
  - strict-mode quoted-literal policy in compiler dataflow (bare identifier-like tokens in read positions are treated as vars; literals must be quoted)
  - `tests/test_runtime_compiler_conformance.py`
  - `tests/test_grammar_constraint_alignment.py`
  - `tests/test_runtime_basic.py`
